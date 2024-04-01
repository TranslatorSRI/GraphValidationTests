"""
Code to submit GraphValidation test queries to
Translator components - ARS, ARA, KP - via TRAPI
"""
from sys import stderr
from typing import Optional, Dict
from functools import lru_cache
import requests

from reasoner_validator.trapi import call_trapi
from graph_validation_test.translator.registry import (
    DEPLOYMENT_TYPE_MAP,
    get_the_registry_data,
    get_component_endpoint_from_registry
)

from logging import getLogger
logger = getLogger()


ars_env_spec = {
    'dev': 'ars-dev',
    'ci': 'ars.ci',
    'test': 'ars.test',
    'prod': 'ars-prod'
}


ARS_HOSTS = [
    'ars-prod.transltr.io',
    'ars.test.transltr.io',
    'ars.ci.transltr.io',
    'ars-dev.transltr.io',
    'ars.transltr.io'
]


def post_query(url: str, query: Dict, params=None, server: str = ""):
    """
    Post a JSON query to the specified URL and return the JSON response.

    :param url, str URL target for HTTP POST
    :param query, JSON query for posting
    :param params, optional parameters
    :param server, str human-readable name of server called (for error message reports)
    """
    if params is None:
        response = requests.post(url, json=query)
    else:
        response = requests.post(url, json=query, params=params)
    if not response.status_code == 200:
        print(
            f"Server {server} at '\nUrl: '{url}', Query: '{query}' with " +
            f"parameters '{params}' returned HTTP error code: '{response.status_code}'",
            file=stderr
        )
        return {}
    return response.json()


def generate_test_error_msg_prefix(case: Dict, test_name: str) -> str:
    assert case
    test_msg_prefix: str = "test_onehops.py::test_trapi_"
    resource_id: str = ""
    component: str = "kp"
    if 'ara_source' in case and case['ara_source']:
        component = "ara"
        ara_id = case['ara_source'].replace("infores:", "")
        resource_id += ara_id + "|"
    test_msg_prefix += f"{component}s["
    if 'kp_source' in case and case['kp_source']:
        kp_id = case['kp_source'].replace("infores:", "")
        resource_id += kp_id
    edge_idx = case['idx']
    edge_id = generate_edge_id(resource_id, edge_idx)
    if not test_name:
        test_name = "input"
    test_msg_prefix += f"{edge_id}-{test_name}] FAILED"
    return test_msg_prefix


def generate_edge_id(resource_id: str, edge_i: int) -> str:
    return f"{resource_id}#{str(edge_i)}"


def constrain_trapi_request_to_kp(trapi_request: Dict, kp_source: str) -> Dict:
    """
    Method to annotate KP constraint on an ARA call
    as an attribute_constraint object on the test edge.
    :param trapi_request: Dict, original TRAPI message
    :param kp_source: str, KP InfoRes (from kp_source field of test edge)
    :return: Dict, trapi_request annotated with additional KP 'attribute_constraint'
    """
    assert "message" in trapi_request
    message: Dict = trapi_request["message"]
    assert "query_graph" in message
    query_graph: Dict = message["query_graph"]
    assert "edges" in query_graph
    edges: Dict = query_graph["edges"]
    assert "ab" in edges
    edge: Dict = edges["ab"]

    # annotate the edge constraint on the (presumed single) edge object
    edge["attribute_constraints"] = [
        {
            "id": "biolink:knowledge_source",
            "name": "knowledge source",
            "value": [kp_source],
            "operator": "=="
        }
    ]

    return trapi_request


def retrieve_trapi_response(host_url: str, response_id: str):
    try:
        response_content = requests.get(
            f"{host_url}{response_id}",
            headers={'accept': 'application/json'}
        )
        if response_content:
            status_code = response_content.status_code
            if status_code == 200:
                print(f"...Result returned from '{host_url}'!")
        else:
            status_code = 404

    except Exception as e:
        print(f"Remote host {host_url} unavailable: Connection attempt to {host_url} triggered an exception: {e}")
        response_content = None
        status_code = 404

    return status_code, response_content


def retrieve_ars_result(response_id: str, verbose: bool) -> Optional[Dict]:
    trapi_response: Optional[Dict] = None

    if verbose:
        print(f"Trying to retrieve ARS Response UUID '{response_id}'...")

    response_content: Optional = None
    status_code: int = 404

    for ars_host in ARS_HOSTS:
        if verbose:
            print(f"\n...from {ars_host}", end=None)

        status_code, response_content = retrieve_trapi_response(
            host_url=f"https://{ars_host}/ars/api/messages/",
            response_id=response_id
        )
        if status_code != 200:
            continue

    if status_code != 200:
        print(f"Unsuccessful HTTP status code '{status_code}' reported for ARS PK '{response_id}'?")
    else:
        # Unpack the response content into a dict
        try:
            response_dict = response_content.json()

            if 'fields' in response_dict:
                if 'actor' in response_dict['fields'] and str(response_dict['fields']['actor']) == '9':
                    print("The supplied response id is a collection id. Please supply the UUID for a response")
                elif 'data' in response_dict['fields']:
                    print(f"Validating ARS PK '{response_id}' TRAPI Response result...")
                    trapi_response = response_dict['fields']['data']
                else:
                    print("ARS response dictionary is missing 'fields.data'?")
            else:
                print("ARS response dictionary is missing 'fields'?")

        except Exception as e:
            print(f"Cannot decode ARS PK '{response_id}' to a Translator Response, exception: {e}")

    return trapi_response


def get_component_infores_object_id(component: str) -> str:
    """
    Returns the InfoRes object identifier of a given component.
    :param component: str, acronym of the component
    :return: infores reference identifier of the component
    """
    # TODO: can I resolve here whether a given component
    #       is an ARA or a KP, and return this to the caller?
    assert component
    infores_map = {
        "arax": "arax",
        "aragorn": "aragorn",
        "bte": "biothings-explorer",
        "improving": "improving-agent",
    }
    return infores_map.setdefault(component, component)


@lru_cache()
def resolve_component_endpoint(
        component: Optional[str],
        environment: Optional[str],
        target_trapi_version: Optional[str],
        target_biolink_version: Optional[str]
) -> Optional[str]:
    """
    Resolve target endpoints for running the test.
    :param component: Optional[str], component to be queried, ideally, drawn from a value
                                            in the 'ComponentEnum' of the Translator Testing Model;
                                            (default: None == 'ars')
    :param environment: Optional[str]: target Translator execution environment of the component to be accessed;
                                              One of ['dev', 'ci', 'test', 'prod'] (default: None == 'ci')
    :param target_trapi_version: Optional[str], target TRAPI version (default: latest public release)
    :param target_biolink_version: Optional[str], target Biolink Model version (default: Biolink toolkit release)
    :return: Optional[str], environment-specific endpoint for component to be queried. None if not available.
    """
    if not component:
        component = 'ars'

    if not environment:
        environment = 'ci'
    elif environment not in DEPLOYMENT_TYPE_MAP.keys():
        logger.error(
            f"resolve_component_endpoint(): unexpected environment type: '{environment}', Cannot resolve endpoint!"
        )
        return None

    if component == 'ars':
        ars_env: str = ars_env_spec[environment]
        return f"https://{ars_env}.transltr.io/ars/api/"
    else:
        registry_data: Dict = get_the_registry_data()
        endpoint: Optional[str] = \
            get_component_endpoint_from_registry(
                registry_data,
                infores_id=get_component_infores_object_id(component),
                environment=environment,
                target_trapi_version=target_trapi_version,
                target_biolink_version=target_biolink_version
            )
        if not endpoint:
            logger.error(
                f"Could not resolve endpoint of component '{component}' within specified environment '{environment}'?"
            )

        return endpoint


async def run_trapi_query(
        trapi_request: Dict,
        component: str,
        environment: str,
        target_trapi_version: Optional[str],
        target_biolink_version: Optional[str]
) -> Optional[Dict]:
    """
    Make a call to the TRAPI (or TRAPI-like, e.g. ARS) component, returning the result.

    :param trapi_request: Dict, TRAPI request JSON, as a Python data structure.
    :param component: str, simple identifier of a Translator component target:
                          'ars', ARA acronym (e.g. 'arax') or KP acronym (e.g. 'molepro')
    :param environment: Optional[str] = None, Target Translator execution environment for the test,
                                              one of 'dev', 'ci', 'test' or 'prod' (default: 'ci')
    :param target_trapi_version: Optional[str], target TRAPI version (default: latest public release)
    :param target_biolink_version: Optional[str], target Biolink Model version (default: Biolink toolkit release)
    :return:  Dict, TRAPI response JSON, as a Python data structure.
    """
    trapi_response: Optional[Dict] = None
    endpoint: str = resolve_component_endpoint(
        component=component,
        environment=environment,
        target_trapi_version=target_trapi_version,
        target_biolink_version=target_biolink_version
    )
    if not endpoint:
        return None

    if component == 'ars':
        # TODO: make the (modified) TRAPI query to the ARS
        raise NotImplementedError("Implement ARS TRAPI query processing!")
    else:
        # Make the TRAPI call to the TestCase targeted ARS, KP or
        # ARA resource, using the case-documented input test edge
        trapi_response = await call_trapi(endpoint, trapi_request)

    return trapi_response
