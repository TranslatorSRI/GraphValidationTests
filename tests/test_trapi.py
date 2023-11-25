"""
Unit tests of the low level TRAPI (ARS, KP & ARA) calling subsystem.
"""
from typing import Optional
import pytest

from one_hop_tests import get_test_asset
from one_hop_tests.trapi import post_query, execute_trapi_lookup
from one_hop_tests.ontology_kp import ONTOLOGY_KP_TRAPI_SERVER, NODE_NORMALIZER_SERVER
from one_hop_tests.unit_test_templates import by_subject

pytest_plugins = ('pytest_asyncio',)


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


@pytest.mark.asyncio
async def test_post_query_to_node_normalization():
    j = {'curies': ['HGNC:12791']}
    result = post_query(url=NODE_NORMALIZER_SERVER, query=j, server="Post Node Normalizer Query")
    assert result
    assert "HGNC:12791" in result
    assert "equivalent_identifiers" in result["HGNC:12791"]
    assert len(result["HGNC:12791"]["equivalent_identifiers"])


@pytest.mark.asyncio
async def test_execute_trapi_lookup():
    url: str = ""  # where do I send this TRAPI test query? The ARS?
    input_curie = 'MONDO:0005301'
    relationship = 'treats'
    output_curie = 'PUBCHEM.COMPOUND:107970'
    expected_output = 'Acceptable'
    test_asset = get_test_asset(input_curie, relationship, output_curie, expected_output)
    report = execute_trapi_lookup(url, test_asset, by_subject)
    pass
