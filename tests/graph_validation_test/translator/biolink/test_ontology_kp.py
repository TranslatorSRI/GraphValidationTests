"""
Unit tests of the Ontology KP
"""
from typing import Optional
from graph_validation_test.utils.ontology_kp import get_parent_concept

import pytest


@pytest.mark.parametrize(
    "curie,category,result",
    [
        (   # Query 0 - chemical compounds are NOT in an ontology hierarchy
            "CHEMBL.COMPOUND:CHEMBL2333026",
            "biolink:SmallMolecule",
            None
        ),
        (   # Query 1 - MONDO disease terms are in an ontology term hierarchy
            "MONDO:0011027",
            "biolink:Disease",
            "MONDO:0015967"
        ),
        (   # Query 2 - HP phenotype terms are in an ontology term hierarchy
            "HP:0040068",  # "Abnormality of limb bone"
            "biolink:PhenotypicFeature",
            "HP:0000924"  # Abnormality of the skeletal system
        )
    ]
)
def test_get_parent_concept(curie: str, category: str, result: Optional[str]):
    # Just use default Biolink Model release for this test
    assert get_parent_concept(curie=curie, category=category, biolink_version=None) == result
