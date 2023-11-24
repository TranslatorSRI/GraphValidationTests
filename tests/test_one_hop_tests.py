"""
Unit tests for pieces of the OneHopTests code
"""

from one_hop_tests import _generate_test_asset_id, get_test_asset
from translator_testing_model.datamodel.pydanticmodel import ExpectedOutputEnum


def test_generate_test_asset_id():
    assert _generate_test_asset_id() == "TestAsset:00001"
    assert _generate_test_asset_id() == "TestAsset:00002"
    assert _generate_test_asset_id() == "TestAsset:00003"


def test_expected_output_enum():
    expected_output = 'Acceptable'
    assert expected_output in ExpectedOutputEnum.__members__
    not_an_expected_output = 'UnforeseenEvent'
    assert not_an_expected_output not in ExpectedOutputEnum.__members__


def test_get_test_asset():
    input_curie = 'MONDO:0005301'
    relationship = 'treats'
    output_curie = 'PUBCHEM.COMPOUND:107970'
    expected_output = 'Acceptable'
    test_asset = get_test_asset(input_curie, relationship, output_curie, expected_output)
    assert test_asset.id == "TestAsset:00001"
    assert test_asset.input_id == input_curie
    assert test_asset.predicate == relationship
    assert test_asset.output_id == output_curie
    assert test_asset.expected_output == expected_output

#
# TODO: perhaps each OneHop template should be unit tested?
#
# def test_by_subject_template():
#     pass
#
#
# def test_inverse_by_new_subject_template():
#     pass
#
#
# def test_by_object_template():
#     pass
#
#
# def test_raise_subject_entity_template():
#     pass
#
#
# def test_raise_object_entity_template():
#     pass
#
#
# def test_raise_object_by_subject_template():
#     pass
#
#
# def test_raise_predicate_by_subject_template():
#     pass
