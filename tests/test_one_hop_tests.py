"""
Unit tests for pieces of the OneHopTests code
"""
from typing import Optional, Dict, List, Tuple
import pytest

from one_hop_tests import generate_test_asset_id, build_test_asset
from one_hop_tests.unit_test_templates import (
    create_one_hop_message,
    swap_qualifiers, by_subject, invert_association,
)
from translator_testing_model.datamodel.pydanticmodel import ExpectedOutputEnum, TestAsset


def test_expected_output_enum():
    expected_output = 'Acceptable'
    assert expected_output in ExpectedOutputEnum.__members__
    not_an_expected_output = 'UnforeseenEvent'
    assert not_an_expected_output not in ExpectedOutputEnum.__members__


def test_generate_test_asset_id():
    assert generate_test_asset_id() == "TestAsset:00001"
    assert generate_test_asset_id() == "TestAsset:00002"
    assert generate_test_asset_id() == "TestAsset:00003"


def test_get_test_asset():
    input_curie = 'MONDO:0005301'
    relationship = 'treats'
    output_curie = 'PUBCHEM.COMPOUND:107970'
    expected_output = 'Acceptable'
    test_asset: TestAsset = build_test_asset(input_curie, relationship, output_curie, expected_output)
    assert test_asset.id == "TestAsset:00004"
    assert test_asset.input_id == input_curie
    assert test_asset.predicate_name == relationship
    assert test_asset.output_id == output_curie
    assert test_asset.expected_output == expected_output


#
# create_one_hop_message(edge, look_up_subject: bool = False) -> Tuple[Optional[Dict], str]
@pytest.mark.parametrize(
    "edge,lookup_subject,expected_result",
    [
        (   # Query 0
            {},
            False,
            (None, "")
        ),
        (   # Query 1
            {},
            False,
            (None, "")
        )
    ]
)
def create_one_hop_message(edge: Dict, look_up_subject: bool, expected_result: Tuple[Optional[Dict], str]):
    result = create_one_hop_message(edge, look_up_subject)


# swap_qualifiers(qualifiers: List[Dict[str, str]]) -> List[Dict[str, str]]
#
@pytest.mark.parametrize(
    "qualifiers,expected_result",
    [
        (   # Query 0
            [],
            []
        ),
        (   # Query 1
            [],
            []
        )
    ]
)
def test_swap_qualifiers(qualifiers: List[Dict[str, str]], expected_result: List[Dict[str, str]]):
    result = swap_qualifiers(qualifiers)


@pytest.mark.parametrize(
    "association,expected_result",
    [
        (   # Query 0
            "",
            ""
        ),
        (   # Query 1
            "",
            ""
        )
    ]
)
def test_invert_association(association: str, expected_result: str):
    result = invert_association(association)


# by_subject(request) -> Tuple[Optional[Dict], str, str]
@pytest.mark.parametrize(
    "input,expected_result",
    [
        (  # Query 0
            None,
            (None, "", "")
        ),
        (  # Query 1

            None,
            (None, "", "")
        )
    ]
)
def test_by_subject_template(input, expected_result: Tuple[Optional[Dict], str, str]):
    result = by_subject(input)


# by_subject(request) -> Tuple[Optional[Dict], str, str]
@pytest.mark.parametrize(
    "input,expected_result",
    [
        (  # Query 0
            None,
            (None, "", "")
        ),
        (  # Query 1
            None,
            (None, "", "")
        )
    ]
)
def test_inverse_by_new_subject_template(input, expected_result: Tuple[Optional[Dict], str, str]):
    pass


# by_object(request) -> Tuple[Optional[Dict], str, str]
@pytest.mark.parametrize(
    "input,expected_result",
    [
        (  # Query 0
            None,
            (None, "", "")
        ),
        (  # Query 1
            None,
            (None, "", "")
        )
    ]
)
def test_inverse_by_new_object_template(input, expected_result: Tuple[Optional[Dict], str, str]):
    pass


@pytest.mark.parametrize(
    "input,expected_result",
    [
        (  # Query 0
            None,
            (None, "", "")
        ),
        (  # Query 1
            None,
            (None, "", "")
        )
    ]
)
def test_raise_subject_entity_template(input, expected_result: Tuple[Optional[Dict], str, str]):
    pass


@pytest.mark.parametrize(
    "input,expected_result",
    [
        (  # Query 0
            None,
            (None, "", "")
        ),
        (  # Query 1
            None,
            (None, "", "")
        )
    ]
)
def test_raise_object_entity_template(input, expected_result: Tuple[Optional[Dict], str, str]):
    pass


@pytest.mark.parametrize(
    "input,expected_result",
    [
        (  # Query 0
            None,
            (None, "", "")
        ),
        (  # Query 1
            None,
            (None, "", "")
        )
    ]
)
def test_raise_object_by_subject_template(input, expected_result: Tuple[Optional[Dict], str, str]):
    pass


@pytest.mark.parametrize(
    "input,expected_result",
    [
        (  # Query 0
            None,
            (None, "", "")
        ),
        (  # Query 1
            None,
            (None, "", "")
        )
    ]
)
def test_raise_predicate_by_subject_template(input, expected_result: Tuple[Optional[Dict], str, str]):
    pass
