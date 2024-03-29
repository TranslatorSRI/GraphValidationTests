"""
Unit tests of the low level TRAPI (ARS, KP & ARA) calling subsystem.
"""
from typing import Optional
import pytest

from graph_validation_test.translator.trapi import post_query, get_component_infores
from graph_validation_test.utils.ontology_kp import ONTOLOGY_KP_TRAPI_SERVER, NODE_NORMALIZER_SERVER

pytest_plugins = ('pytest_asyncio',)

TRAPI_TEST_ENDPOINT = "https://molepro-trapi.transltr.io/molepro/trapi/v1.4"


def test_empty_component_infores():
    with pytest.raises(AssertionError):
        assert get_component_infores(component="")


@pytest.mark.parametrize(
    "component,infores",
    [
        ("arax", "infores:arax"),
        ("aragorn", "infores:aragorn"),
        ("bte", "infores:biothings-explorer"),
        ("improving", "infores:improving-agent"),
        ("molepro", "infores:molepro")
    ]
)
def test_get_component_infores(component: str, infores: str):
    assert get_component_infores(component=component) == infores


# GraphValidationTest.target_component_urls(env: str, components: Optional[str] = None) -> List[str]:
def test_target_component_urls():
    pass


@pytest.mark.parametrize(
    "curie,category,result",
    [
        (   # Query 0 - chemical compounds are NOT in ontology hierarchy
            "CHEMBL.COMPOUND:CHEMBL2333026",
            "biolink:SmallMolecule",
            None
        ),
        (   # Query 1 - MONDO disease terms are in an ontology term hierarchy
            "MONDO:0011027",
            "biolink:Disease",
            "MONDO:0015967"
        )
    ]
)
@pytest.mark.asyncio
async def test_post_query_to_ontology_kp(curie: str, category: str, result: Optional[str]):
    query = {
        "message": {
            "query_graph": {
                "nodes": {
                    "a": {
                        "ids": [curie]
                    },
                    "b": {
                        "categories": [category]
                    }
                },
                "edges": {
                    "ab": {
                        "subject": "a",
                        "object": "b",
                        "predicates": ["biolink:subclass_of"]
                    }
                }
            }
        }
    }
    response = post_query(url=ONTOLOGY_KP_TRAPI_SERVER, query=query, server="Post Ontology KP Query")
    assert response


@pytest.mark.parametrize(
    "curie,category",
    [
        # Query 0 - HGNC id
        ("HGNC:12791", "biolink:Gene"),

        # Query 1 - MONDO term
        ("MONDO:0011027", "biolink:Disease"),

        # Query 2 - HP term
        ("HP:0040068", "biolink:PhenotypicFeature")
    ]
)
@pytest.mark.asyncio
async def test_post_query_to_node_normalization(curie: str, category: str):
    j = {'curies': [curie]}
    result = post_query(url=NODE_NORMALIZER_SERVER, query=j, server="Post Node Normalizer Query")
    assert result
    assert curie in result
    assert "equivalent_identifiers" in result[curie]
    assert len(result[curie]["equivalent_identifiers"])
    assert category in result[curie]["type"]


# @pytest.mark.asyncio
# async def test_execute_trapi_lookup():
#     url: str = TRAPI_TEST_ENDPOINT
#     subject_id = 'MONDO:0005301'
#     subject_category = "biolink:Disease"
#     predicate_name = "treats"
#     predicate_id = f"biolink:{predicate_name}"
#     object_id = 'PUBCHEM.COMPOUND:107970'
#     object_category = "biolink:SmallMolecule"
#     oht: OneHopTest = OneHopTest(endpoints=[url])
#     test_asset: TestAsset = oht.build_test_asset(
#         subject_id=subject_id,
#         subject_category=subject_category,
#         predicate_id=predicate_id,
#         object_id=object_id,
#         object_category=object_category
#     )
#     report: UnitTestReport = await run_one_hop_unit_test(
#         url=url,
#         test_asset=test_asset,
#         creator=by_subject,
#         trapi_version="1.4.2",
#         # biolink_version=None
#     )
#     assert report
