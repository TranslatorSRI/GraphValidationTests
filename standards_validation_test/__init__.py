"""
TRAPI and Biolink Model Standards Validation test (using reasoner-validator)
"""
from typing import List, Dict
import asyncio

# from translator_testing_model.datamodel.pydanticmodel import TestAsset
from graph_validation_test import GraphValidationTest, get_parameters


class StandardsValidationTest(GraphValidationTest):

    async def run(self):
        """
        Wrapper to invoke a StandardsValidationTest co-routine run, on the
        currently bound TestAsset, in a given test environment, to assess
        compliance to the assumed TRAPI and Biolink Model releases.

        :return: None - use 'GraphValidationTest.get_results()'
        or its subclass implementation, to access the test results.
        """
        raise NotImplementedError("Implement this")


if __name__ == '__main__':
    args = get_parameters()
    results: List[Dict] = asyncio.run(StandardsValidationTest.run_test(**vars(args)))
    print(results)
