"""
TRAPI and Biolink Model Standards Validation test (using reasoner-validator)
"""
from typing import Dict
import asyncio

from translator_testing_model.datamodel.pydanticmodel import TestAsset
from graph_validation_test import GraphValidationTest, get_parameters


class StandardsValidationTest(GraphValidationTest):

    async def run(self, test_asset: TestAsset):
        """
        Wrapper to invoke a StandardsValidationTest on a single TestAsset
        in a given test environment for a given query type.

        :param test_asset: TestAsset, test to be processed for target TestCases.
        :return: None - use 'get_results()' method below
        """
        raise NotImplementedError("Implement this")


if __name__ == '__main__':
    args = get_parameters()
    results: Dict = asyncio.run(StandardsValidationTest.run_test(**vars(args)))
    print(results)
