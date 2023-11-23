"""
One Hop Tests (core tests extracted
from the legacy SRI_Testing project)
"""
from typing import Dict, List, Optional
from argparse import ArgumentParser
from translator_testing_model.datamodel.pydanticmodel import TestAsset
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


def get_test_asset(query_type, expected_output, input_curie, output_curie) -> TestAsset:
    # query_type, expected_output, input_curie, output_curie
    #
    #    mapped onto
    #
    # class TestCase(TestEntity):
    #     """
    #     Represents a single enumerated instance of Test Case,
    #     derived from a  given TestAsset and used to probe a particular test condition.
    #     """
    #     inputs: Optional[List[str]] = Field(default_factory=list)
    #     outputs: Optional[List[str]] = Field(default_factory=list)
    #     preconditions: Optional[List[str]] = Field(default_factory=list)
    #     id: str = Field(..., description="""A unique identifier for a Test Entity""")
    #     name: Optional[str] = Field(None, description="""A human-readable name for a Test Entity""")
    #     description: Optional[str] = Field(None, description="""A human-readable description for a Test Entity""")
    #     tags: Optional[List[str]] = Field(
    #                   default_factory=list,
    #                   description="""A human-readable tags for categorical memberships of a
    #                                  TestEntity (preferably a URI or CURIE). Typically used to
    #
    return TestAsset()


def run_onehop_tests(
        env, query_type, expected_output, input_curie, output_curie, log_level: Optional[str] = None
) -> Dict:
    ars_env = env_spec[env]
    one_hop_test: OneHopTest = OneHopTest(url=f"https://{ars_env}.transltr.io/ars/api/", log_level=log_level)
    testasset: TestAsset = get_test_asset(query_type, expected_output, input_curie, output_curie)
    one_hop_test.run(test_asset=testasset)
    return one_hop_test.get_result()


def get_parameters():
    """Parse CLI args."""

    # Sample command line interface parameters:
    #     --env 'ci'
    #     --query_type 'treats_creative'  # currently ignored by this TestRunner
    #     --expected_output 'TopAnswer,TopAnswer'
    #     --input_curie 'MONDO:0005301'
    #     --output_curie  'PUBCHEM.COMPOUND:107970,UNII:3JB47N2Q2P'

    parser = ArgumentParser(description="Translator SRI Automated Test Harness")

    parser.add_argument(
        "env",
        type=str,
        choices=['dev', 'ci', 'test' 'prod'],
        help="Target Translator execution environment for the test.",
    )

    parser.add_argument(
        "--query_type",
        type=str,
        help="Query Type (see Translator Testing Model; currently ignored by this TestRunner)",
    )

    parser.add_argument(
        "--expected_output",
        type=str,
        help="Expected output (may be a comma separated string of CURIEs)",
    )

    parser.add_argument(
        "--input_curie",
        type=str,
        help="Input CURIE",
    )

    parser.add_argument(
        "--output_curie",
        type=str,
        help="Output CURIE (may be a comma separated string of CURIEs)",
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
