"""
One Hop Tests (core tests extracted
from the legacy SRI_Testing project)
"""
from sys import stderr
from typing import Optional, List, Dict
import asyncio

from reasoner_validator.trapi import TRAPISchemaValidator, call_trapi
from reasoner_validator.validator import TRAPIResponseValidator
from graph_validation_test import (
    GraphValidationTest,
    TestCaseRun,
    get_parameters
)
from one_hop_test.unit_test_templates import (
    by_subject,
    inverse_by_new_subject,
    by_object,
    raise_subject_entity,
    raise_object_entity,
    raise_object_by_subject,
    raise_predicate_by_subject
)

# from .utils.asyncio import gather


class OneHopTestCaseRun(TestCaseRun):

    async def process_test_case(self):
        """
        Method to execute a TRAPI lookup, using a 'test' code template
        that defines a single TestCase using the GraphValidationTest associated TestAsset.
        :return: None, results are captured as validation messages within the TestCaseRun parent.
        """
        output_element: Optional[str]
        output_node_binding: Optional[str]

        # TODO: not sure if this is necessary - is the remapping
        #       of test asset fields already accomplished elsewhere?
        test_asset = self.translate_test_asset()

        trapi_request, output_element, output_node_binding = self.test(test_asset)

        if not trapi_request:
            # output_element and output_node_binding were
            # expropriated by the 'creator' to return error information
            context = output_element.split("|")
            self.report(
                code="critical.trapi.request.invalid",
                identifier=context[1],
                context=context[0],
                reason=output_node_binding
            )

        else:
            # sanity check: verify first that the TRAPI request is well-formed by the creator(case)
            validator: TRAPISchemaValidator = TRAPISchemaValidator(trapi_version=self.trapi_version)
            validator.validate(trapi_request, component="Query")
            self.merge(validator)
            if not self.has_messages():

                # if no messages are reported, then continue with the validation

                # TODO: this is SRI_Testing harness functionality which we don't yet support here?
                #
                # if 'ara_source' in _test_asset and _test_asset['ara_source']:
                #     # sanity check!
                #     assert 'kp_source' in test_asset and test_asset['kp_source']
                #
                #     # Here, we need annotate the TRAPI request query graph to
                #     # constrain an ARA query to the test case specified 'kp_source'
                #     trapi_request = constrain_trapi_request_to_kp(
                #         trapi_request=trapi_request, kp_source=test_asset['kp_source']
                #     )

                # Make the TRAPI call to the TestCase targeted ARS, KP or
                # ARA resource, using the case-documented input test edge
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
                    response: Optional[Dict] = trapi_response['response_json']

                    if response:
                        # Report 'trapi_version' and 'biolink_version' recorded
                        # in the 'response_json' (if the tags are provided)
                        if 'schema_version' not in response:
                            self.report(code="warning.trapi.response.schema_version.missing")
                        else:
                            trapi_version: str = response['schema_version'] \
                                if not self.trapi_version else self.trapi_version
                            print(f"run_one_hop_unit_test() using TRAPI version: '{trapi_version}'", file=stderr)

                        if 'biolink_version' not in response:
                            self.report(code="warning.trapi.response.biolink_version.missing")
                        else:
                            biolink_version = response['biolink_version'] \
                                if not self.biolink_version else self.biolink_version
                            self.get_logger().info(
                                f"run_one_hop_unit_test() using Biolink Model version: '{biolink_version}'"
                            )

                        # If nothing badly wrong with the TRAPI Response to this point, then we also check
                        # whether the test input edge was returned in the Response Message knowledge graph
                        #
                        # case: Dict contains something like:
                        #
                        #     idx: 0,
                        #     subject_category: 'biolink:SmallMolecule',
                        #     object_category: 'biolink:Disease',
                        #     predicate: 'biolink:treats',
                        #     subject_id: 'CHEBI:3002',  # may have the deprecated key 'subject' here
                        #     object_id: 'MESH:D001249', # may have the deprecated key 'object' here
                        #
                        # the contents for which ought to be returned in
                        # the TRAPI Knowledge Graph, as a Result mapping?
                        #
                        validator: TRAPIResponseValidator = TRAPIResponseValidator(
                            trapi_version=self.trapi_version,
                            biolink_version=self.biolink_version
                        )
                        if not validator.case_input_found_in_response(test_asset, response, self.trapi_version):
                            test_edge_id: str = f"{test_asset['idx']}|" \
                                                f"({test_asset['subject_id']}#{test_asset['subject_category']})" + \
                                                f"-[{test_asset['predicate']}]->" + \
                                                f"({test_asset['object_id']}#{test_asset['object_category']})"
                            self.report(
                                code="error.trapi.response.knowledge_graph.missing_expected_edge",
                                identifier=test_edge_id
                            )
                    else:
                        self.report(code="error.trapi.response.empty")


class OneHopTest(GraphValidationTest):
    pass


if __name__ == '__main__':

    args = get_parameters()

    # TRAPI test case query generators
    # used for OneHopTest runs
    trapi_generators = [
        by_subject,
        inverse_by_new_subject,
        by_object,
        raise_subject_entity,
        raise_object_entity,
        raise_object_by_subject,
        raise_predicate_by_subject
    ]
    results: List[Dict] = asyncio.run(
        OneHopTest.run_tests(
            trapi_generators=trapi_generators,
            **vars(args)
        )
    )
    print(results)
