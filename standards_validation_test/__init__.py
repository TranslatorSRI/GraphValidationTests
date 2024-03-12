"""
One Hop Tests (core tests extracted
from the legacy SRI_Testing project)
"""
from typing import Dict, List, Optional
import logging

from translator_testing_model.datamodel.pydanticmodel import TestAsset, TestEnvEnum
from graph_validation_test import env_spec, GraphValidationTest, get_parameters, target_component_urls


class StandardsValidationTest(GraphValidationTest):

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
        super().__init__(endpoints, trapi_version, biolink_version, runner_settings, logger)

    async def run(self, test_asset: TestAsset):
        """
        Wrapper to invoke a StandardsValidationTest on a single TestAsset
        in a given test environment for a given query type.

        :param test_asset: TestAsset, test to be processed for target TestCases.
        :return: None - use 'get_results()' method below
        """
        raise NotImplementedError("Implement this")


def run_validation_test(
        subject_id: str,
        subject_category: str,
        predicate_id: str,
        object_id: str,
        object_category: str,
        environment: Optional[TestEnvEnum] = None,
        components: Optional[str] = None,
        trapi_version: Optional[str] = None,
        biolink_version: Optional[str] = None,
        runner_settings: Optional[List[str]] = None,
        logger: Optional[logging.Logger] = None
) -> Dict:
    #     # One test edge (asset)
    #     "subject_id": asset.input_id,  # str
    #     "subject_category": asset.input_category,  # str
    #     "predicate_id": asset.predicate_id,  # str
    #     "object_id": asset.output_id,  # str
    #     "object_category": asset.output_category  # str
    #
    #     "environment": environment, # Optional[TestEnvEnum] = None; default: 'TestEnvEnum.ci' if not given
    #     "components": components,  # Optional[str] = None; default: 'ars' if not given
    #     "trapi_version": trapi_version,  # Optional[str] = None; latest community release if not given
    #     "biolink_version": biolink_version,  # Optional[str] = None; current Biolink Toolkit default if not given
    #     "runner_settings": asset.test_runner_settings,  # Optional[List[str]] = None
    #     "logger": logger,  # Python Optional[logging.Logger] = None
    """
    Run a battery of "One Hop" knowledge graph test cases using specified test asset information.

    :param subject_id: str, CURIE identifying the identifier of the subject concept
    :param subject_category: str, CURIE identifying the category of the subject concept
    :param predicate_id: str, name of Biolink Model predicate defining the statement predicate_id being tested.
    :param object_id: str, CURIE identifying the identifier of the object concept
    :param object_category: str, CURIE identifying the category of the object concept
    :param components: Optional[str] = None, components to be tested
                                     (values from ComponentEnum in TranslatorTestingModel; default 'ars')
    :param environment: Optional[str] = None, Target Translator execution environment for the test,
                                       one of 'dev', 'ci', 'test' or 'prod' (default: 'ci')
    :param trapi_version: Optional[str] = None, target TRAPI version (default: latest public release)
    :param biolink_version: Optional[str] = None, target Biolink Model version (default: Biolink toolkit release)
    :param runner_settings: Optional[Dict[str, str]] = None, extra string parameters to the Test Runner
    :param logger: Optional[logging.Logger] = None, Python logging handle
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


if __name__ == '__main__':
    args = get_parameters()
    results: Dict = run_validation_test(**vars(args))
    print(results)
