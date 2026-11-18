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

Execute all linting, formatting, and build verifications prior to pushing commits:

```bash
# 1. Run Ruff linter
ruff check .

# 2. Run Ruff format check
ruff format --check .

# 3. Verify distribution build
python -m build

# 4. Verify relative markdown links
python3 -c '
import re, glob, os, sys
broken = []
for f in glob.glob("**/*.md", recursive=True):
    content = re.sub(r"```[\s\S]*?```", "", open(f, encoding="utf-8").read())
    content = re.sub(r"`[^`]*`", "", content)
    for link in re.findall(r"\[.*?\]\((?!https?://|mailto:)(.*?)(?:#.*)?\)", content):
        link = link.strip().split("?")[0]
        if not link or link.startswith("#"): continue
        target = os.path.normpath(os.path.join(os.path.dirname(f), link))
        if not os.path.exists(target):
            broken.append(f"{f} -> {link}")
if broken:
    print("Broken links detected:", broken, file=sys.stderr)
    sys.exit(1)
print("Internal documentation links verified.")
'
```

---

## Pull Request Checklist

Before opening a pull request, verify that:

- Commits follow the Conventional Commits specification.
- Local verification commands pass with zero warnings or errors.
- Any new public classes or methods include descriptive docstrings and type annotations.
- Documentation in `README.md` or `docs/` is updated if CLI flags or MCP schemas changed.
- No temporary files, `.env` files, or extraneous dependencies are committed.
