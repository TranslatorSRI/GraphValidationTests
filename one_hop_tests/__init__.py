"""
One Hop Tests (core tests extracted
from the legacy SRI_Testing project)
"""
from typing import Dict, List, Optional
from argparse import ArgumentParser
from translator_testing_model.datamodel.pydanticmodel import TestAsset, ExpectedOutputEnum
from one_hop_tests.trapi import execute_trapi_lookup, UnitTestReport
from one_hop_tests.unit_test_templates import (
    by_subject,
    inverse_by_new_subject,
    by_object,
    raise_subject_entity,
    raise_object_entity,
    raise_object_by_subject,
    raise_predicate_by_subject
)


class OneHopTest:

    def __init__(self, url: str, log_level: Optional[str]):
        """
        OneHopTest constructor.

        :param url: str, target environment endpoint being targeted for testing
        :param log_level: str, logging level for diagnostics
        """
        self.url: str = url
        self.log_level: Optional[str] = log_level
        self.results: Dict = dict()

    def run(self, test_asset: TestAsset):
        """
        Wrapper to invoke a OneHopTest on a single TestAsset
        in a given test environment for a given query type.

        :param test_asset: TestAsset, test to be processed for target TestCases.
        :return: None (use 'get_result()' method below)
        """
        self.results["by_subject"] = execute_trapi_lookup(
            self.url, test_asset, by_subject
        )
        self.results["inverse_by_new_subject"] = execute_trapi_lookup(
            self.url, test_asset, inverse_by_new_subject
        )
        self.results["by_object"] = execute_trapi_lookup(
            self.url, test_asset, by_object
        )
        self.results["raise_subject_entity"] = execute_trapi_lookup(
            self.url, test_asset, raise_subject_entity
        )
        self.results["raise_object_by_subject"] = execute_trapi_lookup(
            self.url, test_asset, raise_object_by_subject
        )
        self.results["raise_predicate_by_subject"] = execute_trapi_lookup(
            self.url, test_asset, raise_predicate_by_subject
        )

    def get_result(self) -> Dict[str, Dict[str, List[str]]]:
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


def generate_test_asset_id() -> str:
    global _id
    _id += 1
    return f"TestAsset:{_id:0>5}"


def get_test_asset(input_curie, relationship, output_curie, expected_output) -> TestAsset:
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
    #     predicate: str = Field(...)
    #     output_id: str = Field(...)
    #     output_name: Optional[str] = Field(None)
    #     expected_output: ExpectedOutputEnum = Field(...)
    #     test_issue: Optional[TestIssueEnum] = Field(None)
    #     semantic_severity: Optional[SemanticSeverityEnum] = Field(None)
    #     in_v1: Optional[bool] = Field(None)
    #     well_known: Optional[bool] = Field(None)
    #     id: str = Field(..., description="""A unique identifier for a Test Entity""")
    #     name: Optional[str] = Field(None, description="""A human-readable name for a Test Entity""")
    #     description: Optional[str] = Field(None, description="""A human-readable description for a Test Entity""")
    #     tags: Optional[List[str]] = Field(
    #           default_factory=list, description="""One or more 'tags' slot values
    #           (inherited from TestEntity) should generally be defined to specify
    #           TestAsset membership in a \"Block List\" collection  """
    #      )
    return TestAsset.construct(
        id=generate_test_asset_id(),
        input_id=input_curie,
        predicate=relationship,
        output_id=output_curie,
        expected_output=expected_output
    )


def run_onehop_tests(
        env: str,
        input_curie: str,
        relationship: str,
        output_curie: str,
        expected_output: str,
        log_level: Optional[str] = None
) -> Dict:
    """
    Run a batter of "One Hop" knowledge graph test cases using specified test asset information.
    :param env: str, Target Translator execution environment for the test, one of 'dev', 'ci', 'test' or 'prod'.
    :param input_curie: str, CURIE identifying the input ('subject') concept
    :param relationship: str, name of Biolink Model predicate defining the statement relationship being tested.
    :param output_curie: str, CURIE identifying the output ('object') concept
    :param expected_output: category of expected output (values from ExpectedOutputEnum in TranslatorTestingModel)
    :param log_level:
    :return:
    """
    ars_env = env_spec[env]
    one_hop_test: OneHopTest = OneHopTest(url=f"https://{ars_env}.transltr.io/ars/api/", log_level=log_level)

    assert expected_output in ExpectedOutputEnum.__members__

    # TODO: if output_curie is allowed to be multivalued here, how should the code be run?

    # OneHop tests directly use Test Assets to internally configure and run its Test Cases
    test_asset: TestAsset = get_test_asset(input_curie, relationship, output_curie, expected_output)

    one_hop_test.run(test_asset=test_asset)

    return one_hop_test.get_result()


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
        "env",
        type=str,
        required=True,
        choices=['dev', 'ci', 'test', 'prod'],
        help="Target Translator execution environment for the test.",
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
        "--log_level",
        type=str,
        choices=["ERROR", "WARNING", "INFO", "DEBUG"],
        help="Level of the logs.",
        default="WARNING",
    )

    return parser.parse_args()


if __name__ == '__main__':
    args = get_parameters()
    run_onehop_tests(**vars(args))
