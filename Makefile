.PHONY: help install install-dev lint lint-fix format format-check build clean check validate-links

PYTHON ?= python3

define VALIDATE_LINKS_PY
import re, glob, os, sys
broken = []
for f in glob.glob("**/*.md", recursive=True):
    content = re.sub(r"```[\s\S]*?```", "", open(f, encoding="utf-8").read())
    content = re.sub(r"`[^`]*`", "", content)
    for link in re.findall(r"\[.*?\]\((?!https?://|mailto:)(.*?)(?:#.*)?\)", content):
        link = link.strip().split("?")[0]
        if not link or link.startswith("#"):
            continue
        target = os.path.normpath(os.path.join(os.path.dirname(f), link))
        if not os.path.exists(target):
            broken.append(f"{f} -> {link}")
if broken:
    print("Broken markdown links detected:", broken, file=sys.stderr)
    sys.exit(1)
print("All markdown links verified.")
endef
export VALIDATE_LINKS_PY

help:
	@echo "Available targets:"
	@echo "  install         Install package in editable mode"
	@echo "  install-dev     Install package with dev and optional dependencies"
	@echo "  lint            Run Ruff linter"
	@echo "  lint-fix        Run Ruff linter with auto-fix"
	@echo "  format          Format codebase using Ruff"
	@echo "  format-check    Verify formatting without modifying files"
	@echo "  build           Build sdist and wheel distributions"
	@echo "  clean           Remove build and cache artifacts"
	@echo "  validate-links  Verify relative internal markdown links"
	@echo "  check           Run linting, formatting check, and link validation"

install:
	$(PYTHON) -m pip install -e .

install-dev:
	$(PYTHON) -m pip install -e ".[dev,all]"
	pre-commit install

lint:
	ruff check .

lint-fix:
	ruff check --fix .

format:
	ruff format .

format-check:
	ruff format --check .

build:
	$(PYTHON) -m pip install --upgrade build
	$(PYTHON) -m build

validate-links:
	@$(PYTHON) -c "$$VALIDATE_LINKS_PY"

check: lint format-check validate-links

clean:
	rm -rf build/ dist/ src/*.egg-info *.egg-info .pytest_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
