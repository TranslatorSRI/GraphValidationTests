"""
Unit tests for pieces of the GraphValidationTests code
"""
from graph_validation_test import GraphValidationTest
from translator_testing_model.datamodel.pydanticmodel import ExpectedOutputEnum, TestAsset
from tests import DEFAULT_TRAPI_VERSION, DEFAULT_BMT
from translator_testing_model.datamodel.pydanticmodel import TestAsset
from graph_validation_test import TestCaseRun, GraphValidationTest

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


TEST_SUBJECT_ID = "MONDO:0005301"
TEST_SUBJECT_CATEGORY = "biolink:Disease"
TEST_PREDICATE_NAME = "treats"
TEST_PREDICATE_ID = f"biolink:{TEST_PREDICATE_NAME}"
TEST_OBJECT_ID = "PUBCHEM.COMPOUND:107970"
TEST_OBJECT_CATEGORY = "biolink:SmallMolecule"
SAMPLE_TEST_ASSET: TestAsset = GraphValidationTest.build_test_asset(
        subject_id=TEST_SUBJECT_ID,
        subject_category=TEST_SUBJECT_CATEGORY,
        predicate_id=TEST_PREDICATE_ID,
        object_id=TEST_OBJECT_ID,
        object_category=TEST_OBJECT_CATEGORY
)


# def get_component_infores(component: str)

# target_component_urls(env: str, components: Optional[str] = None) -> List[str]:

def test_generate_test_asset_id():
    assert GraphValidationTest.generate_test_asset_id() == "TestAsset:00002"
    assert GraphValidationTest.generate_test_asset_id() == "TestAsset:00003"
    assert GraphValidationTest.generate_test_asset_id() == "TestAsset:00004"


def test_build_test_asset():
    assert SAMPLE_TEST_ASSET.id == "TestAsset:00001"
    assert SAMPLE_TEST_ASSET.input_id == TEST_SUBJECT_ID
    assert SAMPLE_TEST_ASSET.input_category == TEST_SUBJECT_CATEGORY
    assert SAMPLE_TEST_ASSET.predicate_id == TEST_PREDICATE_ID
    assert SAMPLE_TEST_ASSET.predicate_name == TEST_PREDICATE_NAME
    assert SAMPLE_TEST_ASSET.output_id == TEST_OBJECT_ID
    assert SAMPLE_TEST_ASSET.output_category == TEST_OBJECT_CATEGORY
    assert SAMPLE_TEST_ASSET.expected_output is None  # not set?


# def test_default_graph_validation_test_construction():
#     gvt: GraphValidationTest = GraphValidationTest(
#         endpoints=["https://example.com", "https://example2.com"],
#         test_name="test_default_graph_validation_test_construction",
#         test_asset=SAMPLE_TEST_ASSET,
#         runner_settings=["Inferred"]
#     )
#     assert "https://example.com" in gvt.get_endpoints()
#     assert "test_default_graph_validation_test_construction" in gvt.get_test_name()
#     assert gvt.get_trapi_version() == DEFAULT_TRAPI_VERSION
#     assert gvt.get_biolink_version() == DEFAULT_BMT.get_model_version()
#     assert "Inferred" in gvt.get_runner_settings()
def test_default_unit_test_report_construction():
    test_asset: TestAsset = GraphValidationTest.build_test_asset(**TEST_ASSET_1)
    unit_test_report = TestCaseRun(
        test_name="test_default_unit_test_report_construction",
        test_asset=test_asset,
        test_logger=logger
    )
    assert unit_test_report
    assert unit_test_report.get_trapi_version() == DEFAULT_TRAPI_VERSION
    assert unit_test_report.get_biolink_version() == DEFAULT_BMT.get_model_version()


def test_explicit_releases_unit_test_report_construction():
    test_asset: TestAsset = GraphValidationTest.build_test_asset(**TEST_ASSET_1)
    unit_test_report = TestCaseRun(
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
    unit_test_report = TestCaseRun(
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
    unit_test_report = TestCaseRun(
        test_name="test_unit_test_report_messages",
        test_asset=test_asset,
        test_logger=logger
    )
    unit_test_report.report(code="skipped.test")
    skipped = unit_test_report.get_skipped()
    assert len(skipped) == 1
    assert "skipped.test" in skipped
