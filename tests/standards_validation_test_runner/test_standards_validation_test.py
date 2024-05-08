"""
Unit tests for Standards Validation Test code validation
"""
from sys import stderr
from typing import Dict
from json import dump
import pytest

from graph_validation_tests.utils.unit_test_templates import by_subject, by_object
from standards_validation_test_runner import StandardsValidationTest, run_standards_validation_tests
from tests import SAMPLE_MOLEPRO_INPUT_DATA, SAMPLE_ARAX_INPUT_DATA, SAMPLE_ARAGORN_INPUT_DATA


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
@pytest.mark.asyncio
async def test_run_standards_validation_tests(
        data: Dict,
        environment: str,
        component: str,
        expected_result
):
    results: Dict = await run_standards_validation_tests(
        **data,
        environment=environment,
        components=[component]
    )
    assert results
    dump(results, stderr, indent=4)
