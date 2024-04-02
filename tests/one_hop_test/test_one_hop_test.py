"""
Unit tests for One Hop Test code validation
"""
from sys import stderr
from typing import Dict
from json import dump

from translator_testing_model.datamodel.pydanticmodel import TestEnvEnum

from one_hop_test import OneHopTest
from graph_validation_test.utils.unit_test_templates import (
    by_subject,
    inverse_by_new_subject,
    by_object,
    raise_subject_entity,
    raise_object_entity,
    raise_object_by_subject,
    raise_predicate_by_subject
)
from tests import SAMPLE_TEST_INPUT_1


def test_one_hop_test():
    trapi_generators = [
        by_subject,
        inverse_by_new_subject,
        by_object,
        raise_subject_entity,
        raise_object_entity,
        raise_object_by_subject,
        raise_predicate_by_subject
    ]
    results: Dict = OneHopTest.run_tests(
        **SAMPLE_TEST_INPUT_1,
        trapi_generators=trapi_generators,
        environment=TestEnvEnum.ci,
        components="arax,molepro"
    )
    dump(results, stderr, indent=4)
