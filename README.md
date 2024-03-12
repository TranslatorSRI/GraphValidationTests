
# GraphValidationTests

[![Pyversions](https://img.shields.io/pypi/pyversions/reasoner-validator)](https://pypi.python.org/pypi/OneHopTests)
[![Publish Python Package](https://github.com/TranslatorSRI/OneHopTests/actions/workflows/python-publish.yml/badge.svg)](https://pypi.org/project/OneHopTests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Run tests](https://github.com/TranslatorSRI/OneHopTests/actions/workflows/test.yml/badge.svg)](https://github.com/TranslatorSRI/OneHopTests/actions/workflows/test.yml)


This repository provides the implementation of some Translator knowledge graph validation Test Runners within the new 2023 Testing Infrastructure, specifically:

- **StandardsValidationTest:** is a wrapper of the [Translator reasoner-validator package](https://github.com/NCATSTranslator/reasoner-validator) which certifies that knowledge graph data access is TRAPI compliant and the graph semantic content is Biolink Model compliant.
- **OneHopTest:** is a slimmed down excerpt of "One Hop" knowledge graph navigation unit test code from the legacy [SRI_Testing test harness](https://github.com/TranslatorSRI/SRI_testing), code which validates that single hop TRAPI lookup queries on a Translator knowledge graph, meet basic expectation of input test edge data recovery in the output, using several diverse kinds of templated TRAPI queries. Unlike **SR_Testing**, the **OneHopTest** module retrieves its test data directly from the new [NCATS Translator Tests](https://github.com/NCATSTranslator/Tests) repository. 

## Getting Started

The **GraphValidationTests** module can be installed from pypi and used as part of the Translator-wide automated testing.

- `pip install GraphValidationTests`

## StandardsValidationTest

To run TRAPI and Biolink Model validation tests of a knowledge graph component:

```python
import asyncio
from standards_validation_test import run_validation_test

test_data = {
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
}
output = asyncio.run(run_validation_test(**test_data))
```

## OneHopTest

To run "One Hop" knowledge graph navigation tests:

```python
import asyncio
from one_hop_test import run_one_hop_test

test_data = {
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
}
output = asyncio.run(run_one_hop_test(**test_data))
```

### Sample Output

```json
{
  "Results": "<tba>"
}
```
