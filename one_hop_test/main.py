"""
Main OneHopTest Test Runner entry.
(Inspired partially by the design of Benchmarks/benchmarks_runner/main.py)
"""
import asyncio
import os
import tempfile

from graph_validation_test.request import fetch_results
from benchmarks.cli.eval import evaluate_ara_results


async def run_one_hop_test(
    test_suite: str,
    target: str,
):
    """Run OneHopTest."""
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
    asyncio.run(run_one_hop_test(
        # test_inputs = {
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
        #
        # }
    ))
