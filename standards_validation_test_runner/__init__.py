"""
TRAPI and Biolink Model Standards Validation
test (using reasoner-validator)
"""
from typing import Any, Optional, Dict
import asyncio

from graph_validation_tests import (
    GraphValidationTest,
    TestCaseRun,
    get_parameters
)

# For the initial implementation of the StandardsValidation,
# we just do a simply 'by_subject' TRAPI query
from graph_validation_tests.utils.unit_test_templates import by_subject, by_object


class StandardsValidationTestCaseRun(TestCaseRun):

    def validate_test_case(self):
        """
        Validates a previously run TRAPI response JSON result
        resulting from a provided TestAsset, against the output
        validation criteria of the given StandardsValidationTest.
        The test_asset and trapi_response values are expected
        to be recorded in the TestCaseRun instance attributes.

        :return: Dict, a dictionary containing the Translator Test results
        """
        # We assume that there is some kind of TRAPI Response to this point,
        # then we check whether the TRAPI Response JSON is compliant with
        # current TRAPI and Biolink Model version expectations,
        # assessed without any reference back to the input TestAsset.
        self.check_compliance_of_trapi_response(response=self.trapi_response)


class StandardsValidationTest(GraphValidationTest):
    def test_case_wrapper(
            self,
            test: Optional = None,
            trapi_response: Optional[Dict[str, Any]] = None,
            **kwargs
    ) -> TestCaseRun:
        """
        Converts currently bound TestAsset into
        a usable StandardsValidationTestCaseRun.

        :param test: Optional, pointer to a code function that
                     configures an individual TRAPI query request (default: None)
                     See graph_validation_tests.unit_test_templates.
        :param trapi_response: Optional[Dict[str, Any]], pre-run TRAPI Response for validation (default: None)
        :param kwargs: Dict, optional extra named parameters to passed to TestCase TestRunner.
        :return: TestCaseRun object
        """
        return StandardsValidationTestCaseRun(
            test_run=self,
            test=test,
            trapi_response=trapi_response,
            **kwargs
        )


async def run_standards_validation_tests(**kwargs) -> Dict:
    # TRAPI test case query generators
    # used for StandardsValidationTest
    trapi_generators = [by_subject, by_object]
    results: Dict = await StandardsValidationTest.run_tests(trapi_generators=trapi_generators, **kwargs)
    return results


def main():
    args = get_parameters(tool_name="Translator TRAPI and Biolink Model Validation of Knowledge Graphs")
    results: Dict = asyncio.run(run_standards_validation_tests(**vars(args)))
    # TODO: need to save these results somewhere central?
    print(results)


if __name__ == '__main__':
    main()
