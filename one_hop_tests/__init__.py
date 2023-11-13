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


def run_onehop_tests(testcase: TestCase) -> Dict[str, Dict[str, List[str]]]:
    """
    Wrapper to invoke a OneHopTest on a single TestAsset
    in a given test environment for a given query type
    """
    results: Dict = dict()
    results["by_subject"] = execute_trapi_lookup(testcase, by_subject)
    results["inverse_by_new_subject"] = execute_trapi_lookup(testcase, inverse_by_new_subject)
    results["by_object"] = execute_trapi_lookup(testcase, by_object)
    results["raise_subject_entity"] = execute_trapi_lookup(testcase, raise_subject_entity)
    results["raise_object_by_subject"] = execute_trapi_lookup(testcase, raise_object_by_subject)
    results["raise_predicate_by_subject"] = execute_trapi_lookup(testcase, raise_predicate_by_subject)
    report: UnitTestReport
    # TODO: need to sync and iterate with TestHarness conception of TestRunner results
    return {test_name: report.get_messages() for test_name, report in results.items()}
