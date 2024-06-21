"""
Unit tests for Translator SmartAPI Registry access
"""
from typing import Optional, Dict, List, Tuple, Union
import pytest

from graph_validation_tests.translator.registry import (
    # get_default_url,
    query_smart_api,
    SMARTAPI_QUERY_PARAMETERS,
    tag_value,
    get_the_registry_data,
    # extract_component_test_metadata_from_registry,
    # get_testable_resources_from_registry,
    # get_testable_resource,
    source_of_interest,
    validate_testable_resource,
    live_trapi_endpoint,
    select_endpoint, get_component_endpoint_from_registry,
    # assess_trapi_version
)

import logging
logger = logging.getLogger(__name__)


def test_get_the_registry_data():
    registry_data: Dict = get_the_registry_data()
    assert registry_data


def test_default_empty_query():
    registry_data = query_smart_api()
    assert len(registry_data) > 0, "Default query failed"


_QUERY_SMART_API_EXCEPTION_PREFIX = "Translator SmartAPI Registry Access Exception:"


def test_fake_url():
    registry_data: Dict = query_smart_api(url="fake URL")
    assert registry_data and "Error" in registry_data, "Missing error message?"
    assert registry_data["Error"].startswith(_QUERY_SMART_API_EXCEPTION_PREFIX), "Unexpected error message?"


def test_query_smart_api():
    registry_data = query_smart_api(parameters=SMARTAPI_QUERY_PARAMETERS)
    assert "total" in registry_data, f"\tMissing 'total' tag in results?"
    assert registry_data["total"] > 0, f"\tZero 'total' in results?"
    assert "hits" in registry_data, f"\tMissing 'hits' tag in results?"
    for index, service in enumerate(registry_data['hits']):
        if "info" not in service:
            logger.debug(f"\tMissing 'hits' tag in hit entry? Ignoring entry...")
            continue
        info = service["info"]
        if "title" not in info:
            logger.debug(f"\tMissing 'title' tag in 'hit.info'? Ignoring entry...")
            continue
        title = info["title"]
        logger.debug(f"\n{index} - '{title}':")
        if "x-translator" not in info:
            logger.debug(f"\tMissing 'x-translator' tag in 'hit.info'? Ignoring entry...")
            continue
        x_translator = info["x-translator"]
        if "component" not in x_translator:
            logger.debug(f"\tMissing 'component' tag in 'hit.info.x-translator'? Ignoring entry...")
            continue
        component = x_translator["component"]
        if "x-translator" not in info:
            logger.debug(f"\tMissing 'x-translator' tag in 'hit.info'? Ignoring entry...")
            continue
        x_trapi = info["x-translator"]

        if component == "KP":
            if "test_data_location" not in x_trapi:
                logger.debug(f"\tMissing 'test_data_location' tag in 'hit.info.x-translator'? Ignoring entry...")
                continue
            else:
                test_data_location = x_trapi["test_data_location"]
                logger.debug(f"\t'hit.info.x-translator.test_data_location': '{test_data_location}'")
        else:
            logger.debug(f"\tIs an ARA?")


def test_empty_json_data():
    value = tag_value({}, "testing.one.two.three")
    assert not value


_TEST_JSON_DATA = {
        "testing": {
            "one": {
                "two": {
                    "three": "The End!"
                },

                "another_one": "for_fun"
            }
        }
    }


def test_valid_tag_path():
    value = tag_value(_TEST_JSON_DATA, "testing.one.two.three")
    assert value == "The End!"


def test_empty_tag_path():
    value = tag_value(_TEST_JSON_DATA, "")
    assert not value


def test_missing_intermediate_tag_path():
    value = tag_value(_TEST_JSON_DATA, "testing.one.four.five")
    assert not value


def test_missing_end_tag_path():
    value = tag_value(_TEST_JSON_DATA, "testing.one.two.three.four")
    assert not value


def _wrap_infores(infores: str):
    return {
        "info": {
            "title": "test_source_of_interest",
            "x-translator": {
                    "infores": infores
            }
        }
    }


@pytest.mark.parametrize(
    "query",
    [
        # the <infores> from the Registry is assumed to be non-empty (see usage in main code...)
        # (<infores>, <target_sources>, <boolean return value>)
        (_wrap_infores("infores-object-id"), None, "infores-object-id"),   # Empty <target_sources>
        (_wrap_infores("infores-object-id"), set(), "infores-object-id"),  # Empty <target_sources>

        # single matching element in 'target_source' set
        (_wrap_infores("infores-object-id"), {"infores-object-id"}, "infores-object-id"),

        # match to single prefix wildcard pattern in 'target_source' set
        (_wrap_infores("infores-object-id"), {"infores-*"}, "infores-object-id"),

        # match to single suffix wildcard pattern in 'target_source' set
        (_wrap_infores("infores-object-id"), {"*-object-id"}, "infores-object-id"),

        # match to embedded wildcard pattern in 'target_source' set
        (_wrap_infores("infores-object-id"), {"infores-*-id"}, "infores-object-id"),

        # mismatch to embedded wildcard pattern in 'target_source' set
        (_wrap_infores("infores-object-id"), {"infores-*-ID"}, None),

        # only matches a single embedded wildcard pattern...
        (_wrap_infores("infores-object-id"), {"infores-*-*"}, None),

        # mismatch to single wildcard pattern in 'target_source' set
        (_wrap_infores("infores-object-id"), {"another-*"}, None),
        (
            # exact match to single element in the 'target_source' set
            _wrap_infores("infores-object-id"),
            {
                "another-infores-object-id",
                "infores-object-id",
                "yetanuder-infores-id"
            },
            "infores-object-id"
        ),
        (
            # missing match to single element in the 'target_source' set
            _wrap_infores("infores-object-id"),
            {
                "another-infores-object-id",
                "yetanuder-infores-id"
            },
            None
        ),
        (   # missing match to single wildcard pattern
            # embedded in the 'target_source' set
            _wrap_infores("infores-object-id"),
            {
                "another-infores-object-id",
                "yetanuder-*",
                "some-other-infores-id"
            },
            None
        ),
    ]
)
def test_source_of_interest(query: Tuple):
    assert source_of_interest(service=query[0], target_sources=query[1]) is query[2]


@pytest.mark.parametrize(
    "url,outcome",
    [
        (
            "https://automat.renci.org/hgnc/1.4",
            True
        ),
        (
           "https://fake-url",
           False
        )
    ]
)
# def live_trapi_endpoint(url: str) -> Optional[Dict]
def test_live_trapi_endpoint(url: str, outcome: bool):
    assert (live_trapi_endpoint(url) is not None) is outcome


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


# Current default major.minor TRAPI SemVer version"
DEF_M_M_TRAPI = "1.5"

# Current default major.minor.patch TRAPI SemVer version"
DEF_M_M_P_TRAPI = "1.5.0"

KP_INFORES = "molepro"
KP_TEST_DATA_URL = "https://github.com/broadinstitute/molecular-data-provider/blob/" + \
                   "master/test/data/MolePro-test-data.json"
KP_TEST_DATA_NORMALIZED = "https://raw.githubusercontent.com/broadinstitute/molecular-data-provider/" + \
                          "master/test/data/MolePro-test-data.json"

PRODUCTION_KP_BASEURL = "https://molepro-trapi.transltr.io/molepro/trapi/v"
STAGING_KP_BASEURL = "https://molepro-trapi.ci.transltr.io/molepro/trapi/v"
TESTING_KP_BASEURL = "https://molepro-trapi.test.transltr.io/molepro/trapi/v"
DEVELOPMENT_KP_BASEURL = "https://translator.broadinstitute.org/molepro/trapi/v"

PRODUCTION_KP_SERVER_URL = f"{PRODUCTION_KP_BASEURL}{DEF_M_M_TRAPI}"
PRODUCTION_KP_SERVER = {
    'description': f'KP TRAPI {DEF_M_M_TRAPI} endpoint - production',
    'url': PRODUCTION_KP_SERVER_URL,
    'x-maturity': 'production'
}

STAGING_KP_SERVER_URL = f"{STAGING_KP_BASEURL}{DEF_M_M_TRAPI}"
STAGING_KP_SERVER = {
    'description': f'KP TRAPI {DEF_M_M_TRAPI} endpoint - testing',
    'url': STAGING_KP_SERVER_URL,
    'x-maturity': 'staging'
}

TESTING_KP_SERVER_URL = f"{TESTING_KP_BASEURL}{DEF_M_M_TRAPI}"
TESTING_KP_SERVER = {
    'description': f'KP TRAPI {DEF_M_M_TRAPI} endpoint - staging',
    'url': TESTING_KP_SERVER_URL,
    'x-maturity': 'testing'
}

DEVELOPMENT_KP_SERVER_URL = f"{DEVELOPMENT_KP_BASEURL}{DEF_M_M_TRAPI}"
DEVELOPMENT_KP_SERVER = {
    'description': f'KP TRAPI {DEF_M_M_TRAPI} endpoint - development',
    'url': DEVELOPMENT_KP_SERVER_URL,
    'x-maturity': 'development'
}

KP_SERVERS_BLOCK = [PRODUCTION_KP_SERVER, STAGING_KP_SERVER, TESTING_KP_SERVER, DEVELOPMENT_KP_SERVER]

ARA_INFORES = "biothings-explorer"

PRODUCTION_ARA_SERVER_URL = "https://bte.transltr.io/v1"
PRODUCTION_ARA_SERVER = {
    'description': f'ARA TRAPI {DEF_M_M_TRAPI} endpoint - production',
    'url': PRODUCTION_ARA_SERVER_URL,
    'x-maturity': 'production'
}

TESTING_ARA_SERVER_URL = "https://bte.test.transltr.io/v1"
TESTING_ARA_SERVER = {
    'description': f'ARA TRAPI {DEF_M_M_TRAPI} endpoint - staging',
    'url': TESTING_ARA_SERVER_URL,
    'x-maturity': 'testing'
}

DEVELOPMENT_ARA_SERVER_URL = "https://api.bte.ncats.io/v1"
DEVELOPMENT_ARA_SERVER = {
    'description': f'ARA TRAPI {DEF_M_M_TRAPI} endpoint - development',
    'url': DEVELOPMENT_ARA_SERVER_URL,
    'x-maturity': 'development'
}

ARA_SERVERS_BLOCK = [PRODUCTION_ARA_SERVER, PRODUCTION_ARA_SERVER, TESTING_ARA_SERVER, DEVELOPMENT_ARA_SERVER]


# def validate_testable_resource(
#     index: int,
#     service: Dict,
#     component: str,
#     x_maturity: Optional[str] = None
# ) -> Optional[Dict[str, Union[str, List]]]:
#     """
#     Validates a service as testable and resolves then returns parameters for testing.
#
#     :param index: int, internal sequence number (i.e. hit number in the Translator SmartAPI Registry)
#     :param service: Dict, indexed metadata about a component service (from the Registry)
#     :param component: str, type of component, one of 'KP' or 'ARA'
#     :param x_maturity: Optional[str], 'x_maturity' environment target for test run (system chooses if not specified)
#     :return: augmented resource metadata for a given KP or ARA service confirmed to be accessible for testing
#              for one selected x-maturity environment; None if unavailable
#     """
# validate_testable_resource(index, service, component) -> Optional[Dict[str, Union[str, List, Dict]]]
@pytest.mark.parametrize(
    "index,service,outcome,url,x_maturity",
    [
        (  # query 0 - 'empty' service dictionary
            0,
            dict(),  # service
            False,   # True if expecting that resource_metadata is not None; False otherwise
            "",      # expected 'url'
            None
        ),
        (
            1,
            {  # query 1. missing service 'title' - won't return any resource_metadata
                'info': {
                    # 'title': f'ARA Translator Reasoner - TRAPI {CURRENT_DEFAULT_MAJOR_MINOR_PATCH_TRAPI}',
                    'x-translator': {
                        'infores': f"infores:{ARA_INFORES}",
                    },
                },
                'servers': [DEVELOPMENT_ARA_SERVER]
            },      # service
            False,  # True if expecting that resource_metadata is not None; False otherwise
            "",      # expected 'url'
            None
        ),
        (
            2,
            {  # query 2. missing 'infores' - won't return any resource_metadata
                'info': {
                    'title': f'ARA Translator Reasoner - TRAPI {DEF_M_M_P_TRAPI}',
                    'x-translator': {
                        # 'infores': f"infores:{ARA_INFORES}",
                    },
                },
                'servers': [DEVELOPMENT_ARA_SERVER]
            },      # service
            False,  # True if expecting that resource_metadata is not None; False otherwise
            "",      # expected 'url'
            None
        ),
        (
            3,
            {  # query 3. missing 'servers' block - won't return any resource_metadata
                'info': {
                    'title': f'ARA Translator Reasoner - TRAPI {DEF_M_M_P_TRAPI}',
                    'x-translator': {
                        'infores': f"infores:{ARA_INFORES}",
                    },
                }
            },      # service
            False,  # True if expecting that resource_metadata is not None; False otherwise
            "",      # expected 'url'
            None
        ),
        (
            4,
            {  # query 4. empty 'servers' block - won't return any resource_metadata
                'info': {
                    'title': f'ARA Translator Reasoner - TRAPI {DEF_M_M_P_TRAPI}',
                    'x-translator': {
                        'infores': f"infores:{ARA_INFORES}",
                    },
                },
                'servers': [],
            },      # service
            False,  # True if expecting that resource_metadata is not None; False otherwise
            "",      # expected 'url'
            None
        ),
        (
            5,
            {   # query 5. complete metadata - 'production' endpoint prioritized
                'info': {
                    'title': f'ARA Translator Reasoner - TRAPI {DEF_M_M_P_TRAPI}',
                    'x-translator': {
                        'infores': f"infores:{ARA_INFORES}",
                    },
                },
                'servers': ARA_SERVERS_BLOCK
            },       # service
            True,    # True if expecting that resource_metadata is not None; False otherwise
            PRODUCTION_ARA_SERVER_URL,  # expected 'url' is 'production'
            'production'
        ),
        (
            6,
            {   # query 6. 'testing' endpoint has greatest precedence
                'info': {
                    'title': f'ARA Translator Reasoner - TRAPI {DEF_M_M_P_TRAPI}',
                    'x-translator': {
                        'infores': f"infores:{ARA_INFORES}",
                    },
                },
                'servers': [DEVELOPMENT_ARA_SERVER, TESTING_ARA_SERVER]
            },       # service
            True,    # True if expecting that resource_metadata is not None; False otherwise
            TESTING_ARA_SERVER_URL,  # expected 'url' is 'testing'
            'testing'
        )
    ]
)
def test_validate_testable_resource(index: int, service: Dict, outcome: bool, url: str, x_maturity: str):
    resource_metadata: Optional[Dict[str, Union[str, List]]] = validate_testable_resource(index, service, "ARA")
    if outcome:
        assert 'url' in resource_metadata
        assert url in resource_metadata['url']
        assert x_maturity in resource_metadata['x_maturity']
    else:
        assert not resource_metadata


@pytest.mark.skip(
    reason="These tests often work fine with fresh data, " +
           "but fail later due to changes in online resources"
)
@pytest.mark.parametrize(
    "component,environment,result",
    [
        ("arax", "dev", "https://arax.ncats.io/beta/api/arax/v1.4"),
        ("aragorn", "ci", "https://aragorn.ci.transltr.io/aragorn"),
        ("biothings-explorer", "ci", "https://bte.ci.transltr.io/v1"),
        ("improving-agent", "test", "https://ia.test.transltr.io/api/v1.4/"),
        ("molepro", "ci", "https://molepro-trapi.ci.transltr.io/molepro/trapi/v1.5"),
        ("foobar", "ci", None)
    ]
)
def test_get_component_endpoint_from_registry(
        component: str,
        environment: str,
        result: Optional[str]
):
    registry_data: Dict = get_the_registry_data()
    endpoint: Optional[str] = get_component_endpoint_from_registry(
        registry_data=registry_data,
        infores_id=component,
        environment=environment,
        target_trapi_version=None,
        target_biolink_version=None
    )
    assert endpoint == result


def test_get_bad_environment_component_endpoint_from_registry():
    registry_data: Dict = get_the_registry_data()
    with pytest.raises(AssertionError):
        get_component_endpoint_from_registry(
            registry_data=registry_data,
            infores_id="arax",
            environment="bad-environment",
            target_trapi_version=None,
            target_biolink_version=None
        )
