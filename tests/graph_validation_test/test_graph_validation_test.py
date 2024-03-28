"""
Unit tests for pieces of the GraphValidationTests code
"""
from translator_testing_model.datamodel.pydanticmodel import TestAsset
from graph_validation_test import TestCaseRun, GraphValidationTest
from graph_validation_test.utils.unit_test_templates import by_subject, by_object
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


def test_default_graph_validation_test_construction():
    gvt = GraphValidationTest(
        target="https://some-trapi-service.ncats.io",
        test_asset=SAMPLE_TEST_ASSET,
    )
    assert gvt.get_trapi_version() == DEFAULT_TRAPI_VERSION
    assert gvt.get_biolink_version() == DEFAULT_BMT.get_model_version()
    assert not gvt.get_trapi_generators()


def test_explicit_graph_validation_test_construction():
    trapi_generators = [by_subject]
    gvt = GraphValidationTest(
        target="https://some-trapi-service.ncats.io",
        test_asset=SAMPLE_TEST_ASSET,
        trapi_generators=trapi_generators,
        trapi_version="1.4.2",
        biolink_version="4.1.4",
        runner_settings=["Inferred"],
        test_logger=logger
    )
    assert by_subject in gvt.get_trapi_generators()
    assert by_object not in gvt.get_trapi_generators()
    assert gvt.get_trapi_version() == "v1.4.2"
    assert gvt.get_biolink_version() == "4.1.4"
    assert by_subject in gvt.get_trapi_generators()
    assert "Inferred" in gvt.get_runner_settings()
    assert gvt.get_test_logger() == logger


def test_test_case_run_report_messages():
    gvt = GraphValidationTest(
        target="https://some-trapi-service.ncats.io",
        test_asset=SAMPLE_TEST_ASSET,
    )
    tcr = TestCaseRun(
        test_run=gvt,
        test=by_subject
    )
    tcr.report(
        code="error.biolink.model.noncompliance",
        identifier="(a)--[biolink:affects]->(b)",
        biolink_release=DEFAULT_BMT
    )
    tcr.report(code="info.compliant")
    assert len(tcr.get_critical()) == 0
    errors = tcr.get_errors()
    assert len(errors) == 1
    assert "error.biolink.model.noncompliance" in errors
    info = tcr.get_info()
    assert len(info) == 1
    assert "info.compliant" in info
    tcr.report(code="skipped.test", identifier="Non-standards compliant input?")
    skipped = tcr.get_skipped()
    assert len(skipped) == 1
    assert "skipped.test" in skipped
