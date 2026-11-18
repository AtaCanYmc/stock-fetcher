[← Back to Root Repository](../README.md)

# stock-fetcher CLI Manual

The `stock-fetcher` Command Line Interface provides direct terminal queries for stock photography providers. Results render in formatted terminal tables via Rich.

---

## Table of Contents

- [Installation](#installation)
- [Command Syntax](#command-syntax)
- [Positional Arguments](#positional-arguments)
- [Options & Flags](#options--flags)
- [Environment Configuration](#environment-configuration)
- [Execution Examples](#execution-examples)

---

## Installation

Install the package with the `cli` optional extra:

```bash
pip install "stock-fetcher[cli]"
```

---

## Command Syntax

```bash
stock-fetcher search [OPTIONS] PROVIDER TERM
```

---

## Positional Arguments

| Argument | Type | Choices | Description |
| :--- | :--- | :--- | :--- |
| `PROVIDER` | String | `pexels`, `pixabay`, `unsplash`, `flickr` | Target stock photography provider. |
| `TERM` | String | Any text | Query term (e.g. `"mountain lake"`, `"cyberpunk architecture"`). |

---

## Options & Flags

| Flag | Short | Default | Description |
| :--- | :--- | :--- | :--- |
| `--limit` | None | `5` | Maximum number of image records to retrieve. |
| `--api-key` | None | None | Explicit provider authentication token. Overrides environment variables. |
| `--help` | `-h` | None | Display command help and exit. |

---

## Environment Configuration

When `--api-key` is omitted, the CLI reads provider credentials from environment variables:

| Provider | Environment Variable | Required |
| :--- | :--- | :--- |
| `pixabay` | `PIXABAY_API_KEY` | Yes |
| `pexels` | `PEXELS_API_KEY` | Yes |
| `unsplash` | `UNSPLASH_API_KEY` | Yes |
| `flickr` | None | No |

---

## Execution Examples

### Search Pixabay with Explicit API Key

```bash
stock-fetcher search pixabay "alpine forest" --limit 3 --api-key "YOUR_KEY"
```

### Search Flickr Without Credentials

```bash
stock-fetcher search flickr "classic aircraft" --limit 5
```

### Search Pexels Using Environment Variable

```bash
export PEXELS_API_KEY="YOUR_KEY"
stock-fetcher search pexels "deep space" --limit 4
```
