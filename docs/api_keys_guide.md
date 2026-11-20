[← Back to Root Repository](../README.md) | [CLI Manual](cli_manual.md) | [MCP Manual](mcp_manual.md)

# API Keys Guide

This guide details how to obtain free API credentials for supported stock image providers and how to configure them for use with the `stock-fetcher` Command Line Interface (CLI).

---

## Table of Contents

- [Provider Authentication Matrix](#provider-authentication-matrix)
- [How to Obtain API Keys](#how-to-obtain-api-keys)
  - [Pexels](#1-pexels)
  - [Pixabay](#2-pixabay)
  - [Unsplash](#3-unsplash)
  - [Flickr (No Key Required)](#4-flickr-no-key-required)
- [Configuring Keys for the CLI](#configuring-keys-for-the-cli)
  - [Method 1: Persistent Shell Configuration (Recommended)](#method-1-persistent-shell-configuration-recommended)
  - [Method 2: Project-Level `.env` File](#method-2-project-level-env-file)
  - [Method 3: Inline Environment Variables](#method-3-inline-environment-variables)
  - [Method 4: Direct Command Flag (`--api-key`)](#method-4-direct-command-flag---api-key)
  - [Method 5: Unified Global Fallback Variable](#method-5-unified-global-fallback-variable)
- [Verifying Your Configuration](#verifying-your-configuration)
- [Troubleshooting & Common Issues](#troubleshooting--common-issues)
- [Security Best Practices](#security-best-practices)

---

## Provider Authentication Matrix

| Provider | Environment Variable | Key Required? | Free Tier Quota | Registration Link |
| :--- | :--- | :--- | :--- | :--- |
| **Pexels** | `PEXELS_API_KEY` | Yes | 200 requests/hour (20,000/month) | [pexels.com/api](https://www.pexels.com/api/) |
| **Pixabay** | `PIXABAY_API_KEY` | Yes | 100 requests/minute | [pixabay.com/api/docs](https://pixabay.com/api/docs/) |
| **Unsplash** | `UNSPLASH_API_KEY` | Yes | 50 requests/hour (Demo tier) | [unsplash.com/developers](https://unsplash.com/developers) |
| **Flickr** | None | No | Uncapped public scraping | Zero-configuration |
| **Wikimedia** | None | No | Uncapped MediaWiki open access | Zero-configuration |
| **Openverse** | `OPENVERSE_API_KEY` | Optional | Open public access (Token for higher limits) | [api.openverse.org](https://api.openverse.org/) |

---

## How to Obtain API Keys

### 1. Pexels

Pexels provides immediate API access upon creating a developer application. Approval is automated and instantaneous.

1. **Create an Account**: Visit [https://www.pexels.com/](https://www.pexels.com/) and register or sign in.
2. **Access the Developer Portal**: Navigate to [https://www.pexels.com/api/](https://www.pexels.com/api/) and click **Get Started** (or navigate directly to [https://www.pexels.com/api/new/](https://www.pexels.com/api/new/)).
3. **Submit Application Details**:
   - Provide an application name (for example, `CLI Stock Fetcher`).
   - Select your intended use case (e.g. `Personal / Hobby` or `Scripting`).
   - Describe your planned workflow (e.g. `Local terminal queries for copyright-free reference images`).
4. **Copy the API Key**: Once generated, your API key is displayed as a 56-character alphanumeric string.

> [!NOTE]
> The Pexels free tier provides 200 requests per hour and 20,000 requests per month. If you exceed this rate, the API returns HTTP 429 Too Many Requests.

---

### 2. Pixabay

Pixabay links your API key directly to your standard user account. No separate application review is required.

1. **Create an Account**: Register or sign in at [https://pixabay.com/](https://pixabay.com/).
2. **Open the API Documentation**: Navigate to [https://pixabay.com/api/docs/](https://pixabay.com/api/docs/).
3. **Locate Your Key**: Scroll to the **Search Images** or **Parameters** section. When signed in, a green highlighted box displays your personal API key:
   ```text
   key: 12345678-abcdef0123456789abcdef012
   ```
4. **Copy the Key**: Copy the complete alphanumeric string (including the hyphen).

> [!NOTE]
> Pixabay limits free requests to 100 calls per 60-second window across all endpoints.

---

### 3. Unsplash

Unsplash requires registering an application under their developer program.

1. **Register as a Developer**: Visit [https://unsplash.com/developers](https://unsplash.com/developers) and click **Register as a developer** or sign in.
2. **Create an Application**:
   - Navigate to **Your apps** -> **New Application**.
   - Review and accept the API Terms of Use.
   - Enter an Application Name and a brief description.
3. **Retrieve the Access Key**:
   - On your application dashboard, scroll down to the **Keys** section.
   - Copy the **Access Key** string.

> [!IMPORTANT]
> Always use the **Access Key**, never the **Secret Key**. `stock-fetcher` communicates with Unsplash via public client authentication headers (`Authorization: Client-ID <ACCESS_KEY>`).

> [!NOTE]
> Unsplash demo applications are limited to 50 requests per hour. You can apply for Production status (5,000 requests/hour) in the developer dashboard if higher throughput is required.

---

### 4. Flickr (No Key Required)

Flickr integration in `stock-fetcher` uses an integrated HTML scraper targeting Creative Commons licensed media.

- **No API key is required.**
- **No developer account registration is needed.**
- Queries against Flickr work out of the box without configuring any environment variables or parameters.

---

## Configuring Keys for the CLI

`stock-fetcher` supports several methods for supplying API credentials. Choose the method best suited to your workflow.

### Method 1: Persistent Shell Configuration (Recommended)

Exporting variables in your shell profile ensures credentials remain accessible across all terminal sessions.

#### For macOS and Linux with Zsh (Default on macOS)

Open `~/.zshrc` in your text editor:

```bash
nano ~/.zshrc
```

Add your provider keys at the bottom of the file:

```bash
# Stock Fetcher API Keys
export PEXELS_API_KEY="your_pexels_key_here"
export PIXABAY_API_KEY="your_pixabay_key_here"
export UNSPLASH_API_KEY="your_unsplash_key_here"
```

Save the file and apply changes:

```bash
source ~/.zshrc
```

#### For Linux or Bash Users

Open `~/.bashrc`:

```bash
nano ~/.bashrc
```

Append the export statements, save, and reload:

```bash
# Stock Fetcher API Keys
export PEXELS_API_KEY="your_pexels_key_here"
export PIXABAY_API_KEY="your_pixabay_key_here"
export UNSPLASH_API_KEY="your_unsplash_key_here"
```

```bash
source ~/.bashrc
```

---

### Method 2: Project-Level `.env` File

If you prefer keeping credentials scoped to a specific project folder, create a `.env` file in your workspace root:

```ini
# .env
PEXELS_API_KEY=your_pexels_key_here
PIXABAY_API_KEY=your_pixabay_key_here
UNSPLASH_API_KEY=your_unsplash_key_here
```

Load the variables into your current shell before executing CLI commands:

```bash
# Export all variables defined in .env
export $(grep -v '^#' .env | xargs)

# Execute search
stock-fetcher search pexels "abstract architecture"
```

Alternatively, use tools such as [direnv](https://direnv.net/) to automatically load and unload `.env` files upon entering the directory.

---

### Method 3: Inline Environment Variables

For single-command runs or temporary sessions, pass variables directly before the executable:

```bash
# Query Pexels
PEXELS_API_KEY="your_key" stock-fetcher search pexels "cyberpunk"

# Query all providers simultaneously
PEXELS_API_KEY="key1" PIXABAY_API_KEY="key2" UNSPLASH_API_KEY="key3" stock-fetcher find "space nebula"
```

---

### Method 4: Direct Command Flag (`--api-key`)

You can supply an explicit API key using the `--api-key` (or `-k`) option:

```bash
# Explicit Pexels key
stock-fetcher search pexels "mountain peak" --api-key "your_pexels_key_here"

# Shorthand -k flag
stock-fetcher search pixabay "forest path" -k "your_pixabay_key_here"
```

> [!NOTE]
> The `--api-key` flag overrides any environment variable present in the active shell.

---

### Method 5: Unified Global Fallback Variable

If you want a single fallback variable across environments or internal proxies, configure `STOCK_FETCHER_API_KEY`:

```bash
export STOCK_FETCHER_API_KEY="your_universal_or_test_key"
```

When a provider-specific variable (e.g. `PEXELS_API_KEY`) is unset, the CLI falls back to `STOCK_FETCHER_API_KEY` before terminating with an authentication error.

---

## Verifying Your Configuration

`stock-fetcher` provides built-in diagnostic commands to verify credential status without making unnecessary network queries.

### 1. Inspect Stored Keys

Run `stock-fetcher keys` to review detected environment variables:

```bash
stock-fetcher keys
```

Expected output:

```text
                           Environment API Key Status
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Provider  ┃ Variable         ┃ Status                                 ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ pixabay   │ PIXABAY_API_KEY  │ Configured (1234...ab)                 │
│ pexels    │ PEXELS_API_KEY   │ Configured (56a1...8f)                 │
│ unsplash  │ UNSPLASH_API_KEY │ Configured (gh78...z1)                 │
│ flickr    │ -                │ Not Required                           │
└───────────┴──────────────────┴────────────────────────────────────────┘
```

The CLI automatically masks sensitive keys, displaying only the leading and trailing characters.

### 2. Check Provider Readiness

Run `stock-fetcher providers` to inspect operating modes and readiness:

```bash
stock-fetcher providers
```

Expected output:

```text
                                Supported Providers
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Provider  ┃ Mode         ┃ Auth Required ┃ Env Variable     ┃ Status                   ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ pixabay   │ REST API     │ Yes           │ PIXABAY_API_KEY  │ Ready                    │
│ pexels    │ REST API     │ Yes           │ PEXELS_API_KEY   │ Ready                    │
│ unsplash  │ REST API     │ Yes           │ UNSPLASH_API_KEY │ Ready                    │
│ flickr    │ HTML Scraper │ No            │ None             │ Ready (No Key Required)  │
└───────────┴──────────────┴───────────────┴━━━━━━━━━━━━━━━━━━┴━━━━━━━━━━━━━━━━━━━━━━━━━━┘
```

### 3. Run a Test Query

Execute a single-result search against each configured provider to confirm connectivity:

```bash
# Test Flickr (requires no key)
stock-fetcher search flickr "nature" --limit 1

# Test Pexels
stock-fetcher search pexels "nature" --limit 1

# Test Pixabay
stock-fetcher search pixabay "nature" --limit 1

# Test Unsplash
stock-fetcher search unsplash "nature" --limit 1
```

---

## Troubleshooting & Common Issues

### Issue 1: `AuthenticationError: Invalid or expired API token` (HTTP 401 / 403)

- **Cause**: The API key is misspelled, truncated, expired, or has leading/trailing whitespace.
- **Fix**: Check `stock-fetcher keys` to verify the masked string length. Re-copy the exact key from the provider dashboard and re-export. For Unsplash, confirm you copied the **Access Key**, not the Secret Key.

### Issue 2: `Missing API Key for Provider 'pexels'`

- **Cause**: The CLI did not find `PEXELS_API_KEY` in the environment.
- **Fix**: Ensure you ran `export PEXELS_API_KEY="..."` rather than a local subshell variable `PEXELS_API_KEY="..."` without `export`. Run `env | grep PEXELS` to confirm visibility.

### Issue 3: `APIConnectionError: Rate limit exceeded` (HTTP 429)

- **Cause**: You exceeded the hourly or monthly quota of the provider free tier.
- **Fix**: Wait for the rate limit window to reset, enable the `stock-fetcher` caching layer to reduce duplicate requests, or switch to an alternate provider (e.g. Flickr).

---

## Security Best Practices

1. **Never Commit API Keys**: Never hardcode API keys in source files or commit `.env` files to git. Ensure `.env` is listed in `.gitignore`.
2. **Restrict Shell File Permissions**: Protect your shell profile containing credentials against unauthorized local access:
   ```bash
   chmod 600 ~/.zshrc
   chmod 600 ~/.bashrc
   ```
3. **Rotate Compromised Keys**: If a key is accidentally exposed in a commit or public log, immediately revoke it in the respective provider dashboard and generate a replacement.
4. **Prefer Environment Variables over Command Line Flags**: Passing `-k "key"` exposes credentials in shell history (`~/.bash_history` or `~/.zsh_history`) and in system process tables (`ps aux`). Using environment variables avoids this exposure.
