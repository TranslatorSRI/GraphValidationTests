"""
One Hop Tests (core tests extracted
from the legacy SRI_Testing project)
"""
import sys
from typing import Any, Optional, Dict
from json import dump
import asyncio

from graph_validation_tests import (
    GraphValidationTest,
    TestCaseRun,
    get_parameters
)

from graph_validation_tests.utils.unit_test_templates import (
    by_subject,
    inverse_by_new_subject,
    by_object,
    raise_subject_entity,
    raise_object_entity,
    raise_object_by_subject,
    raise_predicate_by_subject
)
import logging
logger = logging.getLogger(__name__)


class OneHopTestCaseRun(TestCaseRun):
    #
    # TODO: there is some SRI_Testing harness functionality which
    #       we don't yet (and perhaps may not need to) support here?
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

    def validate_test_case(self):
        """
        Validates a previously run TRAPI response JSON result
        resulting from a provided TestAsset, against the output
        validation criteria of the given StandardsValidationTest.
        The 'test_asset' and 'trapi_response' values are expected
        to be recorded in the TestCaseRun instance attributes.

        :return: Dict, a dictionary containing the Translator Test results
        """
        # We assume that nothing is badly wrong with the TRAPI Response to this point, then we
        # check whether the test input edge was returned in the Response Message knowledge graph.
        #
        # the TestCase: Dict contains something like:
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
        if not self.trapi_response:
            # nothing to validate here? Report this and exit...
            self.report(code="error.trapi.response.empty")
            return

        self.testcase_input_found_in_response(self.test_asset, self.trapi_response)


class OneHopTest(GraphValidationTest):
    def test_case_wrapper(
            self,
            test: Optional = None,
            trapi_response: Optional[Dict[str, Any]] = None,
            **kwargs
    ) -> TestCaseRun:
        """
        Converts currently bound TestAsset into
        a usable OneHopTestCaseRun.

        :param test: Optional, pointer to a code function that
                     configures an individual TRAPI query request (default: None)
                     See graph_validation_tests.unit_test_templates.
        :param trapi_response: Optional[Dict[str, Any]], pre-run TRAPI Response for validation (default: None)
        :param kwargs: Dict, optional extra named parameters to passed to TestCase TestRunner.
        :return: TestCaseRun object
        """
        return OneHopTestCaseRun(
            test_run=self,
            test=test,
            trapi_response=trapi_response,
            **kwargs
        )


async def run_one_hop_tests(**kwargs) -> Dict:
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
    results: Dict = await OneHopTest.run_tests(trapi_generators=trapi_generators, **kwargs)
    return results


def main():
    args = get_parameters(tool_name="One Hop Test of Knowledge Graph Navigation")
    results: Dict = asyncio.run(run_one_hop_tests(**vars(args)))
    # TODO: need to save these results somewhere central?
    dump(results, sys.stdout)


if __name__ == '__main__':
    main()
