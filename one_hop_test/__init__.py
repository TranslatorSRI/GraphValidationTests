"""
One Hop Tests (core tests extracted
from the legacy SRI_Testing project)
"""
from typing import Dict
import asyncio

from translator_testing_model.datamodel.pydanticmodel import TestAsset
from graph_validation_test import GraphValidationTest, get_parameters
from one_hop_test.translator.trapi import run_one_hop_unit_test, UnitTestReport
from one_hop_test.unit_test_templates import (
    by_subject,
    inverse_by_new_subject,
    by_object,
    raise_subject_entity,
    raise_object_entity,
    raise_object_by_subject,
    raise_predicate_by_subject
)

from one_hop_test.translator.registry import (
    get_the_registry_data,
    extract_component_test_metadata_from_registry
)

# from .utils.asyncio import gather


class OneHopTest(GraphValidationTest):

    def test_case_wrapper(self, test_asset: TestAsset):
        async def test_case(test_type) -> UnitTestReport:
            # TODO: eventually need to process multiple self.endpoints(?)
            target_url: str = self.endpoints[0]
            return await run_one_hop_unit_test(
                target_url, test_asset, test_type, self.trapi_version, self.biolink_version
            )
        return test_case

    async def run(self, test_asset: TestAsset):
        """
        Wrapper to invoke a OneHopTest on a single TestAsset
        in a given test environment for a given query type.

        :param test_asset: TestAsset, test to be processed for target TestCases.
        :return: None - use 'get_results()' method below
        """
        test_case = self.test_case_wrapper(test_asset=test_asset)
        #
        # TODO: do these tests need to be run sequentially or
        #       could they be run concurrently then "gathered" together?
        #     coroutines = [
        #         test_case(test_type)
        #         for test_type in [
        #           by_subject,
        #           inverse_by_new_subject,
        #           by_object,
        #           raise_subject_entity,
        #           raise_object_by_subject,
        #           raise_predicate_by_subject
        #         ]
        #     ]
        #     await gather(*coroutines, limit=num_concurrent_requests)
        #
        #     TODO: How are the results to be retrieved and indexed?

        self.results["by_subject"] = await test_case(by_subject)
        self.results["inverse_by_new_subject"] = await test_case(inverse_by_new_subject)
        self.results["by_object"] = await test_case(by_object)
        self.results["raise_subject_entity"] = await test_case(raise_subject_entity)
        self.results["raise_object_by_subject"] = await test_case(raise_object_by_subject)
        self.results["raise_predicate_by_subject"] = await test_case(raise_predicate_by_subject)


if __name__ == '__main__':
    args = get_parameters()
    results: Dict = asyncio.run(OneHopTest.run_test(**vars(args)))
    print(results)
