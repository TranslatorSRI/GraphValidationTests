"""
Unit tests to validate graph_validation_test::UnitTestReport class
"""
import pytest
from translator_testing_model.datamodel.pydanticmodel import TestAsset
from graph_validation_test import UnitTestReport, GraphValidationTest

import logging

from tests import DEFAULT_TRAPI_VERSION, DEFAULT_BMT

logger = logging.getLogger(__name__)

TEST_ASSET_1 = {
    "subject_id": "DRUGBANK:DB01592",
    "subject_category": "biolink:SmallMolecule",
    "predicate_id": "biolink:treats",
    "object_id": "MONDO:0011426",
    "object_category": "biolink:Disease"
}


#         BiolinkValidator.__init__(
#             self,
#             prefix=test_name,  # TODO: generate_test_error_msg_prefix(test_case, test_name=test_name)
#             trapi_version=trapi_version,
#             biolink_version=biolink_version
#         )
#         self.test_asset = test_asset
#         self.logger = test_logger
#         # self.messages: Dict[str, Set[str]] = {
#         #     "skipped": set(),
#         #     "critical": set(),
#         #     "failed": set(),
#         #     "warning": set(),
#         #     "info": set()
#         # }
#         # adding the "skipped" category to messages
#         self.messages["skipped"] = dict()
#         self.trapi_request: Optional[Dict] = None
#         self.trapi_response: Optional[Dict[str, int]] = None

def test_default_unit_test_report_construction():
    test_asset: TestAsset = GraphValidationTest.build_test_asset(**TEST_ASSET_1)
    unit_test_report = UnitTestReport(
        test_name="test_default_unit_test_report_construction",
        test_asset=test_asset,
        test_logger=logger
    )
    assert unit_test_report
    assert unit_test_report.get_trapi_version() == DEFAULT_TRAPI_VERSION
    assert unit_test_report.get_biolink_version() == DEFAULT_BMT.get_model_version()


def test_explicit_releases_unit_test_report_construction():
    test_asset: TestAsset = GraphValidationTest.build_test_asset(**TEST_ASSET_1)
    unit_test_report = UnitTestReport(
        test_name="test_explicit_releases_unit_test_report_construction",
        test_asset=test_asset,
        test_logger=logger,
        trapi_version="1.4.2",
        biolink_version="3.5.0"
    )
    assert unit_test_report.get_trapi_version() == "v1.4.2"
    assert unit_test_report.get_biolink_version() == "3.5.0"


def test_unit_test_report_regular_messages():
    test_asset: TestAsset = GraphValidationTest.build_test_asset(**TEST_ASSET_1)
    unit_test_report = UnitTestReport(
        test_name="test_unit_test_report_messages",
        test_asset=test_asset,
        test_logger=logger
    )
    unit_test_report.report(
        code="error.biolink.model.noncompliance",
        identifier="",
        biolink_version=DEFAULT_BMT
    )
    unit_test_report.report(code="info.compliant")
    assert len(unit_test_report.get_critical()) == 0
    errors = unit_test_report.get_errors()
    assert len(errors) == 1
    assert "error.biolink.model.noncompliance" in errors
    info = unit_test_report.get_info()
    assert len(info) == 1
    assert "info.compliant" in info


def test_unit_test_report_skip_messages():
    test_asset: TestAsset = GraphValidationTest.build_test_asset(**TEST_ASSET_1)
    unit_test_report = UnitTestReport(
        test_name="test_unit_test_report_messages",
        test_asset=test_asset,
        test_logger=logger
    )
    unit_test_report.report(code="skipped.test")
    skipped = unit_test_report.get_skipped()
    assert len(skipped) == 1
    assert "skipped.test" in skipped
