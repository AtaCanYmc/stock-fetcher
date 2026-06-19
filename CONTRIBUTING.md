# Contributing to Stock Fetcher

First off, thank you for considering contributing to `stock-fetcher`! We welcome contributions from everyone—whether it's adding a new provider, fixing a bug, or improving the documentation.

## Getting Started

1. **Fork & Clone:** Fork the repository on GitHub and clone it to your local machine.
2. **Environment:** Ensure you have Python 3.10 or newer installed. We recommend using a virtual environment (`.venv`).
3. **Installation:** Install the package in editable mode along with all optional dependencies:
   ```bash
   pip install -e ".[all]"
   ```
4. **Pre-commit Hooks:** We use `pre-commit` to ensure code quality and formatting via `ruff`. Install the hooks in your local repository:
   ```bash
   pre-commit install
   ```

## Development Workflow

1. **Branching:** Create a new branch for your feature or bug fix:
   ```bash
   git checkout -b feature/my-awesome-feature
   ```
2. **Making Changes:** Make your changes in the `src/stock_fetcher/` directory.
   - *Adding a new provider?* Ensure it inherits from `BaseFetcher`, implements the `search` method, and is registered in `ClientFactory`.
3. **Examples & Docs:** Add or update usage examples in the `examples/` folder and update the `docs/` if you introduce new CLI commands or MCP tools.
4. **Committing:** Commit your changes. `pre-commit` will automatically run Ruff to format and lint your code. If the checks fail, fix the issues and stage/commit again.

## Pull Requests

- Keep your pull requests focused on a single issue or feature.
- Provide a clear, detailed description of the problem you are solving and how you approached the solution.
- If your PR introduces a breaking change (e.g., changing the `BaseFetcher` interface), please highlight it explicitly in the PR description.

Thank you for helping us make `stock-fetcher` better!
