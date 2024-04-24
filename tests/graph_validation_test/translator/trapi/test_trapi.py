"""
Unit tests of the low level TRAPI (ARS, KP & ARA) calling subsystem.
"""
from typing import Optional
import pytest

from graph_validation_test.translator.trapi import (
    get_component_infores_object_id,
    resolve_component_endpoint
)
from graph_validation_test.utils.http import post_query
from graph_validation_test.utils.ontology_kp import (
    ONTOLOGY_KP_TRAPI_SERVER,
    NODE_NORMALIZER_SERVER
)

pytest_plugins = ('pytest_asyncio',)

TRAPI_TEST_ENDPOINT = "https://molepro-trapi.transltr.io/molepro/trapi/v1.4"


def test_empty_get_component_infores_object_id():
    with pytest.raises(AssertionError):
        assert get_component_infores_object_id(component="")


@pytest.mark.parametrize(
    "component,infores",
    [
        ("arax", "arax"),
        ("aragorn", "aragorn"),
        ("bte", "biothings-explorer"),
        ("improving", "improving-agent"),
        ("molepro", "molepro")
    ]
)
def test_get_get_component_infores_object_id(component: str, infores: str):
    assert get_component_infores_object_id(component=component) == infores


@pytest.mark.parametrize(
    "component,environment,result",
    [
        (None, None, f"https://ars.ci.transltr.io/ars/api/"),
        ("ars", None, f"https://ars.ci.transltr.io/ars/api/"),
        ("ars", "non-environment", None),
        ("ars", "test", f"https://ars.test.transltr.io/ars/api/"),
        ("arax", "dev", "https://arax.ncats.io/beta/api/arax/v1.4"),
        ("aragorn", "prod", "https://aragorn.transltr.io/aragorn"),
        ("biothings-explorer", "test", "https://bte.test.transltr.io/v1"),
        ("improving-agent", "test", "https://ia.test.transltr.io/api/v1.4/"),
        ("molepro", "ci", "https://molepro-trapi.ci.transltr.io/molepro/trapi/v1.5"),
        ("foobar", "ci", None),
        ("arax", "non-environment", None),
    ]
)
def test_resolve_component_endpoint(
        component: Optional[str],
        environment: Optional[str],
        result: Optional[str]
):
    endpoint: Optional[str] = \
        resolve_component_endpoint(
            component=component,
            environment=environment,
            target_trapi_version=None,
            target_biolink_version=None
        )
    assert endpoint == result


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
