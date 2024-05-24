from bmt import Toolkit
from reasoner_validator.biolink import get_biolink_model_toolkit
from reasoner_validator.versioning import get_latest_version
import os

TEST_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..")
SCRIPTS_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "scripts")

DEFAULT_TRAPI_VERSION = get_latest_version("1")
DEFAULT_BMT: Toolkit = get_biolink_model_toolkit()
SAMPLE_MOLEPRO_INPUT_DATA = {
    # One test edge (asset)
    "test_asset_id": "TestAsset_1",
    "subject_id": "CHEBI:16796",   # Melatonin
    "subject_category": "biolink:ChemicalEntity",
    "predicate_id": "biolink:treats",
    "object_id": "MONDO:0005258",  # Autism
    "object_category": "biolink:Disease",
    #
    #     "environment": environment, # Optional[TestEnvEnum] = None; default: 'TestEnvEnum.ci' if not given
    #     "components": components,  # Optional[str] = None; default: 'ars' if not given
    #     "trapi_version": trapi_version,  # Optional[str] = None; latest community release if not given
    #     "biolink_version": biolink_version,  # Optional[str] = None; current Biolink Toolkit default if not given
    #     "runner_settings": asset.test_runner_settings,  # Optional[List[str]] = None
}

SAMPLE_ARAX_INPUT_DATA = {
    "test_asset_id": "TestAsset_2",
    "subject_id": "PUBCHEM.COMPOUND:2801",  # Clomipramine
    "subject_category": "biolink:ChemicalEntity",
    "predicate_id": "biolink:treats",
    "object_id": "ORPHANET:33110",  # Autosomal agammaglobulinemia?
    "object_category": "biolink:Disease",
}

SAMPLE_ARAGORN_INPUT_DATA = {
    "test_asset_id": "TestAsset_3",
    "subject_id": "PUBCHEM.COMPOUND:2801",  # Clomipramine
    "subject_category": "biolink:ChemicalEntity",
    "predicate_id": "biolink:treats",
    "object_id": "ORPHANET:251636",  # Ependymoma
    "object_category": "biolink:Disease"
}

SAMPLE_JOINT_MOLEPRO_ARAX_INPUT_DATA = {
    "test_asset_id": "TestAsset_4",
    "subject_id": "PUBCHEM.COMPOUND:2733526",  # Tamoxifen
    "subject_category": "biolink:ChemicalEntity",
    "predicate_id": "biolink:affects",
    "object_id": "NCBIGene:843632",  # PS2 inorganic pyrophosphatase 1
    "object_category": "biolink:Gene"
}
