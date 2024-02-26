# Developer Notes

These notes are only of interest to developers maintaining this repository.

## Maintaining Dependencies

This project uses the [poetry dependency management](https://python-poetry.org) tool to orchestrate its installation and dependencies. As such, new or revised Python module dependencies are curated within the **pyproject.toml** file.

## Project Releases

Steps to properly issue a new project release:

1. Run the unit test suite to ensure that nothing fails. Iterate to fix failures (in the code or in terms of revised unit tests to reflect fresh code designs)
2. Document release changes in the **CHANGELOG.md**
3. Update the **`[Tool Poetry]version =`** field in the **pyprojects.yaml**, e.g. "0.0.2"
4. Run **`poetry update`** (preferably within  **`poetry shell`**)
5. Commit or pull request merge all files (including the **poetry.lock** file) to **master**
6. Add the equivalent Git **tag** to **master**. This should be the Semantic Version string from step 4 with an added 'v' prefix, i.e. "v3.9.5".
7. Push **master** to remote (if not already done with by a pull request in step 5).
8.  Check if Git Actions for testing and documentation complete successfully.
9. Create the release using the same release tag, i.e. "v3.9.5".
10. Check if Git Action for package deployment is successful and check if the new version (i.e. "0.0.2") is now visible on **[pypy.org](https://pypi.org/search/?q=OneHopTests)**
