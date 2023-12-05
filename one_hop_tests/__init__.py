"""
One Hop Tests (core tests extracted
from the legacy SRI_Testing project)
"""
from typing import Dict, List, Optional
from functools import lru_cache
from argparse import ArgumentParser
from translator_testing_model.datamodel.pydanticmodel import TestAsset, ExpectedOutputEnum
from one_hop_tests.translator.trapi import execute_trapi_lookup, UnitTestReport
from one_hop_tests.unit_test_templates import (
    by_subject,
    inverse_by_new_subject,
    by_object,
    raise_subject_entity,
    raise_object_entity,
    raise_object_by_subject,
    raise_predicate_by_subject
)
from one_hop_tests.translator.registry import (
    get_the_registry_data,
    extract_component_test_metadata_from_registry
)


class OneHopTest:

    def __init__(
            self,
            endpoints: List[str],
            trapi_version: Optional[str] = None,
            biolink_version: Optional[str] = None,
            log_level: Optional[str] = None
    ):
        """
        OneHopTest constructor.

        :param endpoints: List[str], target environment endpoint(s) being targeted for testing
        :param trapi_version: Optional[str], target TRAPI version (default: current release)
        :param biolink_version: Optional[str], target Biolink Model version (default: current release)
        :param log_level: Optional[str], logging level for diagnostics
        """
        self.endpoints: List[str] = endpoints
        self.trapi_version = trapi_version
        self.biolink_version = biolink_version
        self.log_level: Optional[str] = log_level
        self.results: Dict = dict()

    def test_case_wrapper(self, test_asset: TestAsset):
        async def test_case(test_type) -> UnitTestReport:
            # TODO: eventually need to process multiple self.endpoints(?)
            target_url: str = self.endpoints[0]
            return await execute_trapi_lookup(
                target_url, test_asset, test_type, self.trapi_version, self.biolink_version
            )
        return test_case

    async def run(self, test_asset: TestAsset):
        """
        Wrapper to invoke a OneHopTest on a single TestAsset
        in a given test environment for a given query type.

        :param test_asset: TestAsset, test to be processed for target TestCases.
        :return: None (use 'get_results()' method below)
        """
        test_case = self.test_case_wrapper(test_asset=test_asset)
        self.results["by_subject"] = await test_case(by_subject)
        self.results["inverse_by_new_subject"] = await test_case(inverse_by_new_subject)
        self.results["by_object"] = await test_case(by_object)
        self.results["raise_subject_entity"] = await test_case(raise_subject_entity)
        self.results["raise_object_by_subject"] = await test_case(raise_object_by_subject)
        self.results["raise_predicate_by_subject"] = await test_case(raise_predicate_by_subject)

    def get_results(self) -> Dict[str, Dict[str, List[str]]]:
        # The ARS_test_Runner with the following command:
        #
        #       ARS_Test_Runner
        #           --env 'ci'
        #           --query_type 'treats_creative'
        #           --expected_output '["TopAnswer","TopAnswer"]'
        #           --input_curie 'MONDO:0005301'
        #           --output_curie  '["PUBCHEM.COMPOUND:107970","UNII:3JB47N2Q2P"]'
        #
        # gives the json report below:
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
        report: UnitTestReport
        return {test_name: report.get_messages() for test_name, report in self.results.items()}


env_spec = {
    'dev': 'ars-dev',
    'ci': 'ars.ci',
    'test': 'ars.test',
    'prod': 'ars-prod'
}


_id: int = 0


def _generate_test_asset_id() -> str:
    global _id
    _id += 1
    return f"TestAsset:{_id:0>5}"


def build_test_asset(input_curie, relationship, output_curie, expected_output) -> TestAsset:
    """
    Construct a Python TestAsset object.

    :param input_curie: test asset input 'subject' CURIE identifier
    :param relationship: human-readable name of a predicate
    :param output_curie:  test asset output 'object' CURIE identifier
    :param expected_output: from ExpectedOutputEnum, values like Top_Answer, Acceptable, BadButForgivable, NeverShow, etc.
    :return: TestAsset object
    """
    # query_type, expected_output, input_curie, output_curie
    #
    #    mapped onto
    #
    # class TestAsset(TestEntity):
    #     """
    #     Represents a Test Asset, which is a single specific instance of
    #     TestCase-agnostic semantic parameters representing the specification
    #     of a Translator test target with inputs and (expected) outputs.
    #     """
    #     input_id: str = Field(...)
    #     input_name: Optional[str] = Field(None)
    #     input_category: Optional[str] = Field(None)
    #     predicate_id: Optional[str] = Field(None)
    #     predicate_name: str = Field(...)
    #     output_id: str = Field(...)
    #     output_name: Optional[str] = Field(None)
    #     output_category: Optional[str] = Field(None)
    #     association: Optional[str] = Field(
    #                 None,
    #                 description="""Specific Biolink Model association 'category'
    #                 which applies to the test asset defined knowledge statement"""
    #     )
    #     qualifiers: Optional[List[Qualifier]] = Field(
    #                 default_factory=list,
    #                 description="""Optional qualifiers which constrain to the test asset defined knowledge statement.
    #                 Note that this field records such qualifier slots and values as tag=value pairs, where
    #                 the tag is the Biolink Model qualifier slot named and the value is an acceptable
    #                 (Biolink Model enum?) value of the said qualifier slot."""
    #     )
    #     expected_output: ExpectedOutputEnum = Field(...)
    #     test_issue: Optional[TestIssueEnum] = Field(None)
    #     semantic_severity: Optional[SemanticSeverityEnum] = Field(None)
    #     in_v1: Optional[bool] = Field(None)
    #     well_known: Optional[bool] = Field(None)
    #     test_reference: Optional[str] = Field(
    #                     None,
    #                     description="""Document URL where original test source
    #                                    particulars are registered (e.g. Github repo)"""
    #     )
    #     runner_settings: List[str] = Field(
    #                      default_factory=list, description="""Settings for the test harness, e.g. \"inferred\""""
    #     )
    #     id: str = Field(..., description="""A unique identifier for a Test Entity""")
    #     name: Optional[str] = Field(None, description="""A human-readable name for a Test Entity""")
    #     description: Optional[str] = Field(None, description="""A human-readable description for a Test Entity""")
    #     tags: Optional[List[str]] = Field(
    #                     default_factory=list, description="""One or more 'tags' slot values
    #                     (inherited from TestEntity) should generally be defined to specify
    #                     TestAsset membership in a \"Block List\" collection"""
    #      )
    return TestAsset.construct(
        id=_generate_test_asset_id(),
        input_id=input_curie,
        predicate_name=relationship,
        output_id=output_curie,
        expected_output=expected_output
    )


def get_component_infores(component: str):
    infores_map = {
        "arax": "arax",
        "aragorn": "aragorn",
        "bte": "biothings-explorer",
        "improving": "improving-agent",
    }
    # TODO: what if the component is not yet registered in the model?
    return f"infores:{infores_map.setdefault(component,component)}"


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

            endpoints.append(service_metadata["url"])

    return endpoints


def run_onehop_tests(
        env: str,
        input_curie: str,
        relationship: str,
        output_curie: str,
        expected_output: str,
        components: Optional[str] = None,
        trapi_version: Optional[str] = None,
        biolink_version: Optional[str] = None,
        log_level: Optional[str] = None
) -> Dict:
    """
    Run a battery of "One Hop" knowledge graph test cases using specified test asset information.

    :param env: str, Target Translator execution environment for the test, one of 'dev', 'ci', 'test' or 'prod'.
    :param input_curie: str, CURIE identifying the input ('subject') concept
    :param relationship: str, name of Biolink Model predicate defining the statement relationship being tested.
    :param output_curie: str, CURIE identifying the output ('object') concept
    :param expected_output: category of expected output (values from ExpectedOutputEnum in TranslatorTestingModel)
    :param components: Optional[str], components to be tested (values from ComponentEnum in TranslatorTestingModel; default 'ars')
    :param trapi_version: Optional[str], target TRAPI version (default: current release)
    :param biolink_version: Optional[str], target Biolink Model version (default: current release)
    :param log_level:
    :return:
    """
    endpoints: List[str] = target_component_urls(env=env_spec[env], components=components)

    one_hop_test: OneHopTest = OneHopTest(
        endpoints=endpoints,
        trapi_version=trapi_version,
        biolink_version=biolink_version,
        log_level=log_level
    )

    assert expected_output in ExpectedOutputEnum.__members__

    # TODO: if output_curie is allowed to be multivalued here, how should the code be run?

    # OneHop tests directly use Test Assets to internally configure and run its Test Cases
    test_asset: TestAsset = build_test_asset(input_curie, relationship, output_curie, expected_output)

    one_hop_test.run(test_asset=test_asset)

    return one_hop_test.get_results()


def get_parameters():
    """Parse CLI args."""

    # Sample command line interface parameters:
    #     --env 'ci'
    #     --input_curie 'MONDO:0005301'
    #     --relationship 'treats'
    #     --output_curie  'PUBCHEM.COMPOUND:107970,UNII:3JB47N2Q2P'
    #     --expected_output 'Acceptable'

    parser = ArgumentParser(description="Translator SRI Automated Test Harness")

    parser.add_argument(
        "--env",
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
        "--input_curie",
        type=str,
        required=True,
        help="Input CURIE",
    )

    parser.add_argument(
        "--relationship",
        type=str,
        required=True,
        help="Relationship ('Biolink Predicate') name",
    )

    # TODO: should this be multi-valued or not?
    parser.add_argument(
        "--output_curie",
        type=str,
        required=True,
        help="Output CURIE (may be a comma separated string of CURIEs)",
    )

    # Not sure if this needs to be a parameter... could potentially be hard coded internally?
    parser.add_argument(
        "--expected_output",
        type=str,
        required=True,
        help="Expected output value drawn from the ExpectedOutputEnum of the Translator Testing Model",
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


if __name__ == '__main__':
    args = get_parameters()
    results: Dict = run_onehop_tests(**vars(args))
    print(results)
