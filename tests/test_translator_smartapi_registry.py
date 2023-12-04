"""
Unit tests for Translator SmartAPI Registry access
"""
from typing import Optional, Dict, List, Tuple
import pytest

from one_hop_tests.translator.registry import (
    # MOCK_REGISTRY,
    # get_default_url,
    # rewrite_github_url,
    query_smart_api,
    SMARTAPI_QUERY_PARAMETERS,
    # tag_value,
    get_the_registry_data,
    # extract_component_test_metadata_from_registry,
    # get_testable_resources_from_registry,
    # get_testable_resource,
    # source_of_interest,
    # validate_testable_resource,
    # live_trapi_endpoint,
    select_endpoint,
    # assess_trapi_version
)


def test_get_one_specific_target_kp():
    registry_data: Dict = get_the_registry_data()
    assert registry_data


# def select_endpoint(
#         server_urls: Dict[str, List[str]],
#         check_access: bool = True
# ) -> Optional[Tuple[str, str]]
@pytest.mark.parametrize(
    "server_urls,endpoint",
    [
        (
            {
                "production": ["https://automat.renci.org/hgnc/1.4"]
            },
            (
                "https://automat.renci.org/hgnc/1.4", "production"
            )
        ),
        (
            {
                "testing": ["https://automat.renci.org/hgnc/1.4"],
                "production": ["https://automat.renci.org/hgnc/1.4"]
            },
            (
                "https://automat.renci.org/hgnc/1.4", "production"
            )
        ),
        (
            {
                "testing": [
                    "https://automat.renci.org/hgnc/1.4",
                    "https://automat.renci.org/hmdb/1.4"
                ]
            },
            (
                "https://automat.renci.org/hgnc/1.4", "testing"
            )
        ),
        (
            {
                "development": [
                    "https://fake-endpoint",
                    "https://automat.renci.org/hmdb/1.4"
                ]
            },
            (
                "https://automat.renci.org/hmdb/1.4", "development"
            )
        ),
        (
            {
                "development": ["https://fake-endpoint"]
            },
            None
        ),
        (
            {
                "testing": ["https://automat.renci.org/hmdb/1.4"],
                "production": ["https://fake-endpoint"]
            },
            (
                "https://automat.renci.org/hmdb/1.4", "testing"
            )
        )
    ]
)
def test_select_endpoint(server_urls: Dict[str, List[str]], endpoint: Optional[Tuple[str, str]]):
    assert select_endpoint(server_urls) == endpoint
