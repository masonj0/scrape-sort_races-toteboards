#!/bin/bash

# This script recursively fetches the entire file tree from the GitHub API,
# inspired by the logic in the provided React component to ensure a complete,
# non-truncated catalog.

REPO="masonj0/scrape-sort_races-toteboards"
TOKEN="$1" # Accept the token as the first command-line argument

if [ -z "$TOKEN" ]; then
  echo "Error: GitHub API token not provided." >&2
  echo "Usage: ./advanced_aggregator.sh <YOUR_GITHUB_TOKEN>" >&2
  exit 1
fi

# The core recursive function
fetch_tree() {
    local tree_sha="$1"
    local base_path="$2"

    # Fetch the tree data from the GitHub API using the provided token
    local api_url="https://api.github.com/repos/$REPO/git/trees/$tree_sha"
    local tree_data
    tree_data=$(curl -s -H "Authorization: token $TOKEN" -H "Accept: application/vnd.github.v3+json" "$api_url")

    # Error handling for API rate limits or other issues
    if echo "$tree_data" | jq -e '.message' > /dev/null; then
        echo "Error fetching tree $tree_sha: $(echo "$tree_data" | jq -r '.message')" >&2
        return
    fi

    # Process each item in the tree using jq
    echo "$tree_data" | jq -c '.tree[]' | while read -r item; do
        local path=$(echo "$item" | jq -r '.path')
        local type=$(echo "$item" | jq -r '.type')
        local sha=$(echo "$item" | jq -r '.sha')
        local size=$(echo "$item" | jq -r '.size')
        local url=$(echo "$item" | jq -r '.url')

        local full_path
        if [ -z "$base_path" ]; then
            full_path="$path"
        else
            full_path="$base_path/$path"
        fi

        # Output the item as a JSON object
        jq -n \
            --arg path "$full_path" \
            --argjson size "${size:-null}" \
            --arg url "$url" \
            '{path: $path, size: $size, url: $url}'

        # If the item is a directory (tree), recurse into it
        if [ "$type" == "tree" ]; then
            fetch_tree "$sha" "$full_path"
        fi
    done
}

# Start the recursive fetch from the root of the 'main' branch
# The output is a stream of JSON objects, which will be collected into an array.
fetch_tree "main" ""