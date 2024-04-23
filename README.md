# Graph Validation Tests

[![Pyversions](https://img.shields.io/pypi/pyversions/reasoner-validator)](https://pypi.python.org/pypi/OneHopTests)
[![Publish Python Package](https://github.com/TranslatorSRI/OneHopTests/actions/workflows/python-publish.yml/badge.svg)](https://pypi.org/project/OneHopTests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Run tests](https://github.com/TranslatorSRI/OneHopTests/actions/workflows/test.yml/badge.svg)](https://github.com/TranslatorSRI/OneHopTests/actions/workflows/test.yml)


This repository provides the implementation of Translator knowledge graph validation test runners within the new 2023 Testing Infrastructure.  The current package currently contains two such test runners:

- **StandardsValidationTest:** is a wrapper of the [Translator reasoner-validator package](https://github.com/NCATSTranslator/reasoner-validator) which certifies that knowledge graph data access is TRAPI compliant and the graph semantic content is Biolink Model compliant.
- **OneHopTest:** is a slimmed down excerpt of "One Hop" knowledge graph navigation unit test code from the legacy [SRI_Testing test harness](https://github.com/TranslatorSRI/SRI_testing), code which validates that single hop TRAPI lookup queries on a Translator knowledge graph, meet basic expectation of input test edge data recovery in the output, using several diverse kinds of templated TRAPI queries. Unlike **SR_Testing**, the **OneHopTest** module retrieves its test data directly from the new [NCATS Translator Tests](https://github.com/NCATSTranslator/Tests) repository. 

Programmatically, the command line or programmatic parameters to each kind of test are identical, but the underlying Test Cases (derived from the source Test Assets) is the same.

## Usage

The **StandardsValidationTest** and **OneHopTest** test runners may be run directly from the command line or programmatically, from within a Python script.

### Installation

The **graph-validation-tests** module can be installed from pypi and used as part of the Translator-wide automated testing.

_Note: Requires 3.9 <= Python release <= 3.12_

#### From Pypi

From within your target working directory:

- Create a python virtual environment: `python -m venv venv`
- Activate your environment: `. ./venv/bin/activate`
- Install dependencies: `pip install graph-validation-tests`

then proceed with [command line execution](#cli) or [script level execution](#programmatic-level-execution).

#### From GitHub

You can also check out the project from GitHub. If you do that, the installation process will be slightly different, since the project itself uses [Poetry](https://python-poetry.org/) for dependency management - the following instructions assume that you've [installed Poetry on your system](https://python-poetry.org/docs/#installation).

- Check out the code: `git checkout https://github.com/TranslatorSRI/graph-validation-tests.git`
- Create a Poetry shell: `poetry shell`
- Install dependencies: `poetry install`

then proceed with [command line execution](#cli) or [script level execution](#programmatic-level-execution).

### CLI

Within a command line terminal, type:

```shell
$ standards_validation_test --help
```
or

```shell
$ one_hop_test --help
```

should give usage instructions as follows (where <tool name> is either 'standards_validation_test' or 'one_hop_test'):

```shell
usage: <tool name> [-h] [--components COMPONENTS] [--environment {dev,ci,test,prod}] --subject_id SUBJECT_ID --predicate_id PREDICATE_ID
                                 --object_id OBJECT_ID [--trapi_version TRAPI_VERSION] [--biolink_version BIOLINK_VERSION]
                                 [--log_level {ERROR,WARNING,INFO,DEBUG}]

Translator TRAPI and Biolink Model Validation of Knowledge Graphs

options:
  -h, --help            show this help message and exit
  --components COMPONENTS
                        Names Translator components to be tested taken from the Translator Testing Model 'ComponentEnum' 
                        (may be a comma separated string of such names; default: run the test against the 'ars')
  --environment {dev,ci,test,prod}
                        Translator execution environment of the Translator Component targeted for testing.
  --subject_id SUBJECT_ID
                        Statement object concept CURIE
  --predicate_id PREDICATE_ID
                        Statement Biolink Predicate identifier
  --object_id OBJECT_ID
                        Statement object concept CURIE
  --trapi_version TRAPI_VERSION
                        TRAPI version expected for knowledge graph access (default: use current default release)
  --biolink_version BIOLINK_VERSION
                        Biolink Model version expected for knowledge graph access (default: use current default release)
```

### Programmatic Level Execution

### Standards Validation Test

To run TRAPI and Biolink Model validation tests validating query outputs from a knowledge graph TRAPI component:

```python
from typing import Dict
import asyncio
from translator_testing_model.datamodel.pydanticmodel import ComponentEnum
from standards_validation_test import run_standards_validation_tests

test_data = {
    # One test edge (asset)
    "subject_id": "DRUGBANK:DB01592",
    "subject_category": "biolink:SmallMolecule",
    "predicate_id": "biolink:has_side_effect",
    "object_id": "MONDO:0011426",
    "object_category": "biolink:Disease",
    "components": [
            ComponentEnum("arax"),
            ComponentEnum("molepro")
    ]
    # "environment": environment, # Optional[TestEnvEnum] = None; default: 'TestEnvEnum.ci' if not given
    # "trapi_version": trapi_version,  # Optional[str] = None; latest community release if not given
    # "biolink_version": biolink_version,  # Optional[str] = None; current Biolink Toolkit default if not given
    # "runner_settings": asset.test_runner_settings,  # Optional[List[str]] = None
}
results: Dict = asyncio.run(run_standards_validation_tests(**test_data))
print(results)
```

### OneHopTest

To run "One Hop" knowledge graph navigation tests validating query outputs from a knowledge graph TRAPI component:

```python
from typing import Dict
import asyncio
from translator_testing_model.datamodel.pydanticmodel import ComponentEnum
from one_hop_test import run_one_hop_tests

test_data = {
    # One test edge (asset)
    "subject_id": "DRUGBANK:DB01592",
    "subject_category": "biolink:SmallMolecule",
    "predicate_id": "biolink:has_side_effect",
    "object_id": "MONDO:0011426",
    "object_category": "biolink:Disease",
    "components": [
            ComponentEnum("arax"),
            ComponentEnum("molepro")
    ]
    #
    #     "environment": environment, # Optional[TestEnvEnum] = None; default: 'TestEnvEnum.ci' if not given
    #     "trapi_version": trapi_version,  # Optional[str] = None; latest community release if not given
    #     "biolink_version": biolink_version,  # Optional[str] = None; current Biolink Toolkit default if not given
    #     "runner_settings": asset.test_runner_settings,  # Optional[List[str]] = None
}
results: Dict = asyncio.run(run_one_hop_tests(**test_data))
print(results)
```

The above wrapper method runs all related TestCases derived from the specified TestAsset (i.e. subject_id, etc.) without any special test parameters. If more fine-grained testing is desired, a subset of the underlying TRAPI queries can be run directly, something like this (here, we ignore the TestCases 'by_subject', 'inverse_by_new_subject' and 'by_object', and specify the 'strict_validation' parameter of True to Biolink Model validation, as understood by the **reasoner-validator** code running behind the scenes):

```python
from typing import Dict
import asyncio
from standards_validation_test import StandardsValidationTest
from translator_testing_model.datamodel.pydanticmodel import TestEnvEnum, ComponentEnum
from graph_validation_test.utils.unit_test_templates import (
    # by_subject,
    # inverse_by_new_subject,
    # by_object,
    raise_subject_entity,
    raise_object_entity,
    raise_object_by_subject,
    raise_predicate_by_subject
)

test_data = {
    # One test edge (asset)
    "subject_id": "DRUGBANK:DB01592",
    "subject_category": "biolink:SmallMolecule",
    "predicate_id": "biolink:has_side_effect",
    "object_id": "MONDO:0011426",
    "object_category": "biolink:Disease",
    "components": [
            ComponentEnum("arax"),
            ComponentEnum("molepro")
    ],
    "environment": TestEnvEnum.test,
    "trapi_version": "1.5.0-beta",
    "biolink_version": "4.1.6",
    "runner_settings": "Inferred"
}
trapi_generators = [
    # by_subject,
    # inverse_by_new_subject,
    # by_object,
    raise_subject_entity,
    raise_object_entity,
    raise_object_by_subject,
    raise_predicate_by_subject
]

# A test runner specific parameter passed through
kwargs = {
    "strict_validation": True
}
results: Dict = asyncio.run(StandardsValidationTest.run_tests(
    **test_data, trapi_generators=trapi_generators, **kwargs)
)
```

Note that the trapi_generation variables - defined in the **graph_validation_test.utils.unit_test_templates** module - are all simply Python functions returning TRAPI JSON messages to send to the target components. In principle, if one understands what those functions are doing, you could write your own methods to do other kinds of TRAPI queries whose output can then be validated against the specified TRAPI and Biolink Model releases.

### Sample Output

This is a sample of what the JSON output from test runs currently looks like (this sample came from a OneHopTest run).

```json
{    
    "pks": {
        "molepro": "molepro"
    },
    "results": {
        "TestAsset_1-by_subject": {
            "molepro": [
                "FAILED",
                {
                    "error": {
                        "error.trapi.response.knowledge_graph.missing_expected_edge": {
                            "global": {
                                "TestAsset_1|(CHEBI:58579#biolink:SmallMolecule)-[biolink:is_active_metabolite_of]->(UniProtKB:Q9NQ88#biolink:Protein)": null
                            }
                        }
                    }
                }
            ]
        },
        "TestAsset_1-inverse_by_new_subject": {
            "molepro": [
                "FAILED",
                {
                    "critical": {
                        "critical.trapi.request.invalid": {
                            "global": {
                                "predicate 'biolink:is_active_metabolite_of'": [
                                    {
                                        "context": "inverse_by_new_subject",
                                        "reason": "is an unknown or has no inverse?"
                                    }
                                ]
                            }
                        }
                    }
                }
            ]
        },
        "TestAsset_1-by_object": {
            "molepro": [
                "FAILED",
                {
                    "error": {
                        "error.trapi.response.knowledge_graph.missing_expected_edge": {
                            "global": {
                                "TestAsset_1|(CHEBI:58579#biolink:SmallMolecule)-[biolink:is_active_metabolite_of]->(UniProtKB:Q9NQ88#biolink:Protein)": null
                            }
                        }
                    }
                }
            ]
        },
        "TestAsset_1-raise_subject_entity": {
            "molepro": [
                "FAILED",
                {
                    "critical": {
                        "critical.trapi.request.invalid": {
                            "global": {
                                "subject 'CHEBI:58579[biolink:SmallMolecule]'": [
                                    {
                                        "context": "raise_subject_entity",
                                        "reason": "has no 'is_a' parent since it is either not an ontology term or does not map onto a parent ontology term."
                                    }
                                ]
                            }
                        }
                    }
                }
            ]
        },
        "TestAsset_1-raise_object_entity": {
            "molepro": [
                "FAILED",
                {
                    "critical": {
                        "critical.trapi.request.invalid": {
                            "global": {
                                "object 'UniProtKB:Q9NQ88[biolink:Protein]'": [
                                    {
                                        "context": "raise_object_entity",
                                        "reason": "has no 'is_a' parent since it is either not an ontology term or does not map onto a parent ontology term."
                                    }
                                ]
                            }
                        }
                    }
                }
            ]
        },
        "TestAsset_1-raise_object_by_subject": {
            "molepro": [
                "FAILED",
                {
                    "error": {
                        "error.trapi.response.knowledge_graph.missing_expected_edge": {
                            "global": {
                                "TestAsset_1|(CHEBI:58579#biolink:SmallMolecule)-[biolink:is_active_metabolite_of]->(UniProtKB:Q9NQ88#biolink:Protein)": null
                            }
                        }
                    }
                }
            ]
        },
        "TestAsset_1-raise_predicate_by_subject": {
            "molepro": [
                "FAILED",
                {
                    "critical": {
                        "critical.trapi.request.invalid": {
                            "global": {
                                "predicate 'biolink:is_active_metabolite_of'": [
                                    {
                                        "context": "raise_predicate_by_subject",
                                        "reason": "has no 'is_a' parent"
                                    }
                                ]
                            }
                        }
                    }
                }
            ]
        }
    }
}
```

## Releases

A [full change log](CHANGELOG.md) is provided documenting each release, but we summarize key release limitations here:

### v0.0.\* Releases

- This initial code release only supports testing of [Translator SmartAPI Registry](https://smart-api.info/registry/translator) catalogued components which are TRAPI implementations for Translator Autonomous Relay Agent (ARA) and Knowledge Providers (KP), but _not_ direct testing of the Translator Autonomous Relay System (ARS) or Translator user interface (UI)
- Standards validation tests currently calls release 4.0.0 of the [reasoner-validator](https://github.com/NCATSTranslator/reasoner-validator), which is currently limited to TRAPI release 1.4.2 validation (not yet the recent TRAPI 1.5.0 releases)
