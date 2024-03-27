"""
Unit tests for Standards Validation Test code validation
"""
from sys import stderr
from typing import Dict
from json import dump
from standards_validation_test import StandardsValidationTest
from graph_validation_test.utils.unit_test_templates import by_subject, by_object
from tests import SAMPLE_TEST_INPUT_1


def test_standards_validation_test():
    trapi_generators = [
        by_subject,
        by_object
    ]
    results: Dict = StandardsValidationTest.run_tests(
        trapi_generators=trapi_generators,
        **SAMPLE_TEST_INPUT_1
    )
    dump(results, stderr, indent=4)
