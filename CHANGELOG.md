# Change Log

## 0.0.2

- fixes bugs in release 0.0.1, particularly, missing parameters at the CLI level
- Python Logging removed as an explicit parameter (logging assumed configured externally by regular Python, pyproject.toml and environmental variable conventions)

## 0.0.1

- porting of legacy SRI_Testing into OneHopTest and StandardsValidationTest TestRunners in the 2024 Translator Testing framework; this version only currently supports tests test ARA and KP components (not ARS nor UI level).
- The underlying TRAPI standard is still (via reasoner-validator 4.0.0) only to release 1.4.2;
- This release runs on the latest Biolink Model release without choking but the underlying reasoner-validator module doesn't yet do any special validation of the latest Biolink Model semantic features (in 4.1.4 and beyond)
