# Developer Notes

These notes are only of interest to developers maintaining this repository.

## Maintaining Dependencies

This project uses the [poetry dependency management](https://python-poetry.org) tool to orchestrate its installation and dependencies. As such, new or revised Python module dependencies are curated within the **pyproject.toml** file.

## Project Releases

Steps to properly issue a new project release:

1. Run the unit test suite to ensure that nothing fails. Iterate to fix failures (in the code or in terms of revised unit tests to reflect fresh code designs)
2. Document release changes in the **CHANGELOG.md**
3. Update the **`[Tool Poetry]version =`** field in the **pyprojects.yaml**, e.g. "0.0.4"
4. Run **`poetry update`** (preferably, within a **`poetry shell`**)
5. The project pip **requirements.txt** file snapshot of dependencies should also be updated at this point (type **`$ poetry export --output requirements.txt`**, assuming that the [proper poetry export plugin is installed](https://python-poetry.org/docs/pre-commit-hooks#poetry-export)). This may facilitate module deployment within environments that prefer to use pip rather than poetry to manage their deployments.
6. Commit or pull request merge all files (including the **poetry.lock** file) to the local **main** branch.
7. Add the equivalent Git **tag** to **main**. This should be the Semantic Version string from step 4 with an added 'v' prefix, i.e. "v0.0.4".
8. Push **main** to remote.
9. Check if Git Actions for testing and documentation complete successfully.
10. Create a Git package release using the same release tag, i.e. "v0.0.4".
11. Check if Git Actions for package deployment is successful and check if the new version (i.e. "v0.0.4") is now visible on **[pypy.org](https://pypi.org/search/?q=OneHopTests)**
