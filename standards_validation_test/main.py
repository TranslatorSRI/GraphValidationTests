"""
Main TrapiTest Test Runner entry.
(Inspired partially by the design of Benchmarks/benchmarks_runner/main.py)
"""
import asyncio
import os
import tempfile

from one_hop_test.request import fetch_results
from one_hop_test.cli.eval import evaluate_ara_results


async def run_validation_tests(
    test_suite: str,
    target: str,
):
    """Run Standards Validation Test."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = await fetch_results(test_suite, target, tmpdir)
        output_results = []
        if target == 'ars':
            # evaluate results for each ARA in the given ARS query
            for ara in [ara for ara in os.listdir(output_dir) if os.path.isdir(output_dir)]:
                results_dir = os.path.join(output_dir, ara)
                ara_output_result = evaluate_ara_results(test_suite, results_dir, ara)
                output_results.extend(ara_output_result)
        else:
            output_result = evaluate_ara_results(test_suite, output_dir, target)
            output_results.extend(output_result)

    return output_results


if __name__ == "__main__":
    asyncio.run(run_validation_tests(
        #             test_inputs = {
        #                 # from translator_testing_model.datamodel.pydanticmodel import TestEnvEnum
        #                 "environment": environment, # TestEnvEnum
        #                 "components": components,  # List[str], len>0
        #                 "trapi_version": trapi_version,  # str
        #                 "biolink_version": biolink_version,  # str
        #                 "runner_settings": asset.test_runner_settings,  # Optional[List[str]]
        #                 "logger": logger,  # Python logging.Logger
        #
        #                 # One test edge (asset)
        #                 "subject_id": asset.input_id,  # str
        #                 "subject_category": asset.input_category,  # str
        #                 "predicate_id": asset.predicate_id,  # str
        #                 "object_id": asset.output_id,  # str
        #                 "object_category": asset.output_category  # str
        #             }
    ))