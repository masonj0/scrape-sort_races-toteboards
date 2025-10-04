#!/bin/bash

# This script emulates the logic of the AdapterFileFinder React component.
# It fetches the full repository tree, filters for adapter files, and then
# fetches the content of each file to create a single merged output.

REPO="masonj0/scrape-sort_races-toteboards"
OUTPUT_FILE="merged_adapters.txt"

echo "Starting adapter file discovery..." >&2

# 1. Fetch the entire repository tree
TREE_DATA=$(curl -s "https://api.github.com/repos/$REPO/git/trees/main?recursive=1")

# Check for API errors (like rate limiting)
if echo "$TREE_DATA" | jq -e '.message' > /dev/null; then
    echo "Error fetching repository tree: $(echo "$TREE_DATA" | jq -r '.message')" >&2
    exit 1
fi

# 2. Use jq to filter for files matching the adapter criteria
ADAPTER_FILES=$(echo "$TREE_DATA" | jq -c '[.tree[] | select(
    .type == "blob" and
    (.path | test("\\.py$")) and
    (
        (.path | test("adapter")) or
        (.path | test("adaptor")) or
        (.path | contains("/adapters/")) or
        (.path | contains("/adapter/"))
    )
)]')

# Clear the output file
> "$OUTPUT_FILE"

FILE_COUNT=$(echo "$ADAPTER_FILES" | jq 'length')
echo "Found $FILE_COUNT adapter files. Fetching and merging content..." >&2

# 3. Loop through each adapter file, fetch its content, and merge it
echo "$ADAPTER_FILES" | jq -c '.[]' | while read -r file_json; do
    path=$(echo "$file_json" | jq -r '.path')
    size=$(echo "$file_json" | jq -r '.size')
    url=$(echo "$file_json" | jq -r '.url')

    echo "  -> Fetching: $path" >&2

    # Fetch the blob content
    blob_data=$(curl -s "$url")
    content_base64=$(echo "$blob_data" | jq -r '.content' | tr -d '\\n')

    # Decode the base64 content
    decoded_content=$(echo "$content_base64" | base64 --decode)

    # Append the header and content to the output file
    {
        echo "================================================================================"
        echo "# FILE: $path"
        echo "# SIZE: $size bytes"
        echo "================================================================================"
        echo ""
        echo "$decoded_content"
        echo ""
        echo ""
    } >> "$OUTPUT_FILE"
done

echo "Merging complete. Full output is in $OUTPUT_FILE" >&2