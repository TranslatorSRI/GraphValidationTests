"""
Abstract base class for the GraphValidation TestRunners
"""
import asyncio
from typing import Dict, List, Optional
from functools import lru_cache
from argparse import ArgumentParser

from bmt import utils
from reasoner_validator.biolink import BiolinkValidator
from translator_testing_model.datamodel.pydanticmodel import TestAsset, TestEnvEnum

from graph_validation_test.translator.registry import (
    get_the_registry_data,
    extract_component_test_metadata_from_registry
)

import logging
logger = logging.getLogger(__name__)

env_spec = {
    'dev': 'ars-dev',
    'ci': 'ars.ci',
    'test': 'ars.test',
    'prod': 'ars-prod'
}


class UnitTestReport(BiolinkValidator):
    """
    UnitTestReport is a wrapper for BiolinkValidator, used to aggregate
    validation messages from test processing of a given TestAsset.
    """
    def __init__(
            self,
            target: str,
            test_asset: TestAsset,
            trapi_version: Optional[str] = None,
            biolink_version: Optional[str] = None,
            test_logger: Optional[logging.Logger] = None
    ):
        """
        :param target: target: str, target endpoint running in a specified environment of component to be tested
        :param test_asset: The test asset being processed in (Biolink Model compliant TRAPI) testing queries.
        :param trapi_version: The TRAPI version whose compliance must be met
                              by the component responding to the test.
        :param biolink_version: The Biolink Model release version whose compliance
                                must be met by the component responding to the test.
        :param test_logger: The Python logger used to report internal log messages from the test run.
        """
        BiolinkValidator.__init__(
            self,
            default_target=target,
            trapi_version=trapi_version,
            biolink_version=biolink_version
        )
        self.test_asset = test_asset
        self.logger = test_logger
        self.trapi_request: Optional[Dict] = None
        self.trapi_response: Optional[Dict[str, int]] = None

    def skip(self, code: str, edge_id: str, messages: Optional[Dict] = None):
        """
        Edge test Pytest skipping wrapper.
        :param code: str, validation message code (indexed in the codes.yaml of the Reasoner Validator)
        :param edge_id: str, S-P-O identifier of the edge being skipped
        :param messages: (optional) additional validation messages available to explain why the test is being skipped
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
            if self.logger:
                self.logger.critical(critical_msg)

        elif self.has_errors():
            # we now treat 'soft' errors similar to critical errors (above) but
            # the validation messages will be differentiated on the user interface
            err_msg = self.dump_errors(flat=True)
            if self.logger:
                self.logger.error(err_msg)

        elif self.has_warnings():
            wrn_msg = self.dump_warnings(flat=True)
            if self.logger:
                self.logger.warning(wrn_msg)

        elif self.has_information():
            info_msg = self.dump_info(flat=True)
            if self.logger:
                self.logger.info(info_msg)

        else:
            pass  # do nothing... just silent pass through...


class GraphValidationTest(UnitTestReport):

    # Simple singleton class sequencer, for
    # generating unique test identifiers
    _id: int = 0

    def __init__(
            self,
            target: str,
            test_asset: TestAsset,
            trapi_version: Optional[str] = None,
            biolink_version: Optional[str] = None,
            runner_settings: Optional[List[str]] = None,
            test_logger: Optional[logging.Logger] = None
    ):
        """
        GraphValidationTest constructor.

        :param target: str, target endpoint running in a specified environment of component to be tested
        :param test_asset: TestAsset, target test asset(s) being processed
        :param trapi_version: Optional[str], target TRAPI version (default: current release)
        :param biolink_version: Optional[str], target Biolink Model version (default: current release)
        :param runner_settings: Optional[List[str]], extra string directives to the Test Runner (default: None)
        :param test_logger: Optional[logging.Logger], Python logger, for diagnostics
        """
        self.target: str = target

        UnitTestReport.__init__(
            self,
            target=target,
            test_asset=test_asset,
            trapi_version=trapi_version,
            biolink_version=biolink_version,
            test_logger=test_logger
        )
        self.runner_settings = runner_settings
        self.results: Dict = dict()

    def get_runner_settings(self) -> List[str]:
        return self.runner_settings.copy()

    @classmethod
    def generate_test_asset_id(cls) -> str:
        cls._id += 1
        return f"TestAsset:{cls._id:0>5}"

    def generate_predicate_id(self, relationship: str) -> Optional[str]:
        if self.bmt.is_predicate(relationship):
            predicate = self.bmt.get_element(relationship)
            if predicate:
                return utils.format_element(predicate)
        return None

    @classmethod
    def build_test_asset(
            cls,
            subject_id: str,
            subject_category: str,
            predicate_id: str,
            object_id: str,
            object_category: str
    ) -> TestAsset:
        """
        Construct a Python TestAsset object.

        :param subject_id: str, CURIE identifying the identifier of the subject concept
        :param subject_category: str, CURIE identifying the category of the subject concept
        :param predicate_id: str, name of Biolink Model predicate defining the statement predicate_id being tested.
        :param object_id: str, CURIE identifying the identifier of the object concept
        :param object_category: str, CURIE identifying the category of the subject concept
        :return: TestAsset object
        """
        return TestAsset.construct(
            id=cls.generate_test_asset_id(),
            input_id=subject_id,
            input_category=subject_category,
            predicate_id=predicate_id,
            predicate_name=predicate_id.replace("biolink:", ""),
            output_id=object_id,
            output_category=object_category
        )

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

    async def run(self):
        """
        Abstract definition of the wrapper method used to invoke a
        co-routine run to process a given subclass of test, on the
        currently bound TestAsset, in a given test environment.

        :return: None - use get_results() below, or its
        subclass implementation, to access the test results.
        """
        raise NotImplementedError("Implement me in a subclass!")

    @classmethod
    async def run_test(
            cls,  # Python class assumed to be a subclass of GraphValidationTest
            subject_id: str,
            subject_category: str,
            predicate_id: str,
            object_id: str,
            object_category: str,
            environment: Optional[TestEnvEnum] = TestEnvEnum.ci,
            components: Optional[str] = None,
            trapi_version: Optional[str] = None,
            biolink_version: Optional[str] = None,
            runner_settings: Optional[List[str]] = None,
            test_logger: Optional[logging.Logger] = None
    ) -> List[Dict]:
        #     # One test edge (asset)
        #     "subject_id": asset.input_id,  # str
        #     "subject_category": asset.input_category,  # str
        #     "predicate_id": asset.predicate_id,  # str
        #     "object_id": asset.output_id,  # str
        #     "object_category": asset.output_category  # str
        #
        #     "environment": environment, # Optional[TestEnvEnum] = None; default: 'TestEnvEnum.ci' if not given
        #     "components": components,  # Optional[str] = None; default: 'ars' if not given
        #     "trapi_version": trapi_version,  # Optional[str] = None; latest community release if not given
        #     "biolink_version": biolink_version,  # Optional[str] = None; current Biolink Toolkit default if not given
        #     "runner_settings": asset.test_runner_settings,  # Optional[List[str]] = None
        #     "test_logger": Optional[logging.Logger],  # Python Optional[logging.Logger] = None
        """
        Run one or more knowledge graph tests, of specified kind, using a specified test asset.

        Parameters provided to specify the test are:

        - TestAsset to be used for test queries.
        :param cls: The target TestRunner subclass of GraphValidationTest of the test type to be run.
        :param subject_id: str, CURIE identifying the identifier of the subject concept
        :param subject_category: str, CURIE identifying the category of the subject concept
        :param predicate_id: str, name of Biolink Model predicate defining the statement predicate_id being tested.
        :param object_id: str, CURIE identifying the identifier of the object concept
        :param object_category: str, CURIE identifying the category of the object concept

        - Target endpoint(s) to be tested - one test report or report set generated per endpoint provided.
        :param components: Optional[str] = None, components to be tested
                                         (values from ComponentEnum in TranslatorTestingModel; default 'ars')
        :param environment: Optional[str] = None, Target Translator execution environment for the test,
                                           one of 'dev', 'ci', 'test' or 'prod' (default: 'ci')

        - Metadata globally configuring the test(s) to be run.
        :param trapi_version: Optional[str] = None, target TRAPI version (default: latest public release)
        :param biolink_version: Optional[str] = None, target Biolink Model version (default: Biolink toolkit release)
        :param runner_settings: Optional[List[str]] = None, extra string parameters to the Test Runner
        :param test_logger: Optional[logging.Logger] = None, Python logging handle

        :return: Dict { "pks": List[<pks>], "results": Dict[<pks>, <pks_result>] }
        """
        # List of endpoints for testing, based on components and environment
        # requested. The specified test asset is used to query each endpoint
        # independently, to generate a separate test report. Each test report
        # may itself be composed of  one or more independent TestCases,
        # depending on the objective and design of the TestRunner.
        endpoints: List[str] = target_component_urls(env=env_spec[environment], components=components)

        # Load the internal TestAsset being uniformly
        # served to all (endpoint x testcase) test runs.
        test_asset: TestAsset = GraphValidationTest.build_test_asset(
            subject_id,
            subject_category,
            predicate_id,
            object_id,
            object_category
        )

        # One test object - each running and reporting independently -
        # is configured for each resolved component endpoint.
        test_objects: List[cls] = list()
        for endpoint in endpoints:
            test_objects.append(
                cls(
                    target=endpoint,
                    test_asset=test_asset,
                    trapi_version=trapi_version,
                    biolink_version=biolink_version,
                    runner_settings=runner_settings,
                    test_logger=test_logger
                )
            )

        # Concurrently run the tests...
        await asyncio.gather(*[await target.run() for target in test_objects])

        # ... then, return the results
        return [target.get_results() for target in test_objects]

    def get_results(self) -> Dict:
        # The ARS_test_Runner with the following command:
        #
        #       ARS_Test_Runner
        #           --env 'ci'
        #           --query_type 'treats_creative'
        #           --expected_output '["TopAnswer","TopAnswer"]'
        #           --input_curie 'MONDO:0005301'
        #           --output_curie  '["PUBCHEM.COMPOUND:107970","UNII:3JB47N2Q2P"]'
        #
        # gives a Python dictionary report (serialized to JSON) somewhat as follows:
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
        # TODO: need to sync and iterate with TestHarness conception of TestRunner results
        return {test_name: report.get_messages() for test_name, report in self.results.items()}


def get_component_infores(component: str):
    infores_map = {
        "arax": "arax",
        "aragorn": "aragorn",
        "bte": "biothings-explorer",
        "improving": "improving-agent",
    }
    # TODO: what if the component is not yet registered in the model?
    return f"infores:{infores_map.setdefault(component, component)}"


@lru_cache()
def target_component_urls(env: str, components: Optional[str] = None) -> List[str]:
    """
    Resolve target endpoints for running the test.

    :param components: Optional[str], components to be tested
                       (values from 'ComponentEnum' in TranslatorTestingModel; default 'ars')
    :param env: target Translator execution environment of component(s) to be tested.
    :return: List[str], environment-specific endpoint(s) for component(s) to be tested.
    """
    endpoints: List[str] = list()
    component_list: List[str]
    if components:
        # TODO: need to validate/sanitize the list of components
        component_list = components.split(",")
    else:
        component_list = ['ars']
    for component in component_list:
        if component == 'ars':
            endpoints.append(f"https://{env}.transltr.io/ars/api/")
        else:
            # TODO: resolve the endpoints for non-ARS targets using the Translator SmartAPI Registry?
            registry_data: Dict = get_the_registry_data()
            service_metadata = \
                extract_component_test_metadata_from_registry(
                    registry_data,
                    "ARA",  # TODO: how can I also track KP's?
                    target_source=get_component_infores(component),
                    target_x_maturity=env
                )
            if not service_metadata:
                raise NotImplementedError("Non-ARS component-specific testing not yet implemented?")

            # TODO: fix this! the service_metadata is a complex dictionary of entries.. how do we resolve it?
            endpoints.append(service_metadata["url"])

    return endpoints


def get_parameters():
    """Parse CLI args."""

    # Sample command line interface parameters:
    #     --environment 'ci'
    #     --subject_id 'MONDO:0005301'
    #     --predicate_id 'treats'
    #     --object_id  'PUBCHEM.COMPOUND:107970'

    parser = ArgumentParser(description="Translator SRI Automated Test Harness")

    parser.add_argument(
        "--environment",
        type=str,
        required=True,
        choices=['dev', 'ci', 'test', 'prod'],
        help="Translator execution environment of the Translator Component targeted for testing.",
    )

    parser.add_argument(
        "--components",
        type=str,
        help="Names Translator components to be tested taken from the Translator Testing Model 'ComponentEnum' " +
             "(may be a comma separated string of such names; default: run the test against the 'ars')",
        default=None
    )

    parser.add_argument(
        "--subject_id",
        type=str,
        required=True,
        help="Statement object concept CURIE",
    )

    parser.add_argument(
        "--predicate_id",
        type=str,
        required=True,
        help="Statement Biolink Predicate identifier",
    )

    # TODO: should this be multi-valued or not?
    parser.add_argument(
        "--object_id",
        type=str,
        required=True,
        help="Statement object concept CURIE ",
    )

    parser.add_argument(
        "--trapi_version",
        type=str,
        help="TRAPI version expected for knowledge graph access (default: use current default release)",
        default=None
    )

    parser.add_argument(
        "--biolink_version",
        type=str,
        help="Biolink Model version expected for knowledge graph access (default: use current default release)",
        default=None
    )

    parser.add_argument(
        "--log_level",
        type=str,
        choices=["ERROR", "WARNING", "INFO", "DEBUG"],
        help="Level of the logs.",
        default="WARNING"
    )

    return parser.parse_args()
