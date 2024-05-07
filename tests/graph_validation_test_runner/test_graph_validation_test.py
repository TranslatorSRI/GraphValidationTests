"""
Unit tests for pieces of the GraphValidationTests code
"""
from typing import List, Dict
from translator_testing_model.datamodel.pydanticmodel import TestAsset
from graph_validation_tests import TestCaseRun, GraphValidationTest
from graph_validation_tests.utils.unit_test_templates import by_subject, by_object
from tests import DEFAULT_TRAPI_VERSION, DEFAULT_BMT

import logging
logger = logging.getLogger(__name__)

TEST_ASSET_1 = {
    "subject_id": "DRUGBANK:DB01592",
    "subject_category": "biolink:SmallMolecule",
    "predicate_id": "biolink:treats",
    "object_id": "MONDO:0011426",
    "object_category": "biolink:Disease"
}

TEST_ASSET_ID = "TestAsset_1"
TEST_SUBJECT_ID = "MONDO:0005301"
TEST_SUBJECT_CATEGORY = "biolink:Disease"
TEST_PREDICATE_NAME = "treats"
TEST_PREDICATE_ID = f"biolink:{TEST_PREDICATE_NAME}"
TEST_OBJECT_ID = "PUBCHEM.COMPOUND:107970"
TEST_OBJECT_CATEGORY = "biolink:SmallMolecule"
SAMPLE_TEST_ASSET: TestAsset = GraphValidationTest.build_test_asset(
    test_asset_id=TEST_ASSET_ID,
    subject_id=TEST_SUBJECT_ID,
    subject_category=TEST_SUBJECT_CATEGORY,
    predicate_id=TEST_PREDICATE_ID,
    object_id=TEST_OBJECT_ID,
    object_category=TEST_OBJECT_CATEGORY
)


def test_build_test_asset():
    assert SAMPLE_TEST_ASSET.id == TEST_ASSET_ID
    assert SAMPLE_TEST_ASSET.input_id == TEST_SUBJECT_ID
    assert SAMPLE_TEST_ASSET.input_category == TEST_SUBJECT_CATEGORY
    assert SAMPLE_TEST_ASSET.predicate_id == TEST_PREDICATE_ID
    assert SAMPLE_TEST_ASSET.predicate_name == TEST_PREDICATE_NAME
    assert SAMPLE_TEST_ASSET.output_id == TEST_OBJECT_ID
    assert SAMPLE_TEST_ASSET.output_category == TEST_OBJECT_CATEGORY
    assert SAMPLE_TEST_ASSET.expected_output is None  # not set?


def test_default_graph_validation_test_construction():
    gvt = GraphValidationTest(
        component="https://some-trapi-service.ncats.io",
        test_asset=SAMPLE_TEST_ASSET,
    )
    assert gvt.get_trapi_version() == DEFAULT_TRAPI_VERSION
    assert gvt.get_biolink_version() == DEFAULT_BMT.get_model_version()
    assert not gvt.get_trapi_generators()


def test_explicit_graph_validation_test_construction():
    trapi_generators = [by_subject]
    gvt = GraphValidationTest(
        component="https://some-trapi-service.ncats.io",
        test_asset=SAMPLE_TEST_ASSET,
        trapi_generators=trapi_generators,
        trapi_version="1.4.2",
        biolink_version="4.1.4",
        runner_settings=["inferred"]
    )
    assert by_subject in gvt.get_trapi_generators()
    assert by_object not in gvt.get_trapi_generators()
    assert gvt.get_trapi_version() == "v1.4.2"
    assert gvt.get_biolink_version() == "4.1.4"
    assert by_subject in gvt.get_trapi_generators()
    assert "inferred" in gvt.get_runner_settings()


def test_test_case_run_report_messages():
    gvt = GraphValidationTest(
        component="https://some-trapi-service.ncats.io",
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


def test_format_results():
    test_asset_id: str = "TestAsset_1"
    test_asset: TestAsset = TestAsset(id=test_asset_id)
    gvt: GraphValidationTest = GraphValidationTest(
        test_asset=test_asset
    )
    tcr_1: TestCaseRun = TestCaseRun(
        test_run=gvt,
        test=by_subject
    )
    tcr_2: TestCaseRun = TestCaseRun(
        test_run=gvt,
        test=by_object
    )
    test_cases: List[TestCaseRun] = [
        tcr_1,
        tcr_2
    ]
    formatted_output: Dict = gvt.format_results(test_cases)
    assert formatted_output
    by_subject_test_case_id: str = f"{test_asset_id}-by_subject"
    assert formatted_output[by_subject_test_case_id]
    by_object_test_case_id: str = f"{test_asset_id}-by_object"
    assert formatted_output[by_object_test_case_id]
    assert "ars" in formatted_output[by_object_test_case_id]
    assert formatted_output[by_object_test_case_id]["ars"]
    assert "status" in formatted_output[by_object_test_case_id]["ars"]
    assert formatted_output[by_object_test_case_id]["ars"]["status"] == "SKIPPED"
    assert not formatted_output[by_object_test_case_id]["ars"]["messages"]
