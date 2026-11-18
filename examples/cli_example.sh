#!/bin/bash

# ============================================================================
# Stock Fetcher CLI Usage Examples
#
# Ensure you have installed the CLI extras:
# pip install -e ".[cli]"
# ============================================================================

echo "=== 1. Checking Provider and Key Status ==="
stock-fetcher providers
stock-fetcher keys

echo ""
echo "=== 2. Searching on Flickr (No API Key Required) ==="
stock-fetcher search flickr "cyberpunk city" --limit 3

echo ""
echo "=== 3. Exporting Direct URLs (Format: urls) ==="
stock-fetcher search flickr "vintage cars" --limit 2 -f urls

echo ""
echo "=== 4. Searching Across All Providers with JSON Output ==="
# In 'all' mode, providers with missing keys are automatically skipped without crashing
stock-fetcher find "mountains" --limit 2 -f json

echo ""
echo "=== 5. Search and Download Images Directly to Disk ==="
# stock-fetcher search flickr "alpine lake" --limit 2 -d -o ./downloaded_images
