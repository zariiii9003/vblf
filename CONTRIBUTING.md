# Contributing to vblf

Thank you for your interest in contributing to **vblf**! This guide will help you set up your development environment, run tests, ensure code quality, and add changelog entries for your contributions.

## 1. Clone the Repository

First, clone the repository from GitHub:

```bash
git clone https://github.com/zariiii9003/vblf.git
cd vblf
```

- This will create a local copy of the project and move you into the project directory.

## 2. Install Development Dependencies

To get started, install the development dependencies. These include tools for testing, linting, formatting, and documentation.

```bash
python -m pip install -e . --group dev
```

- This command installs the package in editable mode and all dependencies listed under the `dev` group in `pyproject.toml` (including `tox`, `towncrier`, linters, etc.).

## 3. Set Up Pre-commit Hooks

After installing development dependencies, set up pre-commit hooks to automatically check formatting and linting before each commit:

```bash
pre-commit install
```

- This command installs the git hooks defined in `.pre-commit-config.yaml` (if present), so checks like formatting and linting run automatically when you commit.

## 4. Running All Checks and Tests

To run all predefined checks and tests, simply run:

```bash
tox
```

- This will execute all environments defined in `tox.ini`: formatting, linting, type checking, tests, and documentation build. It's the easiest way to ensure your code passes all quality checks before submitting a contribution.

If you want to check only a specific aspect, you can run an individual environment:

- **Formatting:**
  ```bash
  tox -e format
  ```
  Checks code formatting using `ruff`.

- **Linting:**
  ```bash
  tox -e lint
  ```
  Runs `ruff` for linting and code style checks.

- **Type Checking:**
  ```bash
  tox -e type
  ```
  Runs `mypy` for static type checking.

- **Tests:**
  ```bash
  tox -e py
  ```
  Runs all tests using `pytest`.

- **Documentation:**
  ```bash
  tox -e docs
  ```
  Builds the documentation using Sphinx.

## 5. Adding a News Fragment (Changelog Entry)

This project uses [towncrier](https://towncrier.readthedocs.io/) to manage the changelog. For every user-facing change, add a news fragment in the `changelog.d/` directory.

- The filename should be `<issue or PR number>.<type>.md`, e.g., `123.added.md` or `456.fixed.md`. Both issue and pull request numbers are valid.
- Valid types are: `added`, `changed`, `deprecated`, `removed`, `fixed`, `security`.
- Write a short description of your change in the file.

You can create a news fragment manually, or from the command line using towncrier:

```bash
towncrier create -c "Fixed a bug!" 5.fixed.md
```

This will create a file `changelog.d/5.fixed.md` with the provided content.

Example:
```
changelog.d/123.added.md
```
Content:
```
Added support for new BLF message type.
```

When a release is made, these fragments are automatically compiled into `CHANGELOG.md`.

## 6. Submitting Your Contribution

- Ensure your code passes all checks and tests.
- Add a news fragment for your change.
- Open a pull request with a clear description of your changes.

Thank you for helping improve **vblf**!
