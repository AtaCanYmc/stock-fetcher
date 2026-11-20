[← Back to Root Repository](../README.md) | [API Keys Guide](api_keys_guide.md) | [MCP Manual](mcp_manual.md)

# stock-fetcher CLI Manual

The `stock-fetcher` Command Line Interface provides direct terminal queries, output piping, batch downloads, and provider diagnostics rendered via Rich.

---

## Table of Contents

- [Installation](#installation)
- [Command Overview](#command-overview)
- [`search` Command](#search-command)
- [`find` Command](#find-command)
- [`download` Command](#download-command)
- [`providers` Command](#providers-command)
- [`keys` Command](#keys-command)
- [`version` Command](#version-command)
- [Environment Configuration](#environment-configuration)
- [Shell Pipeline Recipes](#shell-pipeline-recipes)

---

## Installation

### Method 1: Homebrew (Recommended on macOS & Linux)

Install the standalone executable via the official tap:

```bash
brew tap AtaCanYmc/tap
brew install stock-fetcher
```

Or install directly in one step:

```bash
brew install AtaCanYmc/tap/stock-fetcher
```

### Method 2: Pip with CLI Extra

Install into your active Python environment:

```bash
pip install "stock-fetcher[cli]"
```

---

## Command Overview

| Command | Description |
| :--- | :--- |
| `stock-fetcher search PROVIDER TERM` | Query a specific provider or `all` providers. |
| `stock-fetcher find TERM` | Shorthand to query all providers simultaneously. |
| `stock-fetcher download URL` | Download an image by direct URL to disk. |
| `stock-fetcher providers` | Display supported providers, access modes, and readiness status. |
| `stock-fetcher keys` | Inspect environment API key configuration. |
| `stock-fetcher version` | Print version and platform details. |

---

## `search` Command

```bash
stock-fetcher search [OPTIONS] PROVIDER TERM
```

### Arguments

| Argument | Choices | Description |
| :--- | :--- | :--- |
| `PROVIDER` | `pixabay`, `pexels`, `unsplash`, `flickr`, `wikimedia`, `openverse`, `all` | Target provider or `all`. |
| `TERM` | String | Search query term (e.g. `"mountain lake"`). |

### Options & Flags

| Flag | Short | Default | Description |
| :--- | :--- | :--- | :--- |
| `--limit` | `-l` | `5` | Maximum images to fetch per provider. |
| `--api-key` | `-k` | None | Explicit provider authentication token. |
| `--format` | `-f` | `table` | Output format: `table`, `json`, `csv`, or `urls`. |
| `--download` | `-d` | `false` | Automatically download fetched images to disk. |
| `--output-dir` | `-o` | `./downloads` | Destination folder when downloading. |

---

## `find` Command

Convenient shorthand equivalent to `stock-fetcher search all TERM`.

```bash
stock-fetcher find "cyberpunk neon city" --limit 3 -f table
```

---

## `download` Command

Downloads a single file from a direct image URL with a real-time progress bar.

```bash
stock-fetcher download "https://images.pexels.com/photos/123/original.jpg" -o ./wallpapers -n custom.jpg
```

---

## `providers` Command

Lists all available providers and their current readiness status:

```bash
stock-fetcher providers
```

---

## `keys` Command

Inspects API key presence in the environment (`PIXABAY_API_KEY`, `PEXELS_API_KEY`, `UNSPLASH_API_KEY`):

```bash
stock-fetcher keys
```

---

## `version` Command

```bash
stock-fetcher version
```

---

## Environment Configuration

When `--api-key` is omitted, the CLI reads provider credentials from environment variables:

| Provider | Environment Variable | Required |
| :--- | :--- | :--- |
| `pixabay` | `PIXABAY_API_KEY` | Yes |
| `pexels` | `PEXELS_API_KEY` | Yes |
| `unsplash` | `UNSPLASH_API_KEY` | Yes |
| `flickr` | None | No |
| `wikimedia` | None | No |
| `openverse` | `OPENVERSE_API_KEY` | Optional |

A universal fallback variable `STOCK_FETCHER_API_KEY` is also checked if a provider-specific variable is unset.

> [!TIP]
> For detailed step-by-step instructions on obtaining free keys for each platform and configuring them permanently in `~/.zshrc` or `~/.bashrc`, see the [API Keys Guide](api_keys_guide.md).

---

## Shell Pipeline Recipes

### 1. Pipe Direct URLs to `curl`

```bash
stock-fetcher search flickr "vintage cars" -l 3 -f urls | xargs -n 1 curl -O
```

### 2. Parse Results with `jq`

```bash
stock-fetcher search pixabay "aurora borealis" -f json | jq '.[].url_original'
```

### 3. Search and Download in One Command

```bash
stock-fetcher find "deep forest" -l 2 -d -o ./nature_photos
```
