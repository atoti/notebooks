We welcome any contributions from the community. Please make sure your PR follows the rules below:

### General notebook rules

- folders and files name should be lowercase with hyphen.

  Example: `name-of-my-folder-or-file`

- notebook example should be put inside a folder which name is the notebook's title. This folder should be located under a specific "domain" folder.

  Example: `/relevant-domain/title-of-my-notebook-folder/`

- entrypoint should be named `main.ipynb`
- README TOC should be updated to link to the new notebook
- notebook should have an H1 title, matching folder name and README TOC

### Data rules

- data files name should use snake_case
- data files should be of reasonnable size, not exceeding 50MB, unless programmatically generated
- all data files should be uploaded on data.atoti.io If you don't have access to it, data should be hosted on a public host and an owner will transfer them to data.atoti.io upon review

### Python code rules

- variables should follow Google's [naming convention](http://google.github.io/styleguide/pyguide.html#316-naming)
- python files should be formatted with [Black](https://black.readthedocs.io/en/stable/)
- python methods should be typed
- documentation should follow Google's [docstring](http://google.github.io/styleguide/pyguide.html#381-docstrings)

### Testing and CI

This repository is tested with a [Github Action](.github/workflows/test.yaml).

These commands can be used while developing:

- Reformat python files using black :

  ```bash
  poetry run black .
  ```

- Reformat notebooks using black-nb :

  ```bash
  poetry run black-nb notebooks/
  ```

- Execute all the notebooks:

  ```bash
  poetry run python tests/execute_notebooks.py
  ```

### How to write a notebook

1. Pull the `master` branch (`git checkout master` and `git pull`).
2. Run `poetry install` to be in the latest defined environment.
3. Create the working branch `git checkout -b <PSEUDO>/<SUBJECT>`.
4. Start jupyter-lab `poetry run jupyter-lab`.
5. Create the folder and notebooks, add notebooks to process data to the list of untested notebooks, only **notebooks using atoti MUST be tested**.
6. If a dependency is missing run `poetry add <DEPENDENCY_NAME>`: **DEPENDENCIES MUST NOT BEEN ADDED WITH CONDA OR PIP** since the Github CI is relying on the `poetry.lock` file to install dependencies.
7. Push changes using `git push` and create the related pull request.

### About

Checkout [atoti.io](https://www.atoti.io) for more info!

By opening an issue or a pull request, you agree with atoti's [terms of use](https://www.atoti.io/terms) and [privacy policy](https://www.atoti.io/privacy-policy).
