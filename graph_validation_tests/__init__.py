"""
Abstract base class for the GraphValidation TestRunners
"""
from typing import Dict, List, Optional, Tuple

from argparse import ArgumentParser

from reasoner_validator.biolink import BiolinkValidator
from reasoner_validator.message import MESSAGES_BY_TARGET, MESSAGE_CATALOG, MESSAGES_BY_TEST
from translator_testing_model.datamodel.pydanticmodel import TestAsset, TestCaseResultEnum

from graph_validation_tests.translator.registry import (
    get_the_registry_data,
    extract_component_test_metadata_from_registry
)
from graph_validation_tests.translator.trapi import get_available_components
from graph_validation_tests.utils.asyncio import gather

import logging
logger = logging.getLogger(__name__)


class TestCaseRun(BiolinkValidator):
    """
    TestCaseRun is a wrapper for BiolinkValidator, used to aggregate
    validation messages from the GraphValidationTest processing of a specific
    TestCase, derived from the TestAsset - bound to the 'test_run' - which is
    based on a TRAPI query against the test_run bound 'target' endpoint. Results
    of a TestCaseRun are stored within the parent BiolinkValidator class.
    """
    def __init__(self, test_run, test, **kwargs):
        """
        Constructor for a TestCaseRun.

        :param test_run: owner of the use case, which should be an instance of a subclass of GraphValidationTest.
        :param test: declared generator of a TestCase TRAPI query being processed (generally, an executable function).
        :param kwargs: Dict, optional extra named BiolinkValidator parameters
                             which may be specified for the test run.
        """
        assert test_run, "'test_run' is uninitialized!"
        self.test_run = test_run

        BiolinkValidator.__init__(
            self,
            default_test=test.__name__,
            default_target=test_run.default_target,
            trapi_version=test_run.trapi_version,
            biolink_version=test_run.biolink_version,
            **kwargs
        )

        # the 'test' itself should be an executable piece of code
        # that defines how a TestCase is derived from the TestAsset
        self.test = test

        self.trapi_request: Optional[Dict] = None
        self.trapi_response: Optional[Dict[str, int]] = None

    def get_test_asset(self) -> TestAsset:
        return self.test_run.test_asset

    def get_component(self) -> str:
        return self.test_run.default_target

    def get_environment(self) -> str:
        return self.test_run.environment

    async def run_test_case(self):
        raise NotImplementedError("Implement me within a suitable test-type specific subclass of TestCaseRun!")

    @staticmethod
    def get_predicate_id(predicate_name: str) -> str:
        """
        SME's (like Jenn) like plain English (possibly capitalized) names
        for their predicates, whereas, we need regular Biolink CURIES here.
        :param predicate_name: predicate name string
        :return: str, predicate CURIE (presumed to be from the Biolink Model?)
        """
        # TODO: maybe validate the predicate name here against the Biolink Model?
        predicate = predicate_name.lower().replace(" ", "_")
        return f"biolink:{predicate}"

    def translate_test_asset(self) -> Dict[str, str]:
        """
        Need to access the TestAsset fields as a dictionary with some
        edge attributes relabelled to reasoner-validator expectations.
        :return: Dict[str,str], reasoner-validator indexed test edge data.
        """
        test_edge: Dict[str, str] = dict()

        # TODO: should "idx" be renamed to "test_asset_id" or will this break the reasoner-validator?
        test_edge["idx"] = self.get_test_asset().id
        test_edge["subject_id"] = self.get_test_asset().input_id
        test_edge["subject_category"] = self.get_test_asset().input_category
        test_edge["predicate_id"] = self.get_test_asset().predicate_id \
            if self.get_test_asset().predicate_id else self.get_predicate_id(self.get_test_asset().predicate_name)
        test_edge["object_id"] = self.get_test_asset().output_id
        test_edge["object_category"] = self.get_test_asset().output_category
        test_edge["biolink_version"] = self.biolink_version

        return test_edge

    def skip(self, code: str, edge_id: str, messages: Optional[Dict] = None):
        """
        Edge test Pytest skipping wrapper.
        :param code: str, validation message code (indexed in the codes.yaml of the Reasoner Validator)
        :param edge_id: str, S-P-O identifier of the edge being skipped
        :param messages: (optional) additional validation messages available
                         to explain why the test is being skipped.
        :return:
        """
        self.report(code=code, edge_id=edge_id)
        if messages:
            self.add_messages(messages)
        report_string: str = self.dump_skipped(flat=True)
        self.report("skipped.test", identifier=report_string)

    def assert_test_outcome(self):
        """
        Test outcomes
        """
        if self.has_critical():
            critical_msg = self.dump_critical(flat=True)
            logger.critical(critical_msg)

        elif self.has_errors():
            # we now treat 'soft' errors similar to critical errors (above) but
            # the validation messages will be differentiated on the user interface
            err_msg = self.dump_errors(flat=True)
            logger.error(err_msg)

        elif self.has_warnings():
            wrn_msg = self.dump_warnings(flat=True)
            logger.warning(wrn_msg)

        elif self.has_information():
            info_msg = self.dump_info(flat=True)
            logger.info(info_msg)

        else:
            pass  # do nothing... just silent pass through...


class GraphValidationTest(BiolinkValidator):
    """
    GraphValidationTest is a wrapper used to build instances
    of TestCase derived from a given TestAsset processed
    against a given 'target' component endpoint in compliance
    with explicit or default TRAPI and Biolink Model versions.
    This wrapper is derived from BiolinkValidator for convenience.
    Most of the actual test result messages are captured within
    the separately defined "TestCaseRun" wrapper class.
    """
    # Simple singleton class sequencer, for
    # generating unique test identifiers
    _id: int = 0

    def __init__(
            self,
            test_asset: TestAsset,
            component: Optional[str] = None,
            environment: Optional[str] = None,
            trapi_generators: Optional[List] = None,
            trapi_version: Optional[str] = None,
            biolink_version: Optional[str] = None,
            runner_settings: Optional[List[str]] = None,
            **kwargs
    ):
        """
        GraphValidationTest constructor.

        :param test_asset: TestAsset, target test asset(s) being processed
        :param component: Optional[str] = None, target component to be tested,
                          from ComponentEnum (default: 'ars' assumed)
        :param environment: Optional[str] = None, Translator execution environment for the test,
                            from TestEnvEnum, one of 'dev', 'ci', 'test' or 'prod' (default: 'ci' assumed)
        :param trapi_generators: Optional[List] = None, pointers to code functions that configure
                                 TRAPI query requests. e.g. see graph_validation_tests.unit_test_templates.
                                 May be empty for some types of tests with fixed TRAPI queries internally?
        :param trapi_version: Optional[str] = None, target TRAPI version (default: current release)
        :param biolink_version: Optional[str], target Biolink Model version (default: current release)
        :param runner_settings: Optional[List[str]], extra string directives to the Test Runner (default: None)
        :param kwargs: named arguments to pass on to BiolinkValidator parent class (if and as applicable)
        """
        if not component:
            component = 'ars'
        if not environment:
            environment = 'ci'

        BiolinkValidator.__init__(
            self,
            default_target=component,
            trapi_version=trapi_version,
            biolink_version=biolink_version,
            **kwargs
        )
        self.environment: str = environment
        self.test_asset: TestAsset = test_asset

        # trapi_generators should usually not be empty, but just in case...
        self.trapi_generators: Tuple = trapi_generators or ()

        self.runner_settings = runner_settings

        self.results: Dict = dict()

    def get_run_id(self):
        # First implementation of 'run identifier' is
        # is to return the default target endpoint?
        # TODO: likely need a more appropriate run identifier here, e.g. ARS PK-like?
        return self.default_target

    def get_trapi_generators(self) -> Tuple:
        return self.trapi_generators

    def get_runner_settings(self) -> List[str]:
        return self.runner_settings.copy()

    @classmethod
    def build_test_asset(
            cls,
            test_asset_id: str,
            subject_id: str,
            subject_category: str,
            predicate_id: str,
            object_id: str,
            object_category: str
    ) -> TestAsset:
        """
        Construct a Python TestAsset object.

        :param test_asset_id: str, CURIE identifying the identifier of the subject concept
        :param subject_id: str, CURIE identifying the identifier of the subject concept
        :param subject_category: str, CURIE identifying the category of the subject concept
        :param predicate_id: str, name of Biolink Model predicate defining the statement predicate_id being tested.
        :param object_id: str, CURIE identifying the identifier of the object concept
        :param object_category: str, CURIE identifying the category of the subject concept
        :return: TestAsset object
        """
        # TODO: is the TestAsset absolutely necessary internally inside this test runner,
        #       which directly uses Biolink fields, not the TestAsset fields?
        return TestAsset.construct(
            id=test_asset_id,
            input_id=subject_id,
            input_category=subject_category,
            predicate_id=predicate_id,
            predicate_name=predicate_id.replace("biolink:", ""),
            output_id=object_id,
            output_category=object_category
        )

    def test_case_wrapper(self, test, **kwargs) -> TestCaseRun:
        """
        Converts currently bound TestAsset into a runnable
        test case.  Implementation is subclassed, to give
        access to a specialized TestCaseRun class wrapped code.

        :param test: pointer to a code function that configure an
                     individual TRAPI query request.
                     See graph_validation_tests.unit_test_templates.
        """
        raise NotImplementedError("Abstract method, implement in subclass!")

    @staticmethod
    async def run_test_cases(test_cases: List[TestCaseRun]):
        # TODO: unsure if one needs to limit concurrent requests here...
        await gather([test_case.run_test_case() for test_case in test_cases])  # , limit=num_concurrent_requests)

    FAILURE_MODES = ("error", "critical")

    def compute_status(self, tcr: TestCaseRun) -> Tuple[str, TestCaseResultEnum, Dict]:
        """
        Method to construct components for a test case result based on the failure mode
        assessment of non-empty validation messages (which are also returned).

        :param tcr: TestCaseRun containing reasoner-validator style validation message from test execution.
        :return: Tuple[str, TestCaseResultEnum, Dict], where position 0 is the target,
                 position 1 is the testcase TestCaseResultEnum status (PASSED|FAILED|SKIPPED) and
                 position 2 is a (possible empty) dictionary of non-empty validation messages
        """
        target: str = tcr.default_target
        test: str = tcr.default_test
        messages_by_target: MESSAGES_BY_TARGET = tcr.get_all_messages()
        if target in messages_by_target:
            messages_by_test: MESSAGES_BY_TEST = messages_by_target[target]
            if test in messages_by_test:
                message_catalog: MESSAGE_CATALOG = messages_by_test[test]
                mtype: str
                messages: Dict
                non_empty_messages: MESSAGE_CATALOG = {
                    mtype: messages for mtype, messages in message_catalog.items() if message_catalog[mtype]
                }
                # TODO: this first iteration in which FAILURE_MODES are
                #       immutable (not sensitive to TestRunner parameters)
                if not non_empty_messages or not any([mtype in non_empty_messages for mtype in self.FAILURE_MODES]):
                    return target, TestCaseResultEnum.PASSED, non_empty_messages
                else:
                    return target, TestCaseResultEnum.FAILED, non_empty_messages
        # TODO: seems sensible to assumed that if the target or test are
        #       missing in test results, then the test was skipped?
        return target, TestCaseResultEnum.SKIPPED, {}

    def format_results(self, test_cases: List[TestCaseRun]) -> Dict:
        """
        This function normalizes and restructures TestCaseRun
        results for the upstream consumer of TestRunner results.

        :param test_cases: List[TestCaseRun], list of Test Case runs with results.
        :return: Dict, structured test PASSED/FAILED/SKIPPED status and message
                       results for all TestCases, indexed by a "test_case_id"
                       of format "<test_asset_id>-<test_name>" "test_name" as
                       specified by TRAPI generators of a given test run.
        """
        # Originally, the results == [tc.get_all_messages() for tc in test_cases], which gives
        # [
        #    {   # components are "ars", ARA or KP infores object references
        #        '<component_id>': {
        #            'by_subject': {
        #                'info': {},
        #                'skipped': {},
        #                'warning': {},
        #                'error': {},
        #                'critical': {}
        #            }
        #        }
        #    },
        #    {
        #        '<component_id>': {
        #            'inverse_by_new_subject': {
        #                'info': {},
        #                'skipped': {},
        #                'warning': {},
        #                'error': {
        #                    'error.trapi.response.knowledge_graph.missing_expected_edge': {
        #                        'global': {
        #                            'TestAsset:00001|(PUBCHEM.COMPOUND:4091#biolink:SmallMolecule)-\
        #                            [biolink:affects]->\
        #                            (NCBIGene:2475#biolink:Gene)': None
        #                        }
        #                    }
        #                },
        #                'critical': {}
        #            }
        #        }
        #    },
        #    etc...
        # ]
        #
        # with the source test_asset as recorded within the test_case.test_run.test_asset property. Note that all the
        # test case message blocks have the same testing target component (although that doesn't have to be the case).
        #
        # We probably need to return something more like the following (using the source test asset information...):
        #
        # results == {
        #     "<test_case_id_1>": {
        #         "<component_1>": {
        #            "status: <PASSED|FAILED|SKIPPED>, # for result 1
        #            "messages": <reasoner-validator formatted message partition>
        #         }
        #         "<component_2>": {
        #            "status: <PASSED|FAILED|SKIPPED>, # for 'test_case_id_1' from 'component_2'
        #            "messages": <reasoner-validator formatted message partition>
        #         }
        #         etc...
        #     }
        #     "<test case id 2>": {
        #         "<component_1>": <result 2>,
        #         etc...
        #     }
        #     etc...
        # ]
        # where the 'test_asset_id_#' is something sensible, probably composite of the test asset identifier and
        # the identifier of the test template method used to generate the TestCase-specific TRAPI query.
        #
        # The <result_#> value could minimally simply be be "PASSED" or "FAILED"; however, perhaps it ought to be
        # a somewhat more complex informative data value for this TestRunner, accounting for the extensive validation
        # messages categories provided by reasoner-validator, i.e. 'info', 'skipped', 'warning', 'error', 'critical'.
        #
        # How should these messages be binned into test PASSED or FAILED? Should “PASSED” only be tolerant of
        # “information” messages? Are “skipped test” messages indicative of a failed test?
        #
        # Are “Warnings” to also be taken as an indication of a test failure? Could/should we give TestRunner
        # “stringency” indications which affect whether “skipped” and “warnings” are returned as “PASSED”?
        #
        # The above <result_#> could be a dictionary of format:
        #
        # {
        #     "status": "<PASSED|FAILED|SKIPPED>",
        #     "messages": "<pruned message catalog>"
        # }
        #
        # where the message catalog is a Python dictionary pruned of all empty reasoner-validator message partitions,
        # where the status of the test is determined by the aforementioned stringency rules, however coded.
        #
        results: Dict = dict()
        for tcr in test_cases:
            # TODO: not sure how robust this is: will the 'id' always be defined?
            test_asset_id: str = tcr.test_run.test_asset.id
            test_name: str = tcr.default_test
            test_case_id: str = f"{test_asset_id}-{test_name}"
            if test_case_id not in results:
                results[test_case_id] = dict()
            component: str
            status: TestCaseResultEnum
            messages: MESSAGE_CATALOG
            component, status, messages = self.compute_status(tcr)
            # TODO: sanity check? we blissfully assume that a 'component'
            #       is only reported once for a given 'test_case_id'
            assert component not in results[test_case_id]
            results[test_case_id][component] = {
                "status": status,
                "messages": messages
            }

        return results

    async def process_test_run(self, **kwargs) -> Dict:
        """
        Applies a TestCase generator giving a specific subclass
        of TestCaseRun, wrapping queries defined by test-specific
        TRAPI query generators, then runs the derived TestCase
        instances as co-routines, returning a list of their results.

        :param kwargs: Dict, optional named parameters passed to the TestRunner.

        :return: Dict, of structured test message results for all TestCases,
                       specified by TRAPI generators of a given test run.
        """
        test_cases: List[TestCaseRun] = [
            self.test_case_wrapper(
                test,
                **kwargs
            )
            for test in self.get_trapi_generators()
        ]

        await self.run_test_cases(test_cases)

        # ... then, return the results
        return self.format_results(test_cases)

    @classmethod
    async def run_tests(
            cls,
            test_asset_id: str,
            subject_id: str,
            subject_category: str,
            predicate_id: str,
            object_id: str,
            object_category: str,
            trapi_generators: List,
            environment: Optional[str] = "ci",
            components: Optional[List[str]] = None,
            trapi_version: Optional[str] = None,
            biolink_version: Optional[str] = None,
            runner_settings: Optional[List[str]] = None,
            **kwargs
    ) -> Dict[str, Dict]:
        """
        Run one or more Graph Validation tests, of specified category of test,
        against all specified components running in a given environment,
        and with test cases derived from a specified test asset.

        Parameters provided to specify the test are:

        :param cls: The target TestRunner subclass of GraphValidationTest of the test type to be run.

        - TestAsset to be used for test queries.
        :param test_asset_id: str, the identifier of the test asset driving test cases in this run of tests
        :param subject_id: str, CURIE identifying the identifier of the subject concept
        :param subject_category: str, CURIE identifying the category of the subject concept
        :param predicate_id: str, name of Biolink Model predicate defining the statement predicate_id being tested.
        :param object_id: str, CURIE identifying the identifier of the object concept
        :param object_category: str, CURIE identifying the category of the object concept

        - TRAPI JSON query generators for the TestCases using the specified TestAsset
        :param trapi_generators: List, pointers to code functions that
                                 configure an individual TRAPI query request.
                                 See graph_validation_tests.unit_test_templates.

        - Target endpoint(s) to be tested - one test report or report set generated per endpoint provided.
        :param components: Optional[List[str]] = None, comma-delimited list of components to be tested
                           (Values specified in ComponentEnum in TranslatorTestingModel; default ['ars'])
        :param environment: Optional[str] = None, Target Translator execution environment for the test,
                            one of 'dev', 'ci', 'test' or 'prod' (default: 'ci')

        - Metadata globally configuring the test(s) to be run.
        :param trapi_version: Optional[str] = None, target TRAPI version (default: latest public release)
        :param biolink_version: Optional[str] = None, target Biolink Model version (default: Biolink toolkit release)
        :param runner_settings: Optional[List[str]] = None, extra string parameters to the Test Runner
        :param kwargs: Dict, optional extra named parameters to passed to TestCase TestRunner.
        :return: Dict { "pks": Dict[<target>, <pk>], "results": Dict[<test_case_id>, <test_case_results>] }
        """
        if not components:
            components = ['ars']

        # TODO: (April 2024) short term limitation: can't test ARS endpoints, see the missing ARS code in
        #       the run_trapi_query() method of the graph_validation_tests.translator.trapi package module.
        if 'ars' in components:
            logger.error("Default ARS testing is not yet supported by GraphValidationTests")
            return dict()

        # Load the internal TestAsset being uniformly served
        # to all TestCase runs against specified components.
        test_asset: TestAsset = GraphValidationTest.build_test_asset(
            test_asset_id,
            subject_id,
            subject_category,
            predicate_id,
            object_id,
            object_category
        )

        # A test run - running and reporting independently - is configured
        # to apply a test derived from the specified TestAsset against each
        # specified component, within the specified environment. Each test run
        # generates a distinct test report, which is composed of the result(s)
        # of one or more independent TestCases derived from the TestAsset,
        # reflecting on the objective and design of the TestRunner.
        test_runs: List[cls] = [
            cls(
                test_asset=test_asset,
                component=target,
                environment=environment,
                trapi_generators=trapi_generators,
                trapi_version=trapi_version,
                biolink_version=biolink_version,
                runner_settings=runner_settings
            ) for target in components
        ]
        #
        # TODO: the following comment is plagiarized from 3rd party TestRunner comments simply as
        #       a short term source of inspiration for the design of results from this TestRunner
        # The ARS_test_Runner with the following command:
        #
        #       ARS_Test_Runner
        #           --env 'ci'
        #           --query_type 'treats_creative'
        #           --expected_output '["TopAnswer","TopAnswer"]'
        #           --input_curie 'MONDO:0005301'
        #           --output_curie  '["PUBCHEM.COMPOUND:107970","UNII:3JB47N2Q2P"]'
        #
        # gives a Python dictionary report (serialized to JSON) similar as follows:
        #
        # {
        #     "pks": {
        #         "parent_pk": "e29c5051-d8d7-4e82-a1a1-b3cc9b8c9657",
        #         "merged_pk": "56e3d5ac-66b4-4560-9f56-7a4d117e8003",
        #         "aragorn": "14953570-7451-4d1b-a817-fc9e7879b477",
        #         "arax": "8c88ead6-6cbf-4c9a-9570-ca76392ddb7a",
        #         "unsecret": "bd084e27-2a0e-4df4-843c-417bfac6f8c7",
        #         "bte": "d28a4146-9486-4e98-973d-8cdd33270595",
        #         "improving": "d8d3c905-ec07-491f-a078-7ef0f489a409"
        #     },
        #     "results": [
        #         {
        #             "PUBCHEM.COMPOUND:107970": {
        #                 "aragorn": "Fail",
        #                 "arax": "Pass",
        #                 "unsecret": "Fail",
        #                 "bte": "Pass",
        #                 "improving": "Pass",
        #                 "ars": "Pass"
        #             }
        #         },
        #         {
        #             "UNII:3JB47N2Q2P": {
        #                 "aragorn": "Fail",
        #                 "arax": "Pass",
        #                 "unsecret": "Fail",
        #                 "bte": "Pass",
        #                 "improving": "Pass",
        #                 "ars": "Pass"
        #             }
        #         }
        #     ]
        # }
        results = {
            "pks": dict(),
            "results": dict()
        }
        for tr in test_runs:
            target: str = tr.default_target
            test_run_id: str = tr.get_run_id()
            results["pks"].update({target: test_run_id})
            results["results"].update(await tr.process_test_run(**kwargs))

        return results


def get_parameters(tool_name: str):
    """Parse CLI args."""

    # Sample command line interface parameters:
    #     --components 'molepro,arax'
    #     --environment 'dev'
    #     --subject_id 'DRUGBANK:DB01592'
    #     --subject_category 'biolink:SmallMolecule',
    #     --predicate_id 'biolink:ameliorates_condition',
    #     --object_id 'MONDO:0011426',
    #     --object_category 'biolink:Disease'
    #     --trapi_version '1.5.0'
    #     --biolink_version '4.1.6'
    #     --runner_settings 'inferred'

    parser = ArgumentParser(description=tool_name)

    parser.add_argument(
        "--components",
        type=str,
        choices=get_available_components(),
        required=True,  # TODO: later, if and when implemented, the default could become 'ars' if unspecified...
        help="Names Translator components to be tested, taken from the Translator Testing Model 'ComponentEnum'; " +
             "which may be a comma separated string of such names (e.g. 'arax,molepro')"
        # "(Default: if unspecified, the test is run against the 'ars')",
        # default=None
    )

    parser.add_argument(
        "--environment",
        type=str,
        choices=['dev', 'ci', 'test', 'prod'],
        default=None,
        help="Translator execution environment of the Translator Component targeted for testing. " +
             "(Default: if unspecified, run the test within the 'ci' environment)",
    )

    parser.add_argument(
        "--test_asset_id",
        type=str,
        required=True,
        help="Identifier of TestAsset associated with specified test run parameters",
    )

    parser.add_argument(
        "--subject_id",
        type=str,
        required=True,
        help="Statement subject concept CURIE",
    )

    parser.add_argument(
        "--subject_category",
        type=str,
        required=True,
        help="Statement subject concept Biolink category (CURIE)",
    )

    parser.add_argument(
        "--predicate_id",
        type=str,
        required=True,
        help="Statement Biolink Predicate identifier",
    )

    parser.add_argument(
        "--object_id",
        type=str,
        required=True,
        help="Statement object concept CURIE",
    )

    parser.add_argument(
        "--object_category",
        type=str,
        required=True,
        help="Statement object concept Biolink category (CURIE)",
    )

    parser.add_argument(
        "--trapi_version",
        type=str,
        help="TRAPI version expected for knowledge graph access (Default: use latest TRAPI community release)",
        default=None
    )

    parser.add_argument(
        "--biolink_version",
        type=str,
        help="Biolink Model version expected for knowledge graph access " +
             "(Default: use current default release of the Biolink Model Toolkit)",
        default=None
    )

    parser.add_argument(
        "--runner_settings",
        nargs='+',
        help="Scalar settings for the TestRunner, e.g. 'inferred'",
        default=None
    )

    args = parser.parse_args()

    # convert any comma-delimited string of components
    # ComponentEnum enumerated identifiers
    # into the expected List of entries
    if "components" in args:
        args["components"] = [entry for entry in args["components"].split(",")]

    return args
