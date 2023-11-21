"""
One Hop Tests (core tests extracted
from the legacy SRI_Testing project)
"""

from translator_testing_model.datamodel.pydanticmodel import TestCase
from one_hop_tests.trapi import execute_trapi_lookup, UnitTestReport
from one_hop_tests import (
    by_subject,
    inverse_by_new_subject,
    by_object,
    raise_subject_entity,
    raise_object_entity,
    raise_object_by_subject,
    raise_predicate_by_subject
)


class OneHopTest:

    def __init__(self):
        self.results: Dict = dict()

    def run_onehop_tests(self, testcase: TestCase):
        """
        Wrapper to invoke a OneHopTest on a single TestAsset
        in a given test environment for a given query type
        :param testcase:
        :return: None (use 'get_result()' method below)
        """
        self.results["by_subject"] = execute_trapi_lookup(testcase, by_subject)
        self.results["inverse_by_new_subject"] = execute_trapi_lookup(testcase, inverse_by_new_subject)
        self.results["by_object"] = execute_trapi_lookup(testcase, by_object)
        self.results["raise_subject_entity"] = execute_trapi_lookup(testcase, raise_subject_entity)
        self.results["raise_object_by_subject"] = execute_trapi_lookup(testcase, raise_object_by_subject)
        self.results["raise_predicate_by_subject"] = execute_trapi_lookup(testcase, raise_predicate_by_subject)

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
        return {test_name: report.get_messages() for test_name, report in results.items()}

