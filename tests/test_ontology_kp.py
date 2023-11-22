"""
Unit tests of the Ontology KP
"""

from one_hop_tests.ontology_kp import get_parent_concept

import pytest


@pytest.mark.asyncio
async def test_post_bad_query():
    get_parent_concept('PUBCHEM.COMPOUND:208898', 'biolink:SmallMolecule', biolink_version="2.2.0")
    get_parent_concept('DRUGBANK:DB00394', 'biolink:SmallMolecule', biolink_version="2.2.0")
    get_parent_concept('CHEMBL.COMPOUND:CHEMBL2333026', 'biolink:SmallMolecule', biolink_version="2.2.0")
