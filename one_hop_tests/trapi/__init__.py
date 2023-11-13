"""
Code to submit OneHop tests to TRAPI
"""
from sys import stderr
from typing import Optional, Dict, Set

from reasoner_validator.validator import TRAPIResponseValidator
from reasoner_validator.report import ValidationReporter
from reasoner_validator.trapi import call_trapi, TRAPISchemaValidator

from logging import getLogger
logger = getLogger()


def generate_test_error_msg_prefix(case: Dict, test_name: str) -> str:
    assert case
    test_msg_prefix: str = "test_onehops.py::test_trapi_"
    resource_id: str = ""
    component: str = "kp"
    if 'ara_source' in case and case['ara_source']:
        component = "ara"
        ara_id = case['ara_source'].replace("infores:", "")
        resource_id += ara_id + "|"
    test_msg_prefix += f"{component}s["
    if 'kp_source' in case and case['kp_source']:
        kp_id = case['kp_source'].replace("infores:", "")
        resource_id += kp_id
    edge_idx = case['idx']
    edge_id = generate_edge_id(resource_id, edge_idx)
    if not test_name:
        test_name = "input"
    test_msg_prefix += f"{edge_id}-{test_name}] FAILED"
    return test_msg_prefix


def generate_edge_id(resource_id: str, edge_i: int) -> str:
    return f"{resource_id}#{str(edge_i)}"


class UnitTestReport(ValidationReporter):
    """
    UnitTestReport is a wrapper for ValidationReporter used to aggregate SRI Test actionable validation messages.
    Not to be confused with the translator.sri.testing.report_db.TestReport, which is the comprehensive set
    of all JSON reports from a single SRI Testing harness test run.
    """
    def __init__(self, test_case: Dict, test_name: str):
        error_msg_prefix = generate_test_error_msg_prefix(test_case, test_name=test_name)
        ValidationReporter.__init__(
            self,
            prefix=error_msg_prefix
        )
        self.messages: Dict[str, Set[str]] = {
            "skipped": set(),
            "critical": set(),
            "failed": set(),
            "warning": set(),
            "info": set()
        }

    def get_messages(self) -> Dict[str, List[str]]:
        return {test_name: list(message_set) for test_name, message_set in self.messages.items()}

    def skip(self, code: str, edge_id: str, messages: Optional[Dict] = None):
        """
        Edge test Pytest skipping wrapper.
        :param code: str, validation message code (indexed in the codes.yaml of the Reasoner Validator)
        :param edge_id: str, S-P-O identifier of the edge being skipped
        :param messages: (optional) additional validation messages available to explain why the test is being skipped
        :return:
        """
        self.report(code=code, edge_id=edge_id)
        if messages:
            self.add_messages(messages)
        report_string: str = self.dump_messages(flat=True)
        self.messages["skipped"].add(report_string)

    def assert_test_outcome(self):
        """
        Test outcomes
        """
        if self.has_critical():
            critical_msg = self.dump_critical(flat=True)
            logger.critical(critical_msg)
            self.messages["critical"].add(critical_msg)

        elif self.has_errors():
            # we now treat 'soft' errors similar to critical errors (above) but
            # the validation messages will be differentiated on the user interface
            err_msg = self.dump_errors(flat=True)
            logger.error(err_msg)
            self.messages["failed"].add(err_msg)

        elif self.has_warnings():
            wrn_msg = self.dump_warnings(flat=True)
            logger.warning(wrn_msg)
            self.messages["warning"].add(wrn_msg)

        elif self.has_information():
            info_msg = self.dump_info(flat=True)
            logger.info(info_msg)
            self.messages["info"].add(info_msg)

        else:
            pass  # do nothing... just silent pass through...


def constrain_trapi_request_to_kp(trapi_request: Dict, kp_source: str) -> Dict:
    """
    Method to annotate KP constraint on an ARA call
    as an attribute_constraint object on the test edge.
    :param trapi_request: Dict, original TRAPI message
    :param kp_source: str, KP InfoRes (from kp_source field of test edge)
    :return: Dict, trapi_request annotated with additional KP 'attribute_constraint'
    """
    assert "message" in trapi_request
    message: Dict = trapi_request["message"]
    assert "query_graph" in message
    query_graph: Dict = message["query_graph"]
    assert "edges" in query_graph
    edges: Dict = query_graph["edges"]
    assert "ab" in edges
    edge: Dict = edges["ab"]

    # annotate the edge constraint on the (presumed single) edge object
    edge["attribute_constraints"] = [
        {
            "id": "biolink:knowledge_source",
            "name": "knowledge source",
            "value": [kp_source],
            "operator": "=="
        }
    ]

    return trapi_request


def execute_trapi_lookup(testcase, creator) -> UnitTestReport:
    """
    Method to execute a TRAPI lookup, using the 'creator' test template.

    :param testcase: input data test case
    :param creator: unit test-specific TRAPI query message creator
    :return: results: Dict of results
    """
    test_report: UnitTestReport = UnitTestReport(test_case=testcase, test_name=creator.__name__)

    trapi_request: Optional[Dict]
    output_element: Optional[str]
    output_node_binding: Optional[str]

    trapi_request, output_element, output_node_binding = creator(testcase)

    if not trapi_request:
        # output_element and output_node_binding were
        # expropriated by the 'creator' to return error information
        context = output_element.split("|")
        test_report.report(
            code="critical.trapi.request.invalid",
            identifier=context[1],
            context=context[0],
            reason=output_node_binding
        )
    else:
        trapi_version = testcase['trapi_version']
        biolink_version = testcase['biolink_version']

        # sanity check: verify first that the TRAPI request is well-formed by the creator(case)
        validator: TRAPISchemaValidator = TRAPISchemaValidator(trapi_version=trapi_version)
        validator.validate(trapi_request, component="Query")
        test_report.merge(validator)
        if not test_report.has_messages():
            # if no messages are reported, then continue with the validation

            if 'ara_source' in testcase and testcase['ara_source']:
                # sanity check!
                assert 'kp_source' in testcase and testcase['kp_source']

                # Here, we need annotate the TRAPI request query graph to
                # constrain an ARA query to the test case specified 'kp_source'
                trapi_request = constrain_trapi_request_to_kp(
                    trapi_request=trapi_request, kp_source=testcase['kp_source']
                )

            # Make the TRAPI call to the Case targeted KP or ARA resource, using the case-documented input test edge
            trapi_response = await call_trapi(testcase['url'], trapi_request)

            # Record the raw TRAPI query input and output for later test harness reference
            results.request = trapi_request
            results.response = trapi_response

            # Second sanity check: was the web service (HTTP) call itself successful?
            status_code: int = trapi_response['status_code']
            if status_code != 200:
                test_report.report("critical.trapi.response.unexpected_http_code", identifier=status_code)
            else:
                #########################################################
                # Looks good so far, so now validate the TRAPI response #
                #########################################################
                response: Optional[Dict] = trapi_response['response_json']

                if response:
                    # Report 'trapi_version' and 'biolink_version' recorded
                    # in the 'response_json' (if the tags are provided)
                    if 'schema_version' not in response:
                        test_report.report(code="warning.trapi.response.schema_version.missing")
                    else:
                        trapi_version: str = response['schema_version'] if not trapi_version else trapi_version
                        print(f"execute_trapi_lookup() using TRAPI version: '{trapi_version}'", file=stderr)

                    if 'biolink_version' not in response:
                        test_report.report(code="warning.trapi.response.biolink_version.missing")
                    else:
                        biolink_version: str = response['biolink_version'] \
                            if not biolink_version else biolink_version
                        print(
                            f"execute_trapi_lookup() using Biolink Model version: '{biolink_version}'",
                            file=stderr
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
                        trapi_version=trapi_version,
                        biolink_version=biolink_version
                    )
                    if not validator.case_input_found_in_response(testcase, response, trapi_version):
                        subject_id = testcase['subject'] if 'subject' in testcase else testcase['subject_id']
                        object_id = testcase['object'] if 'object' in testcase else testcase['object_id']
                        test_edge_id: str = f"{testcase['idx']}|({subject_id}#{testcase['subject_category']})" + \
                                            f"-[{testcase['predicate']}]->" + \
                                            f"({object_id}#{testcase['object_category']})"
                        test_report.report(
                            code="error.trapi.response.knowledge_graph.missing_expected_edge",
                            identifier=test_edge_id
                        )
                else:
                    test_report.report(code="error.trapi.response.empty")

    return test_report
