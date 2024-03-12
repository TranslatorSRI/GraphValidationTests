# GraphValidationTests

This repository provides the implementation of some Translator knowledge graph validation Test Runners within the new 2023 Testing Infrastructure, specifically:

- **StandardsValidationTest:** is a wrapper of the [Translator reasoner-validator package](https://github.com/NCATSTranslator/reasoner-validator) which certifies that knowledge graph data access is TRAPI compliant and the graph semantic content is Biolink Model compliant.
- **OneHopTest:** is a slimmed down excerpt of "One Hop" knowledge graph navigation unit test code from the SRI_Testing harness, which validates that single hop TRAPI lookup queries on a Translator knowledge graph, meet the basic expectation that input test edge data are recovered in the output.
