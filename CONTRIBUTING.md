# Contributing to stock-fetcher

This document details guidelines for submitting code changes, reporting defects, and proposing features for `stock-fetcher`.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Development Setup](#development-setup)
- [Branching Strategy](#branching-strategy)
- [Commit Message Specification](#commit-message-specification)
- [Verification Commands](#verification-commands)
- [Pull Request Checklist](#pull-request-checklist)

---

## Code of Conduct

Maintain professional, technical communication in all issues, pull requests, and review discussions.

---

## Development Setup

Requirements:
- Python 3.10 or higher.
- `git`.

Clone the repository and install all development dependencies:

```bash
git clone https://github.com/AtaCanYmc/stock-fetcher.git
cd stock-fetcher
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev,all]"
pre-commit install
```

---

## Branching Strategy

Create topical branches off the latest `main` branch using standard prefixes:

- `feat/`: New capability or provider client.
- `fix/`: Defect remediation or bug fix.
- `docs/`: Documentation additions or clarifications.
- `refactor/`: Code reorganization without behavioral modifications.
- `chore/`: CI, dependencies, or tooling maintenance.

Example:

```bash
git checkout -b feat/wikimedia-provider
```

---

## Commit Message Specification

All commit messages must adhere to the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```text
<type>(<scope>): <short description>

[optional body]

[optional footer(s)]
```

### Allowed Types

- `feat`: A new feature or provider implementation.
- `fix`: A bug fix.
- `docs`: Documentation changes only.
- `style`: Changes that do not affect the meaning of the code.
- `refactor`: A code change that neither fixes a bug nor adds a feature.
- `perf`: A code change that improves performance.
- `test`: Adding missing tests or correcting existing tests.
- `chore`: Changes to build processes, auxiliary tools, or libraries.

Example:

```text
feat(clients): add Flickr scrapper response parser validation
```

---

## Verification Commands

Execute all linting, formatting, and link verifications prior to pushing commits. You can run all checks via `make`:

```bash
make check
```

Or execute individual steps:

```bash
# 1. Run Ruff linter
make lint

# 2. Run Ruff format check
make format-check

# 3. Verify internal markdown links
make validate-links

# 4. Verify distribution build
make build
```

---

## Pull Request Checklist

Before opening a pull request, verify that:

- Commits follow the Conventional Commits specification.
- Local verification commands pass with zero warnings or errors.
- Any new public classes or methods include descriptive docstrings and type annotations.
- Documentation in `README.md` or `docs/` is updated if CLI flags or MCP schemas changed.
- No temporary files, `.env` files, or extraneous dependencies are committed.
