"""
Unit tests of the low level TRAPI (ARS, KP & ARA) calling subsystem.
"""

from one_hop_tests.trapi import post_query
from one_hop_tests.ontology_kp import ONTOLOGY_KP_TRAPI_SERVER, NODE_NORMALIZER_SERVER

import pytest

pytest_plugins = ('pytest_asyncio',)


@pytest.mark.asyncio
async def test_post_good_query():
    post_query(url="", query={}, params=None, server="Post Good Query")


@pytest.mark.asyncio
async def test_post_bad_query():
    post_query(url="", query={}, params=None, server="Post Bad Query")


@pytest.mark.asyncio
async def test_ontology_kp():
    post_query(url=ONTOLOGY_KP_TRAPI_SERVER, query={}, params=None, server="Post Ontology KP Query")


@pytest.mark.asyncio
async def test_node_normalization():
    j = {'curies': ['HGNC:12791']}
    result = post_query(url=NODE_NORMALIZER_SERVER, query=j, server="Post Node Normalizer Query")
    assert result
    assert "HGNC:12791" in result
    assert "equivalent_identifiers" in result["HGNC:12791"]
    assert len(result["HGNC:12791"]["equivalent_identifiers"])
