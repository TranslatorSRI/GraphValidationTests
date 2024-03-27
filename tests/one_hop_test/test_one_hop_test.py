"""
Unit tests for top level One Hop Test code validation
"""
from sys import stderr
from typing import Dict
from json import dump
from one_hop_test import OneHopTest
from graph_validation_test.unit_test_templates import (
    by_subject,
    inverse_by_new_subject,
    by_object,
    raise_subject_entity,
    raise_object_entity,
    raise_object_by_subject,
    raise_predicate_by_subject
)

SAMPLE_TEST_INPUT = {
    # One test edge (asset)
    "subject_id": "DRUGBANK:DB01592",
    "subject_category": "biolink:SmallMolecule",
    "predicate_id": "biolink:treats",
    "object_id": "MONDO:0011426",
    "object_category": "biolink:Disease",
    #
    #     "environment": environment, # Optional[TestEnvEnum] = None; default: 'TestEnvEnum.ci' if not given
    #     "components": components,  # Optional[str] = None; default: 'ars' if not given
    #     "trapi_version": trapi_version,  # Optional[str] = None; latest community release if not given
    #     "biolink_version": biolink_version,  # Optional[str] = None; current Biolink Toolkit default if not given
    #     "runner_settings": asset.test_runner_settings,  # Optional[List[str]] = None
    #     "logger": logger,  # Python Optional[logging.Logger] = None
}


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
    results: Dict = OneHopTest.run_tests(trapi_generators=trapi_generators, **SAMPLE_TEST_INPUT)
    dump(results, stderr, indent=4)
