#!/bin/bash
# Script to download and convert NVIDIA NCCL documentation to Markdown
# Uses pandoc for HTML to Markdown conversion

set -e

DOCS_DIR="docs/nvidia"
TEMP_DIR="/tmp/nvidia-nccl-html"
BASE_URL="https://docs.nvidia.com/deeplearning/nccl/user-guide/docs"

# Create directories
mkdir -p "$DOCS_DIR"
mkdir -p "$TEMP_DIR"

echo "🔄 Converting NVIDIA NCCL Documentation to Markdown..."
echo "=================================================="

# Define pages to convert (filename:url)
declare -A PAGES=(
    ["nccl-official-overview"]="$BASE_URL/overview.html"
    ["nccl-official-usage"]="$BASE_URL/usage.html"
    ["nccl-official-collectives"]="$BASE_URL/usage/collectives.html"
    ["nccl-official-env-vars"]="$BASE_URL/env.html"
    ["nccl-official-api"]="$BASE_URL/api.html"
    ["nccl-official-tuning"]="$BASE_URL/tuning.html"
    ["nccl-official-troubleshooting"]="$BASE_URL/troubleshooting.html"
)

# Download and convert each page
for filename in "${!PAGES[@]}"; do
    url="${PAGES[$filename]}"
    echo ""
    echo "📥 Processing: $filename"
    echo "   URL: $url"

    # Download HTML
    html_file="$TEMP_DIR/${filename}.html"
    md_file="$DOCS_DIR/${filename}.md"

    if wget -q "$url" -O "$html_file" 2>/dev/null; then
        echo "   ✓ Downloaded"

        # Convert to Markdown
        if pandoc "$html_file" \
            --from=html \
            --to=gfm \
            --wrap=none \
            --extract-media="$DOCS_DIR/images" \
            -o "$md_file" 2>/dev/null; then

            echo "   ✓ Converted to Markdown"

            # Add metadata header
            temp_file="${md_file}.tmp"
            {
                echo "# NVIDIA NCCL Documentation: $(basename "$filename" | sed 's/-/ /g' | sed 's/nccl official /NCCL - /' | awk '{for(i=1;i<=NF;i++){$i=toupper(substr($i,1,1)) tolower(substr($i,2))}}1')"
                echo ""
                echo "**Source**: $url"
                echo "**Converted**: $(date '+%Y-%m-%d')"
                echo "**Version**: NCCL 2.28.6"
                echo ""
                echo "---"
                echo ""
                cat "$md_file"
            } > "$temp_file"
            mv "$temp_file" "$md_file"

            # Get file size
            size=$(wc -c < "$md_file")
            echo "   ✓ Added metadata (${size} bytes)"
        else
            echo "   ⚠️  Conversion failed, trying alternative method..."
            # Fallback: simple extraction
            lynx -dump -nolist "$html_file" > "$md_file" 2>/dev/null || {
                echo "   ❌ Failed to convert $filename"
                rm -f "$md_file"
            }
        fi
    else
        echo "   ⚠️  Page not found (may not exist): $url"
    fi
done

echo ""
echo "=================================================="
echo "📊 Conversion Summary:"
echo "=================================================="

# Count converted files
converted=$(find "$DOCS_DIR" -name "*.md" -type f | wc -l)
total_size=$(find "$DOCS_DIR" -name "*.md" -type f -exec wc -c {} + | tail -1 | awk '{print $1}')

echo "✓ Converted: $converted pages"
echo "✓ Total size: $(numfmt --to=iec-i --suffix=B $total_size 2>/dev/null || echo "${total_size} bytes")"
echo "✓ Location: $DOCS_DIR/"

# List converted files
echo ""
echo "Converted files:"
find "$DOCS_DIR" -name "*.md" -type f -exec basename {} \; | sort

# Clean up
rm -rf "$TEMP_DIR"

echo ""
echo "✅ Conversion complete!"
echo ""
echo "📤 Next steps:"
echo "   1. Review converted files in $DOCS_DIR/"
echo "   2. Upload to S3: ./scripts/deploy-docs.sh"
echo "   3. Sync KB: ./scripts/sync-kb.sh"
