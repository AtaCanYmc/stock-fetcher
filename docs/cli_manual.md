# Stock Fetcher CLI Manual

The Stock Fetcher Command Line Interface (CLI) allows you to search for copyright-free images directly from your terminal. It outputs the results in a clean, readable table format.

## Installation

To use the CLI, ensure you install the package with the `cli` extra:

```bash
pip install 'stock-fetcher[cli]'
```

## Basic Usage

The primary command is `search`.

```bash
stock-fetcher search [OPTIONS] PROVIDER TERM
```

### Arguments

- **`PROVIDER`**: The image source to use. Available options: `pexels`, `pixabay`, `unsplash`, `flickr`.
- **`TERM`**: The search query (e.g., `"nature"`, `"cyberpunk city"`).

### Options

- **`--limit INTEGER`**: Maximum number of images to fetch (Default: `5`).
- **`--api-key TEXT`**: API key for the provider. If omitted, the CLI will look for environment variables.
- **`--help`**: Show this message and exit.

## Environment Variables

Instead of passing the API key via the `--api-key` flag every time, you can export it to your environment. The CLI automatically looks for variables following the `<PROVIDER>_API_KEY` pattern:

- `PEXELS_API_KEY`
- `PIXABAY_API_KEY`
- `UNSPLASH_API_KEY`

*(Note: Flickr does not require an API key in this implementation).*

## Examples

Search for 3 images of mountains using Pixabay:
```bash
stock-fetcher search pixabay "mountains" --limit 3 --api-key "YOUR_PIXABAY_KEY"
```

Search using Flickr without an API key:
```bash
stock-fetcher search flickr "vintage cars" --limit 5
```
