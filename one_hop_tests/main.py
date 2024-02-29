"""
Main OneHopTest Test Runner entry.
(Inspired partially by the design of Benchmarks/benchmarks_runner/main.py)
"""
import asyncio
import os
import tempfile

from one_hop_tests.request import fetch_results
from one_hop_tests.cli.eval import evaluate_ara_results


async def one_hop_tests(
    test_suite: str,
    target: str,
):
    """Run OneHopTests."""
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
    asyncio.run(one_hop_tests(
        "one_hop_tests",
        "aragorn",
    ))