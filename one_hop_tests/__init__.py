"""
One Hop Tests (core tests extracted
from the legacy SRI_Testing project)
"""

from translator_testing_model.datamodel.pydanticmodel import (
    TestMetadata,
    TestAsset,
    AcceptanceTestAsset,
    TestCase,
    TestSuite,
    FileFormatEnum,
    AcceptanceTestSuite,
    BenchmarkTestSuite,
    StandardsComplianceTestSuite,
    OneHopTestSuite,
    TestSuiteSpecification
)
from util import *


def run_onehop_test(test: TestCase):
    """
    Wrapper to invoke a OneHopTest on a single TestAsset
    in a given test environment for a given query type
    """
    # Prepare and run available Unit Tests on the provided TestAsset:
    #
    # - by_subject
    # - inverse_by_new_subject
    # - by_object
    # - raise_subject_entity
    # - raise_object_entity
    # - raise_object_by_subject
    # - raise_predicate_by_subject
    return None
