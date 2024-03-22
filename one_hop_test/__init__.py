"""
One Hop Tests (core tests extracted
from the legacy SRI_Testing project)
"""
from sys import stderr
from typing import Optional, List, Dict
import asyncio

from reasoner_validator.trapi import TRAPISchemaValidator, call_trapi
from reasoner_validator.validator import TRAPIResponseValidator
from graph_validation_test import GraphValidationTest, get_parameters
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


class OneHopTest(GraphValidationTest):

    async def run_one_hop_unit_test(self, url: str, creator):
        """
        Method to execute a TRAPI lookup, using the 'creator' test template.

        :param url: str, target TRAPI url endpoint to be tested
        :param creator: unit test-specific TRAPI query message creator
        :return: results: Dict of results
        """
        # TODO: how can this be made thread safe if co-routines are concurrently executed?
        #       Maybe not completely but adequately by assuming that the messages data for
        #       each distinct co-routine (test) is  uniquely indexed by its (test_run,) url
        #       and test (creator) name, and that the 'message' data is accessed thus.
        self.reset_default_test(creator.__name__)

        trapi_request: Optional[Dict]
        output_element: Optional[str]
        output_node_binding: Optional[str]

        # TODO: not sure if this is necessary - is the remapping
        #       of test asset fields already accomplished elsewhere?
        _test_asset = self.translate_test_asset()

        trapi_request, output_element, output_node_binding = creator(_test_asset)

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
                #     assert 'kp_source' in _test_asset and _test_asset['kp_source']
                #
                #     # Here, we need annotate the TRAPI request query graph to
                #     # constrain an ARA query to the test case specified 'kp_source'
                #     trapi_request = constrain_trapi_request_to_kp(
                #         trapi_request=trapi_request, kp_source=_test_asset['kp_source']
                #     )

                # Make the TRAPI call to the TestCase targeted ARS, KP or
                # ARA resource, using the case-documented input test edge
                trapi_response = await call_trapi(url, trapi_request)

                # Capture the raw TRAPI query input and output
                # for possibly later test harness access
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
                            self.logger.info(
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
                        if not validator.case_input_found_in_response(_test_asset, response, self.trapi_version):
                            test_edge_id: str = f"{_test_asset['idx']}|" \
                                                f"({_test_asset['subject_id']}#{_test_asset['subject_category']})" + \
                                                f"-[{_test_asset['predicate']}]->" + \
                                                f"({_test_asset['object_id']}#{_test_asset['object_category']})"
                            self.report(
                                code="error.trapi.response.knowledge_graph.missing_expected_edge",
                                identifier=test_edge_id
                            )
                    else:
                        self.report(code="error.trapi.response.empty")

    async def run(self):
        """
        Implementation of abstract GraphValidationTest.run() operation
        to invoke a OneHopTest co-routine test runs, on the
        currently bound TestAsset, in a given component endpoint,
        for each given type of "one hop" unit test query.

        :return: None - use 'GraphValidationTest.get_results()'
                 or its subclass implementation, to access test results.
        """
        #
        #     TODO: How are the results to be retrieved and indexed?
        #           Are semaphores and locks also now needed for
        #           thread safety for the reporting of validation messages?
        #
        # Partial answer is that the 'test_name' is reset each time in the
        # report, thus serving as a kind of indexing (nothing now returned
        # by the co-routine... perhaps a more clever internal indexing
        # of validation messages is now necessary?)
        #
        test_case_runs = [
            await self.run_one_hop_unit_test(self.default_target, test_type)
            for test_type in [
                by_subject,
                inverse_by_new_subject,
                by_object,
                raise_subject_entity,
                raise_object_by_subject,
                raise_predicate_by_subject
            ]
        ]
        await asyncio.gather(*test_case_runs)  # , limit=num_concurrent_requests)


if __name__ == '__main__':
    args = get_parameters()
    results: List[Dict] = asyncio.run(OneHopTest.run_test(**vars(args)))
    print(results)
