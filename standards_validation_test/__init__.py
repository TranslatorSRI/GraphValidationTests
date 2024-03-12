"""
One Hop Tests (core tests extracted
from the legacy SRI_Testing project)
"""
from typing import Dict, List, Optional
from functools import lru_cache
import logging
from argparse import ArgumentParser

from bmt import utils
from reasoner_validator.biolink import get_biolink_model_toolkit
from translator_testing_model.datamodel.pydanticmodel import TestAsset
from one_hop_test.translator.trapi import run_one_hop_unit_test, UnitTestReport
from one_hop_test.unit_test_templates import (
    by_subject,
    inverse_by_new_subject,
    by_object,
    raise_subject_entity,
    raise_object_entity,
    raise_object_by_subject,
    raise_predicate_by_subject
)
from one_hop_test.translator.registry import (
    get_the_registry_data,
    extract_component_test_metadata_from_registry
)

# from .utils.asyncio import gather


env_spec = {
    'dev': 'ars-dev',
    'ci': 'ars.ci',
    'test': 'ars.test',
    'prod': 'ars-prod'
}


class StandardsValidationTest:

    def __init__(
            self,
            endpoints: List[str],
            trapi_version: Optional[str] = None,
            biolink_version: Optional[str] = None,
            runner_settings: Optional[Dict[str, str]] = None,
            logger: Optional[logging.Logger] = None
    ):
        """
        StandardsValidationTest constructor.

        :param endpoints: List[str], target environment endpoint(s) being targeted for testing
        :param trapi_version: Optional[str], target TRAPI version (default: current release)
        :param biolink_version: Optional[str], target Biolink Model version (default: current release)
        :param runner_settings: Optional[Dict[str, str]], extra string directives to the Test Runner (default: None)
        :param logger: Optional[logging.Logger], Python logger, for diagnostics
        """
        self.endpoints: List[str] = endpoints
        self.trapi_version = trapi_version

        self.biolink_version = biolink_version
        self.bmt = get_biolink_model_toolkit(biolink_version=biolink_version)

        self.runner_settings = runner_settings

        self.logger: Optional[logging.Logger] = logger
        self._id = 0
        self.results: Dict = dict()

    def generate_test_asset_id(self) -> str:
        self._id += 1
        return f"TestAsset:{self._id:0>5}"

    def generate_predicate_id(self, relationship: str) -> Optional[str]:
        if self.bmt.is_predicate(relationship):
            predicate = self.bmt.get_element(relationship)
            if predicate:
                return utils.format_element(predicate)
        return None

    def build_test_asset(
            self,
            subject_id: str,
            subject_category: str,
            predicate_id: str,
            object_id: str,
            object_category: str
    ) -> TestAsset:
        """
        Construct a Python TestAsset object.

        :param subject_id: str, CURIE identifying the identifier of the subject concept
        :param subject_category: str, CURIE identifying the category of the subject concept
        :param predicate_id: str, name of Biolink Model predicate defining the statement predicate_id being tested.
        :param object_id: str, CURIE identifying the identifier of the object concept
        :param object_category: str, CURIE identifying the category of the subject concept
        :return: TestAsset object
        """
        return TestAsset.construct(
            id=self.generate_test_asset_id(),
            input_id=subject_id,
            input_category=subject_category,
            predicate_id=predicate_id,
            predicate_name=predicate_id.replace("biolink:", ""),
            output_id=object_id,
            output_category=object_category
        )

    def test_case_wrapper(self, test_asset: TestAsset):
        async def test_case(test_type) -> UnitTestReport:
            # TODO: eventually need to process multiple self.endpoints(?)
            target_url: str = self.endpoints[0]
            return await run_one_hop_unit_test(
                target_url, test_asset, test_type, self.trapi_version, self.biolink_version
            )
        return test_case

    async def run(self, test_asset: TestAsset):
        """
        Wrapper to invoke a StandardsValidationTest on a single TestAsset
        in a given test environment for a given query type.

        :param test_asset: TestAsset, test to be processed for target TestCases.
        :return: None - use 'get_results()' method below
        """
        test_case = self.test_case_wrapper(test_asset=test_asset)
        #
        # TODO: do these tests need to be run sequentially or
        #       could they be run concurrently then "gathered" together?
        #     coroutines = [
        #         test_case(test_type)
        #         for test_type in [
        #           by_subject,
        #           inverse_by_new_subject,
        #           by_object,
        #           raise_subject_entity,
        #           raise_object_by_subject,
        #           raise_predicate_by_subject
        #         ]
        #     ]
        #     await gather(*coroutines, limit=num_concurrent_requests)
        #
        #     TODO: How are the results to be retrieved and indexed?

        self.results["by_subject"] = await test_case(by_subject)
        self.results["inverse_by_new_subject"] = await test_case(inverse_by_new_subject)
        self.results["by_object"] = await test_case(by_object)
        self.results["raise_subject_entity"] = await test_case(raise_subject_entity)
        self.results["raise_object_by_subject"] = await test_case(raise_object_by_subject)
        self.results["raise_predicate_by_subject"] = await test_case(raise_predicate_by_subject)

    def get_results(self) -> Dict[str, Dict[str, List[str]]]:
        # The ARS_test_Runner with the following command:
        #
        #       ARS_Test_Runner
        #           --env 'ci'
        #           --query_type 'treats_creative'
        #           --expected_output '["TopAnswer","TopAnswer"]'
        #           --input_curie 'MONDO:0005301'
        #           --output_curie  '["PUBCHEM.COMPOUND:107970","UNII:3JB47N2Q2P"]'
        #
        # gives the json report below:
        #
        # {
        #     "pks": {
        #         "parent_pk": "e29c5051-d8d7-4e82-a1a1-b3cc9b8c9657",
        #         "merged_pk": "56e3d5ac-66b4-4560-9f56-7a4d117e8003",
        #         "aragorn": "14953570-7451-4d1b-a817-fc9e7879b477",
        #         "arax": "8c88ead6-6cbf-4c9a-9570-ca76392ddb7a",
        #         "unsecret": "bd084e27-2a0e-4df4-843c-417bfac6f8c7",
        #         "bte": "d28a4146-9486-4e98-973d-8cdd33270595",
        #         "improving": "d8d3c905-ec07-491f-a078-7ef0f489a409"
        #     },
        #     "results": [
        #         {
        #             "PUBCHEM.COMPOUND:107970": {
        #                 "aragorn": "Fail",
        #                 "arax": "Pass",
        #                 "unsecret": "Fail",
        #                 "bte": "Pass",
        #                 "improving": "Pass",
        #                 "ars": "Pass"
        #             }
        #         },
        #         {
        #             "UNII:3JB47N2Q2P": {
        #                 "aragorn": "Fail",
        #                 "arax": "Pass",
        #                 "unsecret": "Fail",
        #                 "bte": "Pass",
        #                 "improving": "Pass",
        #                 "ars": "Pass"
        #             }
        #         }
        #     ]
        # }
        # TODO: need to sync and iterate with TestHarness conception of TestRunner results
        report: UnitTestReport
        return {test_name: report.get_messages() for test_name, report in self.results.items()}


def get_component_infores(component: str):
    infores_map = {
        "arax": "arax",
        "aragorn": "aragorn",
        "bte": "biothings-explorer",
        "improving": "improving-agent",
    }
    # TODO: what if the component is not yet registered in the model?
    return f"infores:{infores_map.setdefault(component,component)}"


@lru_cache()
def target_component_urls(env: str, components: Optional[str] = None) -> List[str]:
    """
    Resolve target endpoints for running the test.

    :param components: Optional[str], components to be tested
                       (values from 'ComponentEnum' in TranslatorTestingModel; default 'ars')
    :param env: target Translator execution environment of component(s) to be tested.
    :return: List[str], environment-specific endpoint(s) for component(s) to be tested.
    """
    endpoints: List[str] = list()
    component_list: List[str]
    if components:
        # TODO: need to validate/sanitize the list of components
        component_list = components.split(",")
    else:
        component_list = ['ars']
    for component in component_list:
        if component == 'ars':
            endpoints.append(f"https://{env}.transltr.io/ars/api/")
        else:
            # TODO: resolve the endpoints for non-ARS targets using the Translator SmartAPI Registry?
            registry_data: Dict = get_the_registry_data()
            service_metadata = \
                extract_component_test_metadata_from_registry(
                    registry_data,
                    "ARA",  # TODO: how can I also track KP's?
                    target_source=get_component_infores(component),
                    target_x_maturity=env
                )
            if not service_metadata:
                raise NotImplementedError("Non-ARS component-specific testing not yet implemented?")

            # TODO: fix this! the service_metadata is a complex dictionary of entries.. how do we resolve it?
            endpoints.append(service_metadata["url"])

    return endpoints


def run_validation_test(
        subject_id: str,
        subject_category: str,
        predicate_id: str,
        object_id: str,
        object_category: str,
        components: Optional[str] = None,
        environment: Optional[str] = None,
        trapi_version: Optional[str] = None,
        biolink_version: Optional[str] = None,
        runner_settings: Optional[Dict[str, str]] = None,
        logger: Optional[logging.Logger] = None
) -> Dict:
    """
    Run a reasoner-validator driven validation of a knowledge graph using specified test data edges.

    :param subject_id: str, CURIE identifying the identifier of the subject concept
    :param subject_category: str, CURIE identifying the category of the subject concept
    :param predicate_id: str, name of Biolink Model predicate defining the statement predicate_id being tested.
    :param object_id: str, CURIE identifying the identifier of the object concept
    :param subject_category: str, CURIE identifying the category of the subject concept
    :param components: Optional[str], components to be tested
                                     (values from ComponentEnum in TranslatorTestingModel; default 'ars')
    :param environment: Optional[str], Target Translator execution environment for the test,
                                       one of 'dev', 'ci', 'test' or 'prod' (default: 'ci')
    :param trapi_version: Optional[str], target TRAPI version (default: current release)
    :param biolink_version: Optional[str], target Biolink Model version (default: current release)
    :param runner_settings: Optional[Dict[str, str]], extra string parameters to the Test Runner (default: None)
    :param logger: Optional[logging.Logger], Python logging handle (Default: None)
    :return: Dict { "pks": List[<pks>], "results": Dict[<pks>, <pks_result>] }
    """
    endpoints: List[str] = target_component_urls(env=env_spec[environment], components=components)

    oht: StandardsValidationTest = StandardsValidationTest(
        endpoints=endpoints,
        trapi_version=trapi_version,
        biolink_version=biolink_version,
        runner_settings=runner_settings,
        logger=logger
    )

    # OneHop tests directly use Test Assets to internally configure and run its Test Cases
    test_asset: TestAsset = oht.build_test_asset(
        subject_id,
        subject_category,
        predicate_id,
        object_id,
        object_category
    )

    oht.run(test_asset=test_asset)

    return oht.get_results()


def get_parameters():
    """Parse CLI args."""

    # Sample command line interface parameters:
    #     --environment 'ci'
    #     --subject_id 'MONDO:0005301'
    #     --predicate_id 'treats'
    #     --object_id  'PUBCHEM.COMPOUND:107970'

    parser = ArgumentParser(description="Translator SRI Automated Test Harness")

    parser.add_argument(
        "--environment",
        type=str,
        required=True,
        choices=['dev', 'ci', 'test', 'prod'],
        help="Translator execution environment of the Translator Component targeted for testing.",
    )

    parser.add_argument(
        "--components",
        type=str,
        help="Names Translator components to be tested taken from the Translator Testing Model 'ComponentEnum' " +
             "(may be a comma separated string of such names; default: run the test against the 'ars')",
        default=None
    )

    parser.add_argument(
        "--subject_id",
        type=str,
        required=True,
        help="Statement object concept CURIE",
    )

    parser.add_argument(
        "--predicate_id",
        type=str,
        required=True,
        help="Statement Biolink Predicate identifier",
    )

    # TODO: should this be multi-valued or not?
    parser.add_argument(
        "--object_id",
        type=str,
        required=True,
        help="Statement object concept CURIE ",
    )

    parser.add_argument(
        "--trapi_version",
        type=str,
        help="TRAPI version expected for knowledge graph access (default: use current default release)",
        default=None
    )

    parser.add_argument(
        "--biolink_version",
        type=str,
        help="Biolink Model version expected for knowledge graph access (default: use current default release)",
        default=None
    )

    parser.add_argument(
        "--log_level",
        type=str,
        choices=["ERROR", "WARNING", "INFO", "DEBUG"],
        help="Level of the logs.",
        default="WARNING"
    )

    return parser.parse_args()


if __name__ == '__main__':
    args = get_parameters()
    results: Dict = run_validation_test(**vars(args))
    print(results)
