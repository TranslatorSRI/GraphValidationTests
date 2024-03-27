from bmt import Toolkit
from reasoner_validator.biolink import get_biolink_model_toolkit
from reasoner_validator.versioning import get_latest_version

DEFAULT_TRAPI_VERSION = get_latest_version("1")
DEFAULT_BMT: Toolkit = get_biolink_model_toolkit()
