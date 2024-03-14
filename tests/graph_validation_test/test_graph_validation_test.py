"""
Unit tests for pieces of the GraphValidationTests code
"""
from graph_validation_test import GraphValidationTest
from translator_testing_model.datamodel.pydanticmodel import ExpectedOutputEnum, TestAsset


def test_expected_output_enum():
    expected_output = 'Acceptable'
    assert expected_output in ExpectedOutputEnum.__members__
    not_an_expected_output = 'UnforeseenEvent'
    assert not_an_expected_output not in ExpectedOutputEnum.__members__


def test_generate_test_asset_id():
    assert GraphValidationTest.generate_test_asset_id() == "TestAsset:00001"
    assert GraphValidationTest.generate_test_asset_id() == "TestAsset:00002"
    assert GraphValidationTest.generate_test_asset_id() == "TestAsset:00003"


def test_get_test_asset():
    subject_id = 'MONDO:0005301'
    subject_category = "biolink:Disease"
    predicate_name = "treats"
    predicate_id = f"biolink:{predicate_name}"
    object_id = 'PUBCHEM.COMPOUND:107970'
    object_category = "biolink:SmallMolecule"
    test_asset: TestAsset = GraphValidationTest.build_test_asset(
        subject_id=subject_id,
        subject_category=subject_category,
        predicate_id=predicate_id,
        object_id=object_id,
        object_category=object_category
    )
    assert test_asset.id == "TestAsset:00004"
    assert test_asset.input_id == subject_id
    assert test_asset.input_category == subject_category
    assert test_asset.predicate_id == predicate_id
    assert test_asset.predicate_name == predicate_name
    assert test_asset.output_id == object_id
    assert test_asset.output_category == object_category
    assert test_asset.expected_output is None  # not set?
