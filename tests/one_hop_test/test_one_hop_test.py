"""
Unit tests for One Hop Test code validation
"""
from sys import stdout, stderr
from typing import Dict
from json import dump
import subprocess
import pytest

from graph_validation_test.utils.unit_test_templates import (
    by_subject,
    inverse_by_new_subject,
    by_object,
    raise_subject_entity,
    raise_object_entity,
    raise_object_by_subject,
    raise_predicate_by_subject
)
from one_hop_test import OneHopTest, run_one_hop_tests
from tests import SAMPLE_TEST_INPUT_1, SCRIPTS_DIR


@pytest.mark.asyncio
async def test_one_hop_test():
    trapi_generators = [
        by_subject,
        inverse_by_new_subject,
        by_object,
        raise_subject_entity,
        raise_object_entity,
        raise_object_by_subject,
        raise_predicate_by_subject
    ]
    results: Dict = await OneHopTest.run_tests(
        **SAMPLE_TEST_INPUT_1,
        trapi_generators=trapi_generators,
        environment="prod",
        components=["arax", "molepro"]
    )
    dump(results, stderr, indent=4)


# ARS tests not yet supported so yes... results will
# always be empty, with a logger message to inform why
@pytest.mark.asyncio
async def test_one_hop_test_of_ars():
    trapi_generators = [
        by_subject,
        inverse_by_new_subject,
        by_object,
        raise_subject_entity,
        raise_object_entity,
        raise_object_by_subject,
        raise_predicate_by_subject
    ]
    results: Dict = await OneHopTest.run_tests(
        **SAMPLE_TEST_INPUT_1,
        trapi_generators=trapi_generators,
        environment="prod"
    )
    assert not results


@pytest.mark.asyncio
async def test_run_one_hop_tests():
    results: Dict = await run_one_hop_tests(
        **SAMPLE_TEST_INPUT_1,
        environment="prod",
        components=["arax", "molepro"]
    )
    assert results
    dump(results, stderr, indent=4)


@pytest.mark.asyncio
async def test_run_one_hop_tests_with_runner_parameters():
    results: Dict = await run_one_hop_tests(
        **SAMPLE_TEST_INPUT_1,
        environment="prod",
        components=["arax", "molepro"],
        strict_validation=True
    )
    assert results
    dump(results, stderr, indent=4)


# subprocess.run(
#     args, *, stdin=None, input=None, stdout=None, stderr=None,
#     capture_output=False, shell=False, cwd=None, timeout=None,
#     check=False, encoding=None, errors=None, text=None, env=None,
#     universal_newlines=None, **other_popen_kwargs
# )
@pytest.mark.skip("Not yet fully implemented")
def test_one_hop_cli():
    # command: List = ["python", "-m", "one_hop_test.__init__"]
    # args: Dict = SAMPLE_TEST_INPUT_1.copy()
    # args["components"] = "arax,molepro"
    # [command.extend([f"--{flag}", value]) for flag, value in args.items()]
    # results = check_output(["dir"])
    # results = check_output([
    #     "python", "-m", "venv", "--clear", "test_venv", ";",
    #     ".", "test_venv/bin/activate"
    # ])
    subprocess.run("one_hop_test", stdout=stdout, shell=True, cwd=SCRIPTS_DIR)
