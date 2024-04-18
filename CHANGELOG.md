# Change Log

## 0.0.6

- Moved, into inside of **`graph_validation_test.get_parameters()`** method, the string parsing of CLI comma-delimited components parameter to the **`List[ComponentEnum]`** now expected as the **`components`** parameter of the **`graph_validation_test.run_tests()`** method.

## 0.0.5

- Belated upgrade to TranslatorTestingModel release 0.2.6
- Fix sample data to more credible predicate
- Tweak unit test environments to match current deployment reality
- Reactivate skipped unit tests after updating some url's to currently active endpoints

## 0.0.4 (package bug fix; deprecates v0.0.3 in pypi - yanked)

- Added missing 'graph_validation_test' to the release

## 0.0.3

- co-routine management of co-routine processing pushed up to a top level 'asyncio.run' of the highest level (now 'async') method, converting processing underneath to await runs on async methods, down to the lowest level parallel processing of co-routines of test cases
- Some Ontology KP graph and Translator endpoing access unit tests are temporarily skipped (endpoints offline on release day?)

## 0.0.2

- fixes bugs in release 0.0.1, particularly, missing parameters at the CLI level
- Python Logging removed as an explicit parameter (logging assumed configured externally by regular Python, pyproject.toml and environmental variable conventions)

## 0.0.1

- porting of legacy SRI_Testing into OneHopTest and StandardsValidationTest TestRunners in the 2024 Translator Testing framework; this version only currently supports tests test ARA and KP components (not ARS nor UI level).
- The underlying TRAPI standard is still (via reasoner-validator 4.0.0) only to release 1.4.2;
- This release runs on the latest Biolink Model release without choking but the underlying reasoner-validator module doesn't yet do any special validation of the latest Biolink Model semantic features (in 4.1.4 and beyond)
