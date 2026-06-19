#!/bin/bash

# ============================================================================
# Stock Fetcher CLI Usage Example
#
# Make sure you have installed the CLI extras:
# pip install -e ".[cli]"
# ============================================================================

echo "=== Searching on Flickr (No API Key Required) ==="
# Search for 3 images of 'cyberpunk city' using Flickr
stock-fetcher search flickr "cyberpunk city" --limit 3

echo ""
echo "=== Searching on Pixabay (Requires API Key) ==="
# You can pass the API key via environment variable:
# export PIXABAY_API_KEY="your_key"
# Or via the --api-key flag:
# stock-fetcher search pixabay "nature" --limit 2 --api-key "your_key"
echo "(Uncomment the lines in the script to test Pixabay)"

# stock-fetcher search pixabay "nature" --limit 2
