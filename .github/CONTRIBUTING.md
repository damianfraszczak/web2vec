# Contributing to Web2Vec

We warmly welcome contributions to Web2Vec! This document provides guidelines for contributing to this project. By participating in this project, you agree to abide by its terms.

## Table of Contents
- [How to Contribute](#how-to-contribute)
- [Local Development Setup](#local-development-setup)
- [Releasing a New Version](#releasing-a-new-version)
- [Pre-commit Hooks](#pre-commit-hooks)

## How to Contribute

### Reporting Bugs and Requesting Features

- **Bug Reports**: Please use the [Bug Report Template](.github/ISSUE_TEMPLATE/bug_report.md) to report any bugs. Provide as much detail as possible to help us understand and fix the issue.
- **Feature Requests**: For proposing new features or enhancements, use the [Feature Request Template](.github/ISSUE_TEMPLATE/feature_request.md). Describe the feature, its benefits, and possible implementation if you have one in mind.

### Coding Style

- **PEP 8**: All Python code must adhere to the [PEP 8 style guide](https://www.python.org/dev/peps/pep-0008/), except where explicitly mentioned.
- **Comments and Docstrings**: Use comments and docstrings to explain the purpose of complex code blocks. Follow the [PEP 257](https://www.python.org/dev/peps/pep-0257/) docstring conventions.

### Implementation Requirements

- **Source Detection Method Implementation**:
  - Each new method must be implemented in a separate file within the `web2vec/algorithms` directory in appropriate package according to its intended purpose e.g. reconstruction algorithm should be placed in `reconstruction` package.
  - The file name should match the method's name.
  - Each file must contain a single function, named after the new method name.
  - Each alg function must be exposed in the `web2vec/algorithms` package to be accessible for external use.
  - Add an entry for the new alg in the appropiate taxonomy class, e.g. for reconstruction algorithm new entry should be placed into `PropagationReconstructionAlgorithm` enum to ensure it's recognized and accessible through a standardized interface.

- **Testing**:
  - Contributions must include tests covering the new functionality. We require at least 80% test coverage for changes.
  - Use the `pytest` framework for writing tests.

- **Documentation**:
  - Update the project documentation to reflect the addition of new method or any other significant changes.
  - Ensure that examples, usage guides, and API documentation are clear and updated.

### Making Changes

1. **Create an Issue**: For every change, whether a bug fix or a feature implementation, please open a new issue. This helps us keep track of what's being worked on and discuss potential changes before the development work starts.
2. **Follow the Style Guide and Contribution Requirements**: Adhere to the [Coding Style](#coding-style) and [Contribution Requirements](#contribution-requirements).
3. **Use Pre-commit Hooks**: This project uses pre-commit hooks to ensure code style and quality. Run `pre-commit install` after cloning the repository to set up the hooks locally. For more, check [Pre-commit Hooks](#pre-commit-hooks).
4. **Submit a Pull Request**: Once you're ready, submit a pull request linked to the issue you've created. Describe your changes clearly in the PR description.


## Local development setup

By default venv is used to work on the project. After creating venv, install the requirements:

```bash
pip install -r requirements.txt
pip install -r requirements.dev.txt
```
and you are ready to go.

## Release a version

- Merge your PR into **`main`**
- Update changelog in CHANGELOG.md
- Change the version in src/web2vec/version.py
- Commit. `git commit -m 'Release version x.y.z'`
- Tag the commit. `git tag -a x.y.z -m 'Release version x.y.z'`
- Push (do not forget --tags). `git push origin master --tags`
- Release will be created automatically by GitHub Actions


## Pre-commit Hooks

This project supports [**pre-commit**](https://pre-commit.com/). To use it please install it
in the `pip install pre-commit` and then run `pre-commit install` and you are ready to go.
Bunch of checks will be executed before commit and files will be formatted correctly.

Pre-commit works on staged files while commiting. To run it without a command one should run `pre-commit run`. Changes has to be staged.

To run pre-commit hooks on all changes in the branch:

1.  Sync branch with main
1.  Run `git diff --name-only --diff-filter=MA origin/master | xargs pre-commit run --files`

For branches that are not based on `master` you might replace `origin/master` with `origin/{your_branch}`

## Generating documentation
### Source files
In docs/source directory
```shell
sphinx-apidoc -o . ../../src -f -e
```
