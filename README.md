# OneHopTests

[![Pyversions](https://img.shields.io/pypi/pyversions/reasoner-validator)](https://pypi.python.org/pypi/OneHopTests)
[![Publish Python Package](https://github.com/TranslatorSRI/OneHopTests/actions/workflows/python-publish.yml/badge.svg)](https://pypi.org/project/OneHopTests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Run tests](https://github.com/TranslatorSRI/OneHopTests/actions/workflows/test.yml/badge.svg)](https://github.com/TranslatorSRI/OneHopTests/actions/workflows/test.yml)


This repository encodes a "One Hop" TestRunner for the new 2023 Testing Infrastructure. The OneHopTest module tests basic knowledge graph (KG) navigation using known subject:category-predicate-object:category test asset data.

The original testing functionality is adapted from the [SRI_Testing](https://github.com/TranslatorSRI/SRI_testing) test harness.   Unlike **SR_Testing**, the **OneHopTest** module retrieves its test data directly from the new [NCATS Translator Tests](https://github.com/NCATSTranslator/Tests) repository.   Also, full [reasoner_validator](https://github.com/NCATSTranslator/reasoner-validator) validation of TRAPI and Biolink Model compliance is **_not_** attempted.

## OneHopTest Runner

The OneHopTest module can be installed from pypi and used as part of the Translator-wide automated testing.
- `pip install OneHopTests`

To run One Hop Tests:

```python
import asyncio
from one_hop_tests import run_onehop_tests
input_data = {
        # subject_id: str,
        # subject_category: str,
        # predicate_id: str,
        # object_id: str,
        # object_category: str,
        # components: Optional[str] = None,
        # environment: Optional[str] = None,
        # trapi_version: Optional[str] = None,
        # biolink_version: Optional[str] = None,
        # runner_settings: Optional[Dict[str, str]] = None,
        # log_level: Optional[str] = None
}
output = asyncio.run(run_onehop_tests(**input_data))
```
where test_suite is the name of a Test Suite declared in the [NCATS Translator Tests](https://github.com/NCATSTranslator/Tests) repository, 
and a target that is specified in config/targets.json

### Sample Output

```json
{
  "Results": "<tba>"
}
```