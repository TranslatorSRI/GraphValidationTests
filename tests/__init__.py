from bmt import Toolkit
from reasoner_validator.biolink import get_biolink_model_toolkit
from reasoner_validator.versioning import get_latest_version
import os

TEST_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..")
SCRIPTS_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "scripts")

DEFAULT_TRAPI_VERSION = get_latest_version("1")
DEFAULT_BMT: Toolkit = get_biolink_model_toolkit()
SAMPLE_TEST_INPUT_1 = {
    # One test edge (asset)
    "test_asset_id": "TestAsset_1",
    "subject_id": "DRUGBANK:DB01592",
    "subject_category": "biolink:SmallMolecule",
    "predicate_id": "biolink:has_side_effect",
    "object_id": "MONDO:0011426",
    "object_category": "biolink:Disease",
    #
    #     "environment": environment, # Optional[TestEnvEnum] = None; default: 'TestEnvEnum.ci' if not given
    #     "components": components,  # Optional[str] = None; default: 'ars' if not given
    #     "trapi_version": trapi_version,  # Optional[str] = None; latest community release if not given
    #     "biolink_version": biolink_version,  # Optional[str] = None; current Biolink Toolkit default if not given
    #     "runner_settings": asset.test_runner_settings,  # Optional[List[str]] = None
}
