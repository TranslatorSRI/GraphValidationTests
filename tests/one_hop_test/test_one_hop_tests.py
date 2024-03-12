"""
Unit tests for pieces of the OneHopTests code
"""
from typing import Optional, Dict, List, Tuple
from copy import deepcopy
from deepdiff import DeepDiff
import pytest

from one_hop_test import OneHopTest
from one_hop_test.unit_test_templates import (
    create_one_hop_message,
    swap_qualifiers,
    # by_subject,
    invert_association,
)
from translator_testing_model.datamodel.pydanticmodel import ExpectedOutputEnum, TestAsset


def test_expected_output_enum():
    expected_output = 'Acceptable'
    assert expected_output in ExpectedOutputEnum.__members__
    not_an_expected_output = 'UnforeseenEvent'
    assert not_an_expected_output not in ExpectedOutputEnum.__members__


def test_generate_test_asset_id():
    oht = OneHopTest(endpoints=list())
    assert oht.generate_test_asset_id() == "TestAsset:00001"
    assert oht.generate_test_asset_id() == "TestAsset:00002"
    assert oht.generate_test_asset_id() == "TestAsset:00003"


def test_get_test_asset():
    subject_id = 'MONDO:0005301'
    subject_category = "biolink:Disease"
    predicate_name = "treats"
    predicate_id = f"biolink:{predicate_name}"
    object_id = 'PUBCHEM.COMPOUND:107970'
    object_category = "biolink:SmallMolecule"
    oht = OneHopTest(endpoints=list())
    test_asset: TestAsset = oht.build_test_asset(
        subject_id=subject_id,
        subject_category=subject_category,
        predicate_id=predicate_id,
        object_id=object_id,
        object_category=object_category
    )
    assert test_asset.id == "TestAsset:00001"
    assert test_asset.input_id == subject_id
    assert test_asset.input_category == subject_category
    assert test_asset.predicate_id == predicate_id
    assert test_asset.predicate_name == predicate_name
    assert test_asset.output_id == object_id
    assert test_asset.output_category == object_category
    assert test_asset.expected_output is None  # not set?


TEST_ASSET_1 = {
    "subject_id": "DRUGBANK:DB01592",
    "subject_category": "biolink:SmallMolecule",
    "predicate": "biolink:treats",
    "object_id": "MONDO:0011426",
    "object_category": "biolink:Disease"
}

TEST_TRAPI_TEMPLATE = {
    "message": {
        "query_graph": {
            "nodes": {
                "a": {
                    "categories": ["biolink:SmallMolecule"]
                },
                "b":  {
                    "categories": ["biolink:Disease"]
                },
            },
            "edges": {
                "ab": {
                    "subject": "a",
                    "object": "b",
                    "predicates": ["biolink:treats"]
                }
            }
        },
        "knowledge_graph": {
            "nodes": {}, "edges": {},
        },
        "results": []
    }
}

TEST_TRAPI_LOOKUP_SUBJECT = deepcopy(TEST_TRAPI_TEMPLATE)
TEST_TRAPI_LOOKUP_SUBJECT["message"]["query_graph"]["nodes"]["b"]["ids"] = ["MONDO:0011426"]
TEST_TRAPI_LOOKUP_OBJECT = deepcopy(TEST_TRAPI_TEMPLATE)
TEST_TRAPI_LOOKUP_OBJECT["message"]["query_graph"]["nodes"]["a"]["ids"] = ["DRUGBANK:DB01592"]


#
# create_one_hop_message(edge, look_up_subject: bool = False) -> Tuple[Optional[Dict], str]
@pytest.mark.parametrize(
    "edge,look_up_subject,expected_result",
    [
        (   # Query 0
            {},
            False,
            (None, "Missing edge parameters!")
        ),
        (   # Query 1 - Lookup up subject
            TEST_ASSET_1,
            True,
            (
                TEST_TRAPI_LOOKUP_SUBJECT,
                ""
            )
        ),
        (   # Query 2 - Look up object
            TEST_ASSET_1,
            False,
            (
                TEST_TRAPI_LOOKUP_OBJECT,
                ""
            )
        )
    ]
)
def test_create_one_hop_message(edge: Dict, look_up_subject: bool, expected_result: Tuple[Optional[Dict], str]):
    result = create_one_hop_message(edge, look_up_subject)
    assert not DeepDiff(result[0], expected_result[0])
    assert result[1] == expected_result[1]


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
# @pytest.mark.parametrize(
#     "query,expected_result",
#     [
#         (  # Query 0
#             None,
#             (None, "", "")
#         ),
#         (  # Query 1
#
#             None,
#             (None, "", "")
#         )
#     ]
# )
# def test_by_input_template(query, expected_result: Tuple[Optional[Dict], str, str]):
#     result = by_subject(query)
#     assert result == expected_result


# by_subject(request) -> Tuple[Optional[Dict], str, str]
# @pytest.mark.parametrize(
#     "query,expected_result",
#     [
#         (  # Query 0
#             None,
#             (None, "", "")
#         ),
#         (  # Query 1
#             None,
#             (None, "", "")
#         )
#     ]
# )
# def test_inverse_by_new_input_template(query, expected_result: Tuple[Optional[Dict], str, str]):
#     pass


# by_object(request) -> Tuple[Optional[Dict], str, str]
@pytest.mark.parametrize(
    "query,expected_result",
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
def test_inverse_by_new_output_template(query, expected_result: Tuple[Optional[Dict], str, str]):
    pass


@pytest.mark.parametrize(
    "query,expected_result",
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
def test_raise_input_entity_template(query, expected_result: Tuple[Optional[Dict], str, str]):
    pass


@pytest.mark.parametrize(
    "query,expected_result",
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
def test_raise_output_entity_template(query, expected_result: Tuple[Optional[Dict], str, str]):
    pass


@pytest.mark.parametrize(
    "query,expected_result",
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
def test_raise_output_by_input_template(query, expected_result: Tuple[Optional[Dict], str, str]):
    pass


@pytest.mark.parametrize(
    "query,expected_result",
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
def test_raise_predicate_by_input_template(query, expected_result: Tuple[Optional[Dict], str, str]):
    pass
