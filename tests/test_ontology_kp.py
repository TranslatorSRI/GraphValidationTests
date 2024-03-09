"""
Unit tests of the Ontology KP
"""
from typing import Optional
from one_hop_test.ontology_kp import get_parent_concept

import pytest


@pytest.mark.parametrize(
    "curie,category,biolink_version,result",
    [
        (   # Query 0 - chemical compounds are NOT in an ontology hierarchy
            "CHEMBL.COMPOUND:CHEMBL2333026",
            "biolink:SmallMolecule",
            "3.5.4",
            None
        ),
        (   # Query 1 - MONDO disease terms are in an ontology term hierarchy
            "MONDO:0011027",
            "biolink:Disease",
            "3.5.4",
            "MONDO:0015967"
        ),
        (   # Query 2 - HP phenotype terms are in an ontology term hierarchy
            "HP:0040068",  # "Abnormality of limb bone"
            "biolink:PhenotypicFeature",
            "3.5.4",
            "HP:0000924"  # Abnormality of the skeletal system
        )
    ]
)
def test_get_parent_concept(curie: str, category: str, biolink_version: str, result: Optional[str]):
    assert get_parent_concept(
        curie=curie,
        category=category,
        biolink_version=biolink_version
    ) == result
