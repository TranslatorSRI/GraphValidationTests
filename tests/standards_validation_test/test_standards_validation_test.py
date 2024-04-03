"""
Unit tests for Standards Validation Test code validation
"""
from sys import stderr
from typing import Dict
from json import dump
from translator_testing_model.datamodel.pydanticmodel import TestEnvEnum
from standards_validation_test import StandardsValidationTest
from graph_validation_test.utils.unit_test_templates import by_subject, by_object
from tests import SAMPLE_TEST_INPUT_1


def test_standards_validation_test():
    trapi_generators = [
        by_subject,
        by_object
    ]
    results: Dict = StandardsValidationTest.run_tests(
        **SAMPLE_TEST_INPUT_1,
        trapi_generators=trapi_generators,
        environment=TestEnvEnum.ci,
        components="arax,molepro"
    )
    dump(results, stderr, indent=4)


# ARS tests not yet supported so yes... results will
# always be empty, with a logger message to inform why
def test_standards_validation_test_on_ars():
    trapi_generators = [
        by_subject,
        by_object
    ]
    results: Dict = StandardsValidationTest.run_tests(
        **SAMPLE_TEST_INPUT_1,
        trapi_generators=trapi_generators,
        environment=TestEnvEnum.ci
    )
    assert not results
