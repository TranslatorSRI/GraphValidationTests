"""
TRAPI and Biolink Model Standards Validation
test (using reasoner-validator)
"""
from typing import Optional, List, Dict
import asyncio

from reasoner_validator.trapi import call_trapi
from reasoner_validator.validator import TRAPIResponseValidator
from graph_validation_test import (
    GraphValidationTest,
    TestCaseRun,
    get_parameters
)
# For the initial implementation of the StandardsValidation,
# we just do a simply 'by_subject' TRAPI query
from one_hop_test.unit_test_templates import by_subject, by_object


class StandardsValidationTestCaseRun(TestCaseRun):

    # default constructor is inherited
    # from BiolinkValidator via TestCaseRun

    async def process_test_case(self):
        """
        Method to execute a TRAPI lookup a single TestCase
        using the GraphValidationTest associated TestAsset.

        :return: None, results are captured as validation
                       messages within the TestCaseRun parent.
        """
        output_element: Optional[str]
        output_node_binding: Optional[str]

        # TODO: not sure if this is necessary - is the remapping
        #       of test asset fields already accomplished elsewhere?
        test_asset = self.translate_test_asset()

        trapi_request, output_element, output_node_binding = by_subject(test_asset)

        if not trapi_request:
            # output_element and output_node_binding return values were
            # expropriated by 'by_subject' to return error information
            context = output_element.split("|")
            self.report(
                code="critical.trapi.request.invalid",
                identifier=context[1],
                context=context[0],
                reason=output_node_binding
            )

        else:
            # sanity check: verify first that the TRAPI request
            # is well-formed by the by_subject(test_asset)
            validator: TRAPIResponseValidator = \
                TRAPIResponseValidator(
                    trapi_version=self.trapi_version,
                    biolink_version=self.biolink_version
                )
            validator.validate(trapi_request, component="Query")
            self.merge(validator)

            # We'll ignore warnings and info messages
            if not (self.has_critical() or self.has_errors() or self.has_skipped()):

                # Make the TRAPI call to the default TestCase targeted
                # ARS, KP or ARA component, using the provided 'trapi_request'
                trapi_response = await call_trapi(self.default_target, trapi_request)

                # Capture the raw TRAPI query request and response for reporting
                self.trapi_request = trapi_request
                self.trapi_response = trapi_response

                # Second sanity check: was the web service (HTTP) call itself successful?
                status_code: int = trapi_response['status_code']
                if status_code != 200:
                    self.report("critical.trapi.response.unexpected_http_code", identifier=status_code)
                else:
                    #########################################################
                    # Looks good so far, so now validate the TRAPI response #
                    #########################################################
                    validator.check_compliance_of_trapi_response(
                        response=trapi_response['response_json']
                    )


class StandardsValidationTest(GraphValidationTest):

    async def process_test_run(self, **kwargs):
        """
        Process a single test run of the StandardsValidationTest test
        across every specified component in a given deployment environment.

        :param kwargs: Dict, optional extra named parameters to passed to TestCase TestRunner.
        """
        pass


if __name__ == '__main__':

    args = get_parameters()

    # TRAPI test case query generators
    # used for StandardsValidationTest
    trapi_generators = [by_subject, by_object]
    results: List[Dict] = asyncio.run(
        StandardsValidationTest.run_tests(
            trapi_generators=trapi_generators,
            **vars(args)
        )
    )
    print(results)
