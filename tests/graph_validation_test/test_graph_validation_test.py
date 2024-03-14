"""
Unit tests for pieces of the GraphValidationTests code
"""
from graph_validation_test import GraphValidationTest
from translator_testing_model.datamodel.pydanticmodel import ExpectedOutputEnum, TestAsset
from tests import DEFAULT_TRAPI_VERSION, DEFAULT_BMT


def test_expected_output_enum():
    expected_output = 'Acceptable'
    assert expected_output in ExpectedOutputEnum.__members__
    not_an_expected_output = 'UnforeseenEvent'
    assert not_an_expected_output not in ExpectedOutputEnum.__members__


def test_generate_test_asset_id():
    assert GraphValidationTest.generate_test_asset_id() == "TestAsset:00001"
    assert GraphValidationTest.generate_test_asset_id() == "TestAsset:00002"
    assert GraphValidationTest.generate_test_asset_id() == "TestAsset:00003"


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


def test_get_test_asset():
    assert SAMPLE_TEST_ASSET.id == "TestAsset:00004"
    assert SAMPLE_TEST_ASSET.input_id == TEST_SUBJECT_ID
    assert SAMPLE_TEST_ASSET.input_category == TEST_OBJECT_CATEGORY
    assert SAMPLE_TEST_ASSET.predicate_id == TEST_PREDICATE_ID
    assert SAMPLE_TEST_ASSET.predicate_name == TEST_PREDICATE_NAME
    assert SAMPLE_TEST_ASSET.output_id == TEST_OBJECT_ID
    assert SAMPLE_TEST_ASSET.output_category == TEST_OBJECT_CATEGORY
    assert SAMPLE_TEST_ASSET.expected_output is None  # not set?


def test_default_graph_validation_test_construction():
    gvt: GraphValidationTest = GraphValidationTest(
        endpoints=list(),
        test_name="test_default_graph_validation_test_construction",
        test_asset=SAMPLE_TEST_ASSET,
        runner_settings=["Inferred"]
    )
    assert gvt.get_trapi_version() == DEFAULT_TRAPI_VERSION
    assert gvt.get_biolink_version() == DEFAULT_BMT.get_model_version()
    assert gvt.get_runner_settings()

