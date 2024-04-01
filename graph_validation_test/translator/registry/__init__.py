"""
Translator SmartAPI Registry access  module
"""
from typing import Optional, Union, Dict, List, Set, NamedTuple, Tuple
from functools import lru_cache

import requests
from requests.exceptions import RequestException

from reasoner_validator.versioning import SemVer, get_latest_version
from reasoner_validator.biolink import Toolkit

import logging
logger = logging.getLogger(__name__)

LATEST_TRAPI_VERSION = get_latest_version("1")
MINIMUM_BIOLINK_VERSION = "4.1.4"

# We pragmatically assume that the 'latest' is
# Biolink Model Toolkit version of the model
LATEST_BIOLINK_VERSION = Toolkit().get_model_version()

SMARTAPI_URL = "https://smart-api.info/api/"
SMARTAPI_QUERY_PARAMETERS = "q=__all__&tags=%22trapi%22&" + \
                            "fields=servers,info,_meta,_status,paths,tags,openapi,swagger&size=1000&from=0"

# Singleton reading of the Registry Data
# (do I need to periodically refresh it in long-running applications?)
_the_registry_data: Optional[Dict] = None


def query_smart_api(url: str = SMARTAPI_URL, parameters: Optional[str] = None) -> Optional[Dict]:
    """
    Retrieve Translator SmartAPI Metadata for a specified query parameter filter.

    :param url: str, base URL for Translator SmartAPI Registry
    :param parameters: Optional[str], string of query parameters for Translator SmartAPI Registry
    :return: dict, catalog of Translator SmartAPI Metadata indexed by "test_data_location" source.
    """
    # ... if not faking it, access the real thing...
    query_string = f"query?{parameters}" if parameters else "query"
    data: Optional[Dict] = None
    try:
        request = requests.get(f"{url}{query_string}")
        if request.status_code == 200:
            data = request.json()
    except RequestException as re:
        print(re)
        data = {"Error": "Translator SmartAPI Registry Access Exception: "+str(re)}
    return data


def get_the_registry_data(refresh: bool = False) -> Dict:
    global _the_registry_data
    if not _the_registry_data or refresh:
        _the_registry_data = query_smart_api(parameters=SMARTAPI_QUERY_PARAMETERS)
    return _the_registry_data


#########################################
# Legacy SRI_Testing
# Translator SmartAPI Registry
# accessing code - perhaps deprecated
# in the GraphValidationTest project
#########################################

def get_nested_tag_value(data: Dict, path: List[str], pos: int) -> Optional[str]:
    """
    Navigate dot delimited tag 'path' into a multi-level dictionary, to return its associated value.

    :param data: Dict, multi-level data dictionary
    :param path: str, dotted JSON tag path
    :param pos: int, zero-based current position in tag path
    :return: string value of the multi-level tag, if available; 'None' otherwise if no tag value found in the path
    """
    tag = path[pos]
    part_tag_path = ".".join(path[:pos+1])
    if tag not in data:
        logger.debug(f"\tMissing tag path '{part_tag_path}'?")
        return None
    pos += 1
    if pos == len(path):
        return data[tag]
    else:
        return get_nested_tag_value(data[tag], path, pos)


def tag_value(json_data, tag_path) -> Optional[str]:
    """

    :param json_data:
    :param tag_path:
    :return:
    """
    if not tag_path:
        logger.debug(f"\tEmpty 'tag_path' argument?")
        return None

    parts = tag_path.split(".")
    return get_nested_tag_value(json_data, parts, 0)


def source_of_interest(service: Dict, target_sources: Set[str]) -> Optional[str]:
    """
    Source filtering function, checking a source identifier against a set of identifiers.
    The target_source strings may also be wildcard patterns with a single asterix (only)
    with possible prefix only, suffix only or prefix-<body>-suffix matches.

    :param service: Dict, Translator SmartAPI Registry entry for one service 'hit' containing an 'infores' property
    :param target_sources: Set[str], of target identifiers or wildcard patterns of interest
                           against which to filter service infores reference identifiers
    :return: Optional[str], infores if matched; None otherwise.
    """
    assert service, "registry.source_of_interest() method call: unexpected empty service?!?"

    infores = tag_value(service, "info.x-translator.infores")

    # Internally, within SRI Testing, we only track the object_id of the infores CURIE
    infores = infores.replace("infores:", "") if infores else None

    if not infores:
        service_title = tag_value(service, "info.title")
        logger.warning(f"Registry entry for '{str(service_title)}' has no 'infores' identifier. Skipping?")
        return None

    if target_sources:
        found: bool = False
        for entry in target_sources:

            if entry.find("*") >= 0:
                part = entry.split(sep="*", maxsplit=1)  # part should be a 2-tuple
                if not part[0] or infores.startswith(part[0]):
                    if not part[1] or infores.endswith(part[1]):
                        found = True
                        break

            elif infores == entry:  # exact match?
                found = True
                break

        if not found:
            return None

    # default if no target_sources or matching
    return infores


def assess_trapi_version(
        infores: str,
        service_version: str,
        target_version: Optional[str],
        selected_service_trapi_version: Dict[str, str]
):
    """
    Among the set of service entry releases returned, select and return the 'best' TRAPI version for use in testing.

    If the 'trapi_version' argument IS set (i.e. is not 'None'), then use that version as the 'target' TRAPI release.

    Note: that doesn't mean that the specified release actually exists, but just that it will be used to guide
    the filtering process for the selection of the best service TRAPI version, in order of precedence, as follows:

    1. If the service TRAPI version of the service is an exact or compatible match to a requested TRAPI version.
       (i.e. 1.4.0-beta is compatible to a 1.4.0 target), then select it as a candidate.
    2. If the 'trapi_version' argument IS NOT set (i.e. is 'None'), then select it as a candidate.
    3. If the service version is a candidate, record it if it is the latest encountered version; otherwise, ignore it.

    :param infores: str, infores of the observed service
    :param service_version: str, currently observed service (SemVer) version
    :param target_version: str, desired (SemVer) version
    :param selected_service_trapi_version: Dict, catalog of selected (SemVer) versions, indexed by service infores
    :return:
    """
    candidate_version: Optional[str] = None
    if target_version is not None:
        # 1. If the service TRAPI version of the service is an exact or compatible match
        #    to the major, minor level of the requested TRAPI version.
        #    (i.e. '1.4.1-beta' would be compatible to a '1.4.0' target), then select it.
        if SemVer.from_string(target_version, core_fields=['major', 'minor'], ext_fields=[]) \
                == SemVer.from_string(service_version, core_fields=['major', 'minor'], ext_fields=[]):
            candidate_version = service_version
    else:
        # 2. If the 'target_version' argument IS NOT set (i.e. is 'None'),
        #    then select the specified service version as a candidate
        candidate_version = service_version

    if candidate_version is not None:
        if infores not in selected_service_trapi_version or \
                SemVer.from_string(candidate_version) >= SemVer.from_string(selected_service_trapi_version[infores]):
            selected_service_trapi_version[infores] = candidate_version


class RegistryEntryId(NamedTuple):
    service_title: str
    service_version: str
    trapi_version: str
    biolink_version: str
    x_maturity: str


# here, we track Registry duplications of KP and ARA services
_service_catalog: Dict[str, List[RegistryEntryId]] = dict()

# Some ARA's and KP's may be tagged tp be ignored for practical reasons
_ignored_resources: Set[str] = {
    "empty",
    # "rtx-kg2",  # the test_data_location released for RTX-KG2 is relatively unusable, as of September 2022
    # "molepro",  # TODO: temporarily skip MolePro...
    # "arax",     # temporarily skip ARAX ARA
    # "sri-reference-kg",
    # "automat-icees-kg",
    # "cohd",
    # "service-provider-translator",
}


@lru_cache()
def live_trapi_endpoint(url: str) -> Optional[Dict]:
    """
    Checks if TRAPI endpoint is accessible.
    Current implementation performs a GET on the
    TRAPI /meta_knowledge_graph endpoint,
    to verify that a resource is 'alive'

    :param url: str, URL of TRAPI endpoint to be checked
    :return: Optional[Dict], Returns a Python dictionary version of the /meta_knowledge_graph
                             JSON output if the endpoint is 'alive'; 'None' otherwise.
    """
    if not url:
        return None

    # We initially only tested TRAPI endpoints by a simple 'GET'
    # to its '/meta_knowledge_graph' endpoint.
    #
    # However, not all ARA's implement this (less meaningful for ARA's?)
    #
    # Chris Bizon instead suggested use of the fake query
    # '/asyncquery_status/abcdefg' which all TRAPI endpoints should implement,
    # and which returns http status '200' even though the query itself 'fails'.
    #
    # It turns out that Translator components don't uniformly support that;
    # However, it is likely that all Translator components support one or the other
    #
    # Thus, for now, we will test both, to get evidence for a "live" endpoint
    testing_endpoints: List[str] = ["meta_knowledge_graph", "asyncquery_status/abcdefg"]
    for endpoint in testing_endpoints:
        test_url: str = f"{url}/{endpoint}"
        try:
            request = requests.get(test_url)
            if request.status_code == 200:
                # Success! given url is deemed a 'live' TRAPI endpoint
                # TODO: since we are accessing this endpoint now, perhaps we can
                #       harvest some of its metadata here, for validation purposes?
                data: Optional[Dict] = request.json()
                return data
            else:
                logger.warning(
                    f"live_trapi_endpoint(): TRAPI endpoint '{test_url}' is inaccessible? " +
                    f"Status code: {request.status_code}?"
                )
        except RequestException as re:
            logger.warning(f"live_trapi_endpoint(): requests.get() exception {str(re)}?")
    return None


def capture_kg_metadata(endpoint: str, data: Dict):
    """
    Parses and caches useful metadata from a specified TRAPI endpoint.
    :param endpoint: str, TRAPI endpoint
    :param data: Dict, JSON output from the /meta_knowledge_graph
    :return: ??
    """
    # TODO: IMPLEMENT ME!
    pass


def capture_tag_value(service_metadata: Dict, resource: str, tag: str, value: str):
    """

    :param service_metadata:
    :param resource:
    :param tag:
    :param value:
    """
    if value:
        logger.info(f"\t{resource} '{tag}': {value}")
        service_metadata[resource][tag] = value
    else:
        logger.warning(f"\t{resource} is missing its service '{tag}'")
        service_metadata[resource][tag] = None


# TODO: this is an ordered list giving 'production' testing priority
#       but not sure about preferred testing priority.
#       See https://github.com/TranslatorSRI/SRI_testing/issues/61 and also
#           https://github.com/TranslatorSRI/SRI_testing/issues/59
DEPLOYMENT_TYPES: List[str] = ['production', 'staging', 'testing', 'development']
DEPLOYMENT_TYPE_MAP: Dict[str, str] = {
    "prod": "production",
    "ci": "staging",  # TODO: is this correct?
    "test": "testing",
    "dev": "development"
}


def validate_servers(
        infores: str,
        service: Dict,
        x_maturity: Optional[str] = None
) -> Optional[Dict[str, List[str]]]:
    """
    Validate the servers block, returning it or None if unavailable.

    :param infores: str, InfoRes reference id of the service
    :param service: Dict, service metadata (from Registry)
    :param x_maturity: Optional[str], target x-maturity (if set; may be None if not unconstrained)
    :return: Dict, catalog of x-maturity environment servers; None if unavailable.
    """
    servers: Optional[List[Dict]] = service['servers']

    if not servers:
        logger.warning(f"Registry entry '{infores}' missing a 'servers' block? Skipping...")
        return None

    server_urls: Dict = dict()
    for server in servers:
        if not (
                'url' in server and
                'x-maturity' in server and
                server['x-maturity'] in DEPLOYMENT_TYPES
        ):
            # sanity check!
            continue

        environment = server['x-maturity']

        # Design decisions emerging out of 29 November 2022 Translator Architecture meeting:

        # 1. Check here for explicitly specified 'x_maturity'; otherwise, iterate to select...
        if x_maturity and environment != x_maturity.lower():
            continue

        # 2. Discussions confirmed that if multiple x-maturity urls are present, then they are all
        #    'functionally identical'; however, they may not all be operational.  We will thus now  keep a list of
        #    such endpoints around then iterate through then when issuing TRAPI calls, in case that some are offline?
        env_endpoint = server['url']
        if environment not in server_urls:
            # first url seen for a given for a given x-maturity
            server_urls[environment] = list()

        logger.info(
            f"Registry entry '{infores}' x-maturity '{environment}' includes  url '{env_endpoint}'."
        )
        server_urls[environment].append(env_endpoint)

    return server_urls


def select_accessible_endpoint(urls: Optional[List[str]], check_access: bool) -> Optional[str]:
    url: Optional[str] = None
    for endpoint in urls:
        if not check_access:
            # May be set for testing purposes
            url = endpoint
            break
        else:
            # Since they are all deemed 'functionally equivalent' by the Translator team, the first
            # 'live' endpoint, within the given x-maturity set, is selected as usable for testing.
            data: Optional[Dict] = live_trapi_endpoint(endpoint)
            if data is not None:
                url = endpoint
                capture_kg_metadata(url, data)
                break
    return url


def select_endpoint(
        server_urls: Dict[str, List[str]],
        check_access: bool = True
) -> Optional[Tuple[str, str]]:
    # This is a revised version of the SRI_Testing harness endpoint
    # selector which is agnostic about test_data_location
    """
    Select one test URL based on active endpoints from available 'server_urls'.
    Usually, by the time this method is called, any 'x_maturity' preference
    has constrained the 'server_urls'. If the 'server_urls' have several 'x_maturity'
    environments, the highest precedence x_maturity  is taken.
    The precedence is in order of: 'production', 'staging', 'testing' and 'development'
    (this could change in the future, based on Translator community deliberations...).

    :param server_urls: Dict, the indexed catalog of available
                              Translator SmartAPI Registry entry 'servers' block urls
    :param check_access: bool, verify TRAPI access of endpoints before returning (Default: True)

    :return: Optional[Tuple[str, str]], selected URL endpoint, 'x-maturity' tag
    """
    # Check available environments from the order of the DEPLOYMENT_TYPES list
    for x_maturity in DEPLOYMENT_TYPES:
        if x_maturity in server_urls:
            urls = server_urls[x_maturity]
            url: Optional[str] = select_accessible_endpoint(urls, check_access)
            if url is not None:
                # Return selected endpoint, fully resolved
                # with associated available test data
                return url, x_maturity

    # default is failure
    return None


def validate_testable_resource(
        index: int,
        service: Dict,
        component: str,
        x_maturity: Optional[str] = None
) -> Optional[Dict[str, Union[str, List]]]:
    """
    Validates a service as testable and resolves then returns parameters for testing.

    :param index: int, internal sequence number (i.e. hit number in the Translator SmartAPI Registry)
    :param service: Dict, indexed metadata about a component service (from the Registry)
    :param component: str, type of component, one of 'KP' or 'ARA'
    :param x_maturity: Optional[str], 'x_maturity' environment target for test run (system chooses if not specified)
    :return: augmented resource metadata for a given KP or ARA service confirmed to be accessible for testing
             for one selected x-maturity environment; None if unavailable
    """
    #
    # This 'overloaded' function actually checks a number of parameters that need to be present for testable resources.
    # If the validation of all parameters succeeds, it returns a dictionary of those values; otherwise, returns 'None'
    #
    if not service:
        logger.error("validate_testable_resource() service dictionary is empty?")
        return None

    resource_metadata: Dict = dict()

    service_title = tag_value(service, "info.title")
    if service_title:
        resource_metadata['service_title'] = service_title
    else:
        logger.warning(f"Registry {component} entry '{str(index)}' lacks a 'service_title'... Skipped?")
        return None

    if not ('servers' in service and service['servers']):
        logger.warning(f"Registry {component} entry '{service_title}' lacks a 'servers' block... Skipped?")
        return None

    infores = tag_value(service, "info.x-translator.infores")

    # Internally, within SRI Testing, we only track the object_id of the infores CURIE
    infores = infores.replace("infores:", "") if infores else None

    if infores:
        resource_metadata['infores'] = infores
    else:
        logger.warning(f"Registry entry '{infores}' has no 'infores' identifier. Skipping?")
        return None

    if infores in _ignored_resources:
        logger.warning(
            f"Registry entry '{infores}' is tagged to be ignored. Skipping?"
        )
        return None

    #
    # November 2023: The new testing framework doesn't care about the Registry info.x-translator.test_data_location?
    #
    # raw_test_data_location: Optional[Union[str, Dict]] = tag_value(service, "info.x-translator.test_data_location")
    # # ... and only interested in resources with a non-empty, valid, accessible test_data_location specified
    # test_data_location: Optional[Union[str, List, Dict]] = validate_test_data_locations(raw_test_data_location)
    # if test_data_location:
    #     # Optional[Union[str, List, Dict]], may be a single URL string, an array of URL string's,
    #     # or an x-maturity indexed catalog of URLs (single or List of URL string(s))
    #     resource_metadata['test_data_location'] = test_data_location
    # else:
    #     logger.warning(
    #         f"Empty, invalid or inaccessible 'info.x-translator.test_data_location' specification "
    #         f"'{str(raw_test_data_location)}' for Registry entry '{infores}'! Service entry skipped?")
    #     return None

    servers: Optional[List[Dict]] = service['servers']

    if not servers:
        logger.warning(f"Registry entry '{infores}' missing a 'servers' block? Skipping...")
        return None

    server_urls: Dict = validate_servers(infores=infores, service=service, x_maturity=x_maturity)

    # By the time we are here, we either have a one selected
    # x_maturity environment (if a specific x_maturity was set) or,
    # if no such x_maturity preference, a catalog of (possibly one selected)
    # available 'x_maturity' environments from which to select for testing.

    # We filter out the latter situation first...
    if not server_urls:
        return None

    # Now, we try to select one of the endpoints for testing
    testable_system: Optional[Tuple[str, str]] = select_endpoint(server_urls)
    if testable_system:
        url: str
        x_maturity: str
        url, x_maturity = testable_system
        resource_metadata['url'] = url
        resource_metadata['x_maturity'] = x_maturity
    else:
        # not likely, but another sanity check!
        logger.warning(f"Service {str(index)} has no available endpoint... Skipped?")
        return None

    # Resource Metadata returned with 'testable' endpoint, tagged
    # with by x-maturity and associated with suitable test data
    # (single or list of test data file url strings)
    return resource_metadata


def extract_component_test_metadata_from_registry(
        registry_data: Dict,
        target_component_type: str,
        target_source: Optional[str] = None,
        target_trapi_version: Optional[str] = None,
        target_x_maturity: Optional[str] = None
) -> Dict[str, Dict[str, Optional[Union[str, Dict]]]]:
    """
    Extract metadata from a registry data dictionary, for all components of a specified type.

    Generally speaking, this method should only send back *one* specific service entry for each unique
    (infores-defined) KP or ARA resource, for a given TRAPI version and 'x-maturity' environment.

    The rules for this may be expressed as follows, for a given 'infores' identity:

    1. Retrieve all TRAPI service entry releases - retrieved and enumerated from the Translator SmartAPI Registry,
       as filtered by the 'source' specification and availability of test data - for the (specified or inferred)
       target 'x-maturity' environment.

    2. Among the set of service entry releases returned, select and return the 'best' TRAPI version for use in testing
       (see the assess_trapi_version() function for selection of service TRAPI version.

    :param registry_data:
        Dict, Translator SmartAPI Registry dataset
        from which specific component_type metadata will be extracted.
    :param target_component_type: str, value 'KP' or 'ARA'
    :param target_source: Optional[str], ara_id or kp_id(s) source(s) of test configuration data in the registry.
                                  Return 'all' resources of the given component type if the source is None.
                                  The 'source' may be a scalar string, or a comma-delimited set of strings.
                                  If the 'source' string includes a single asterix ('*'), it is treated
                                  as a wildcard match to the infores name being filtered.
                                  Note that all identifiers here should be the reference (object) id's
                                  of the Infores CURIE of the target resource.
    :param target_trapi_version: Optional[str], target TRAPI version for test run
                                 (system chooses 'latest', if not specified)
    :param target_x_maturity: Optional[str], 'x_maturity' environment target for test run
                              (system chooses, if not specified)

    :return: Dict[str, Dict[str, Optional[Union[str, Dict]]]] of metadata, indexed by 'test_data_location'
    """

    # Sanity check...
    assert target_component_type in ["KP", "ARA"]

    # TODO: is there a way to translate target_sources into a compiled
    #       regex pattern, for more efficient screening of infores (below)?
    #       Or pre-process the target_sources into a list of 2-tuple patterns to match?
    target_sources: Set[str] = set()
    if target_source:
        # if specified, 'source' may be a comma separated list of
        # (possibly wild card pattern matching) source strings...
        for infores in target_source.split(","):
            infores = infores.strip()
            target_sources.add(infores)

    # this dictionary, indexed by service 'infores',
    # will track the selected TRAPI version
    # for each distinct information resource
    selected_service_trapi_version: Dict = dict()

    service_metadata: Dict[str, Dict[str, Optional[Union[str, Dict]]]] = dict()

    for index, service in enumerate(registry_data['hits']):

        # We are only interested in services belonging to a given category of components
        component = tag_value(service, "info.x-translator.component")
        if not (component and component == target_component_type):
            continue

        # Retrieve all available releases of service entries - as retrieved and enumerated from the
        # Translator SmartAPI Registry dataset, as filtered by the 'source' specification - for services
        # with available test data, for the (specified or inferred) target 'x-maturity' environment.
        infores: Optional[str] = source_of_interest(service=service, target_sources=target_sources)
        if not infores:
            # silently ignore any resource whose InfoRes CURIE
            # reference identifier is missing or doesn't have a partial
            # of exact match to a specified non-empty target source
            continue

        # Filter early for TRAPI version
        service_trapi_version = tag_value(service, "info.x-translator.version")
        assess_trapi_version(infores, service_trapi_version, target_trapi_version, selected_service_trapi_version)

        # Current service doesn't have appropriate trapi_version, so skip the service
        if infores not in selected_service_trapi_version:
            continue

        resource_metadata: Optional[Dict[str, Union[str, List]]] = \
            validate_testable_resource(index, service, component, target_x_maturity)

        if not resource_metadata:
            continue

        # Once past the 'testable resources' metadata gauntlet,
        # the following parameters are assumed valid and non-empty
        service_title: str = resource_metadata['service_title']

        # this 'url' is the service endpoint in the
        # specified 'x_maturity' environment
        url: str = resource_metadata['url']
        service_x_maturity: str = resource_metadata['x_maturity']

        # The 'test_data_location' also has url's but these are now expressed
        # in a polymorphic manner: Optional[Dict[str, Union[str, List, Dict]]].
        # See validate_test_data_locations above for details
        test_data_location = resource_metadata['test_data_location']

        # Now, we start to collect the remaining Registry metadata

        # Grab additional service metadata, then store it all
        service_version = tag_value(service, "info.version")
        biolink_version = tag_value(service, "info.x-translator.biolink-version")

        # TODO: temporary hack to deal with resources which are somewhat sloppy or erroneous in their declaration
        #       of the applicable Biolink Model version for validation: enforce a minimium Biolink Model version.
        if not biolink_version or SemVer.from_string(MINIMUM_BIOLINK_VERSION) >= SemVer.from_string(biolink_version):
            biolink_version = MINIMUM_BIOLINK_VERSION

        # Index services by (infores, trapi_version, biolink_version)
        service_id: str = f"{infores},{service_trapi_version},{biolink_version},{service_x_maturity}"

        if service_id not in _service_catalog:
            _service_catalog[service_id] = list()
        else:
            logger.warning(
                f"Infores '{infores}' appears duplicated among {component} Registry entries. " +
                f"The new '{service_x_maturity}' entry reports a service version '{str(service_version)}', " +
                f"TRAPI version '{str(target_trapi_version)}' and Biolink Version '{str(biolink_version)}'."
            )

        if service_id not in service_metadata:
            service_metadata[service_id] = dict()
        else:
            logger.warning(
                f"Ignoring service {index}: '{service_title}' with a duplicate service" +
                f"'infores,trapi_version,biolink_version' identifier: '{service_id}'?"
            )
            continue

        entry_id: RegistryEntryId = \
            RegistryEntryId(
                service_title,
                service_version,
                selected_service_trapi_version[infores],
                biolink_version,
                service_x_maturity
            )

        _service_catalog[service_id].append(entry_id)

        capture_tag_value(service_metadata, service_id, "url", url)
        capture_tag_value(service_metadata, service_id, "x_maturity", service_x_maturity)
        capture_tag_value(service_metadata, service_id, "service_title", service_title)
        capture_tag_value(service_metadata, service_id, "service_version", service_version)
        capture_tag_value(service_metadata, service_id, "component", target_component_type)
        capture_tag_value(service_metadata, service_id, "infores", infores)
        capture_tag_value(service_metadata, service_id, "test_data_location", test_data_location)
        capture_tag_value(service_metadata, service_id, "biolink_version", biolink_version)
        capture_tag_value(service_metadata, service_id, "trapi_version", service_trapi_version)

    # return the selected service(s) uniquely filtered by
    # source constraint, TRAPI version and x-maturity environment
    return {
        service_id: details
        for service_id, details in service_metadata.items()
        if details["trapi_version"] == selected_service_trapi_version.setdefault(details["infores"], None)
    }


def find_infores(service: Dict, target_infores_id: str) -> bool:
    """
    Source filtering function, checking a source identifier against a set of identifiers.
    The target_source strings may also be wildcard patterns with a single asterix (only)
    with possible prefix only, suffix only or prefix-<body>-suffix matches.

    :param service: Dict, Translator SmartAPI Registry entry for one
                          service 'hit' containing an 'infores' property
    :param target_infores_id: str, infores reference identifier
    :return: bool, True if matched; False otherwise.
    """
    assert service, "registry.source_of_interest() method call: unexpected empty service?!?"
    assert target_infores_id, "registry.source_of_interest() empty infores_id"

    service_infores: str = tag_value(service, "info.x-translator.infores")

    # Internally, within SRI Testing, we only track the object_id of the infores CURIE
    service_infores_id = service_infores.replace("infores:", "") if service_infores else None

    if service_infores_id and target_infores_id == service_infores_id:
        return True
    else:
        return False


def resolve_endpoint(
        server_urls: List,
        x_maturity: Optional[str] = None,
        check_access: bool = True
) -> Optional[Tuple[str, str]]:
    # This is a revised version of the SRI_Testing harness endpoint
    # selector which is agnostic about test_data_location
    """
    Select one test URL based on active endpoints from available 'server_urls'.
    Usually, by the time this method is called, any 'x_maturity' preference
    has constrained the 'server_urls'.

    If 'x_maturity' is given then only an endpoint running in it will be returned.
    Otherwise, if the 'server_urls' have several 'x_maturity' environments,
    the highest precedence x_maturity is returned.

    The precedence is in order of: 'production', 'staging', 'testing' and 'development'
    (this could change in the future, based on Translator community deliberations...).

    :param server_urls: List, service 'servers' block list of available servers hosting the service
    :param x_maturity: Optional[str] = None, target x_maturity environment within which the component
                                              is running and for which the endpoint is requested
                                              One of ['production', 'staging', 'testing', 'development']
                                              (default: check x-maturity environments in precedence order)
    :param check_access: bool, verify TRAPI access of endpoints before returning (Default: True)

    :return: Optional[Tuple[str, str]], Tuple of 'x-maturity' and 'url' of an active endpoint
    """
    target_environments: List[str]

    if x_maturity:
        target_environments = [x_maturity]
    else:
        # Check available environments from the
        # precedence order of the DEPLOYMENT_TYPES
        target_environments = DEPLOYMENT_TYPES
    for x_maturity in target_environments:
        urls = [server["url"] for server in server_urls if server["x-maturity"] == x_maturity]
        url: Optional[str] = select_accessible_endpoint(urls, check_access)
        if url is not None:
            return x_maturity, url

    # default is failure
    return None


#########################################
# Simplified resolution of Translator
# component endpoints, for the
# in the GraphValidationTest project
#########################################
def get_component_endpoint_from_registry(
        registry_data: Dict,
        infores_id: str,
        environment: str,
        target_trapi_version: Optional[str],
        target_biolink_version: Optional[str]
) -> Optional[str]:
    """
    Get component endpoint from registry data,
    for a given infores object identifier and
    for a specified environment.
    :param registry_data: Dict, Python dictionary contents retrieved
                                from the Translator SmartAPI Registry
    :param infores_id: str, object (reference) identifier of the InfoRes CURIE
                            identifying a known resource in the Registry
    :param environment: x_maturity environment within which the component
                        is running and for which the endpoint is requested
    :param target_trapi_version: Optional[str] = None, target TRAPI version (default: latest public release)
    :param target_biolink_version: Optional[str] = None, target Biolink Model version (default: Biolink toolkit release)
    :return: Optional[str], the endpoint URL if available, None otherwise
    """
    if not target_trapi_version:
        target_trapi_version = LATEST_TRAPI_VERSION

    if not target_biolink_version:
        target_biolink_version = LATEST_BIOLINK_VERSION

    # this dictionary, indexed by service 'infores',
    # will track the selected TRAPI version
    # for each distinct information resource
    selected_service_trapi_version: Dict = dict()
    endpoint: Optional[str] = None
    for index, service in enumerate(registry_data['hits']):

        if not find_infores(service=service, target_infores_id=infores_id):
            continue

        # Filter early for TRAPI version
        service_trapi_version = tag_value(service, "info.x-trapi.version")
        assess_trapi_version(infores_id, service_trapi_version, target_trapi_version, selected_service_trapi_version)

        # Current service doesn't have a compatible 'service_trapi_version', so skip the service
        if infores_id not in selected_service_trapi_version:
            continue

        # only need to filter on Biolink Release if a 'target_biolink_version' is given?
        if target_biolink_version:
            service_biolink_version = tag_value(service, "info.x-translator.biolink-version")
            if (not service_biolink_version or
                    SemVer.from_string(MINIMUM_BIOLINK_VERSION) >= SemVer.from_string(service_biolink_version)):
                service_biolink_version = MINIMUM_BIOLINK_VERSION
            if not SemVer.from_string(target_biolink_version) >= SemVer.from_string(service_biolink_version):
                continue

        assert environment in DEPLOYMENT_TYPE_MAP.keys(), f"Unknown environment '{environment}'"
        # need to map ['dev', 'ci', 'test', 'prod'] onto full name in DEPLOYMENT_TYPES
        x_maturity = DEPLOYMENT_TYPE_MAP[environment]

        endpoint_entry: Optional[Tuple[str, str]] = \
            resolve_endpoint(server_urls=service["servers"], x_maturity=x_maturity)

        if endpoint_entry is not None:
            x_maturity_found, endpoint = endpoint_entry

            # Is this a necessary sanity check?
            if x_maturity == x_maturity_found:
                logger.info(f"Found live '{infores_id}' service '{endpoint}' running in '{x_maturity}'.")
                return endpoint

    logger.warning(f"No '{environment}' endpoint found for '{infores_id}'")
    return None
