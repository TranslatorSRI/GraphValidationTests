"""
Unit tests for Standards Validation Test code validation
"""
import os
import json
from sys import stderr
from typing import List, Dict
from json import dump
import pytest

from translator_testing_model.datamodel.pydanticmodel import TestAsset

from graph_validation_tests.utils.unit_test_templates import (
    by_subject,
    by_object
)
from standards_validation_test_runner import (
    StandardsValidationTest,
    run_standards_validation_tests
)
from tests import (
    TEST_DATA_DIR,
    SAMPLE_MOLEPRO_INPUT_DATA,
    SAMPLE_ARAX_INPUT_DATA,
    SAMPLE_ARAGORN_INPUT_DATA,
    SAMPLE_MOLEPRO_TEST_ASSET,
    FULL_TEST
)


@pytest.mark.parametrize(
    "data,environment,component,expected_result",
    [
        (
            SAMPLE_MOLEPRO_INPUT_DATA,
            "ci",
            "molepro",
            None
        ),
        (
            SAMPLE_ARAX_INPUT_DATA,
            "ci",
            "arax",
            None
        ),
        (
            SAMPLE_ARAGORN_INPUT_DATA,
            "ci",
            "aragorn",
            None
        )
    ]
)
@pytest.mark.skipif(
    not FULL_TEST,
    reason="This test is a long running TRAPI query on active resources. Best not to run on CI!"
)
@pytest.mark.asyncio
async def test_standards_validation_test(
        data: Dict,
        environment: str,
        component: str,
        expected_result
):
    trapi_generators = [
        by_subject,
        by_object
    ]
    results: Dict = await StandardsValidationTest.run_tests(
        **data,
        trapi_generators=trapi_generators,
        environment=environment,
        components=[component]
    )
    dump(results, stderr, indent=4)


# ARS tests not yet supported so yes... results will
# always be empty, with a logger message to inform why
@pytest.mark.skipif(
    not FULL_TEST,
    reason="This test is a long running TRAPI query on active resources. Best not to run on CI!"
)
@pytest.mark.asyncio
async def test_standards_validation_test_on_ars():
    trapi_generators = [
        by_subject,
        by_object
    ]
    results: Dict = await StandardsValidationTest.run_tests(
        **SAMPLE_MOLEPRO_INPUT_DATA,
        trapi_generators=trapi_generators,
        environment="prod"
    )
    assert not results


@pytest.mark.parametrize(
    "data,environment,components,expected_result",
    [
        (   # Query 0 - MolePro test
            SAMPLE_MOLEPRO_INPUT_DATA,
            "ci",
            ["molepro"],
            None
        ),
        (   # Query 1 - ARAX test
            SAMPLE_ARAX_INPUT_DATA,
            "ci",
            ["arax"],
            None
        ),
        (   # Query 2 - Aragorn test
            SAMPLE_ARAGORN_INPUT_DATA,
            "ci",
            ["aragorn"],
            None
        ),
        (   # Query 3 - Combined ARAX and MolePro test
            SAMPLE_MOLEPRO_INPUT_DATA,
            "ci",
            ["molepro", "arax", "aragorn"],
            None
        )
    ]
)
@pytest.mark.skipif(
    not FULL_TEST,
    reason="This test is a long running TRAPI query on active resources. Best not to run on CI!"
)
@pytest.mark.asyncio
async def test_run_standards_validation_tests(
        data: Dict,
        environment: str,
        components: List[str],
        expected_result
):
    results: Dict = await run_standards_validation_tests(
        **data,
        environment=environment,
        components=components
    )
    assert results
    dump(results, stderr, indent=4)


@pytest.mark.parametrize(
    "environment,component,trapi_response_filename",
    [
        (   # Query 0 - a full MolePro generated TRAPI Response
            "ci",
            "molepro",
            "standards_validation_test_response.json"
        )
    ]
)
def test_standards_validation_tests_validate_test_case(
        environment: str,
        component: str,
        trapi_response_filename: str
):
    test_file = os.path.join(TEST_DATA_DIR, trapi_response_filename)
    with (open(test_file, mode="r") as trapi_json_file):
        # Standards Testing doesn't actually care
        # about the TestAsset, only the JSON output?
        test_asset: TestAsset = TestAsset(**SAMPLE_MOLEPRO_TEST_ASSET)
        trapi_response: Dict = json.load(trapi_json_file)
        svt = StandardsValidationTest(
            test_asset=test_asset,
            environment=environment,
            component=component
        )
        results: Dict = svt.test_case_processor(trapi_response=trapi_response)
        assert results
        dump(results, stderr, indent=4)
