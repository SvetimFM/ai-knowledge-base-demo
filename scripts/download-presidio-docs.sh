#!/bin/bash
# Download Presidio documentation for Knowledge Base

set -e

BASE_DIR="/mnt/j/DevWorkspace/Active Projects/Q_TicketTriage/docs/presidio"
TEMP_DIR="/tmp/presidio-docs"

mkdir -p "$TEMP_DIR"
mkdir -p "$BASE_DIR"/{case-studies,white-papers,solution-briefs,technical-blogs,partner-docs}

echo "🔄 Downloading Presidio Documentation..."
echo "=================================================="

# Function to download and convert HTML to Markdown
download_html() {
    local url="$1"
    local output_file="$2"
    local title="$3"

    echo "📥 Downloading: $title"

    if wget -q "$url" -O "$TEMP_DIR/temp.html" 2>/dev/null; then
        if pandoc "$TEMP_DIR/temp.html" \
            --from=html \
            --to=gfm \
            --wrap=none \
            -o "$output_file" 2>/dev/null; then

            # Add metadata header
            temp_file="${output_file}.tmp"
            {
                echo "# $title"
                echo ""
                echo "**Source**: $url"
                echo "**Downloaded**: $(date '+%Y-%m-%d')"
                echo ""
                echo "---"
                echo ""
                cat "$output_file"
            } > "$temp_file"
            mv "$temp_file" "$output_file"

            size=$(wc -c < "$output_file")
            echo "   ✓ Converted ($size bytes)"
            return 0
        fi
    fi

    echo "   ⚠️  Failed to download/convert"
    return 1
}

# Download confirmed PDFs
echo ""
echo "=== Downloading PDFs ==="

wget -q "https://www.presidio.com/wp-content/uploads/2021/02/VMware-intrinsic-security-solutions-ebook.pdf" \
    -O "$BASE_DIR/white-papers/vmware-intrinsic-security-ebook.pdf" 2>/dev/null && \
    echo "✓ VMware Security eBook" || echo "⚠️  VMware Security eBook failed"

wget -q "https://www.presidio.com/wp-content/uploads/2025/05/sb_simplify-SD-WAN-operations-presidio.pdf" \
    -O "$BASE_DIR/solution-briefs/fortinet-sdwan-solution-brief.pdf" 2>/dev/null && \
    echo "✓ Fortinet SD-WAN Brief" || echo "⚠️  Fortinet SD-WAN Brief failed"

wget -q "https://www.presidio.com/icheestu/2021/03/Slick_StartingPoint.pdf" \
    -O "$BASE_DIR/case-studies/startingpoint-case-study.pdf" 2>/dev/null && \
    echo "✓ StartingPoint Case Study" || echo "⚠️  StartingPoint Case Study failed"

# Download technical blogs
echo ""
echo "=== Downloading Technical Blogs ==="

download_html \
    "https://www.presidio.com/blogs/bringing-generative-ai-in-house-a-strategic-guide/" \
    "$BASE_DIR/technical-blogs/bringing-generative-ai-in-house.md" \
    "Bringing Generative AI In-House: Strategic Guide"

download_html \
    "https://www.presidio.com/blogs/simplifying-the-extended-enterprise-with-presidios-enterprise-edge-solutions/" \
    "$BASE_DIR/technical-blogs/enterprise-edge-solutions.md" \
    "Enterprise Edge Solutions"

download_html \
    "https://www.presidio.com/blogs/vmware-on-aws-getting-the-band-back-together/" \
    "$BASE_DIR/technical-blogs/vmware-on-aws-integration.md" \
    "VMware on AWS Integration"

download_html \
    "https://www.presidio.com/blogs/finally-zero-trust-security-that-users-actually-like-to-use/" \
    "$BASE_DIR/technical-blogs/zero-trust-security-users-like.md" \
    "Zero Trust Security Users Like"

download_html \
    "https://www.presidio.com/blogs/presidios-2024-tech-predictions-ai-cybersecurity-cloud-and-emerging-tech/" \
    "$BASE_DIR/technical-blogs/2024-tech-predictions.md" \
    "2024 Tech Predictions"

download_html \
    "https://www.presidio.com/blogs/navigating-virtualization-in-2024-key-strategies-for-it-leaders/" \
    "$BASE_DIR/technical-blogs/navigating-virtualization-2024.md" \
    "Navigating Virtualization 2024"

download_html \
    "https://www.presidio.com/blogs/government-it-transformation-in-2025/" \
    "$BASE_DIR/technical-blogs/government-it-transformation-2025.md" \
    "Government IT Transformation 2025"

download_html \
    "https://www.presidio.com/blogs/how-planning-disaster-recovery-can-make-the-difference/" \
    "$BASE_DIR/technical-blogs/disaster-recovery-planning.md" \
    "Disaster Recovery Planning"

download_html \
    "https://www.presidio.com/blogs/demystifying-digital-transformation-a-roadmap-for-businesses/" \
    "$BASE_DIR/technical-blogs/digital-transformation-roadmap.md" \
    "Digital Transformation Roadmap"

# Download solution pages
echo ""
echo "=== Downloading Solution Pages ==="

download_html \
    "https://www.presidio.com/solutions/cloud-finops/" \
    "$BASE_DIR/partner-docs/cloud-finops-overview.md" \
    "Cloud FinOps"

download_html \
    "https://www.presidio.com/presidio-tools-and-processes-simplify-data-center-modernization-to-optimize-roi-and-tco/" \
    "$BASE_DIR/partner-docs/data-center-modernization-tools.md" \
    "Data Center Modernization"

download_html \
    "https://www.presidio.com/solutions/cloud/devops-automation/" \
    "$BASE_DIR/partner-docs/devops-automation-overview.md" \
    "DevOps & Automation"

download_html \
    "https://www.presidio.com/solutions/cybersecurity/" \
    "$BASE_DIR/partner-docs/cybersecurity-overview.md" \
    "Cybersecurity Overview"

download_html \
    "https://www.presidio.com/news/presidio-launches-first-of-its-kind-private-gen-ai-platform/" \
    "$BASE_DIR/partner-docs/private-ai-accelerator.md" \
    "Private AI Accelerator"

download_html \
    "https://www.presidio.com/solutions/managed-services/" \
    "$BASE_DIR/partner-docs/managed-services-overview.md" \
    "Managed Services"

download_html \
    "https://www.presidio.com/partners/aws/" \
    "$BASE_DIR/partner-docs/aws-partnership.md" \
    "AWS Partnership"

# Download case studies
echo ""
echo "=== Downloading Case Studies ==="

download_html \
    "https://www.presidio.com/client-stories/q2-partners-with-presidio-and-aws-to-drive-down-cost-and-accelerate-innovation/" \
    "$BASE_DIR/case-studies/q2-holdings-aws-cloud-migration.md" \
    "Q2 Holdings - AWS Cloud Migration"

download_html \
    "https://www.presidio.com/client-stories/the-national-hockey-league-nhl-modernizing-the-upper-deck-nhl-draft/" \
    "$BASE_DIR/case-studies/nhl-draft-application.md" \
    "NHL Draft Application"

download_html \
    "https://www.presidio.com/client-stories/orthocarolina/" \
    "$BASE_DIR/case-studies/orthocarolina-healthcare.md" \
    "OrthoCarolina Healthcare"

download_html \
    "https://www.presidio.com/client-stories/draftkings/" \
    "$BASE_DIR/case-studies/draftkings-cloud-infrastructure.md" \
    "DraftKings Cloud Infrastructure"

download_html \
    "https://www.presidio.com/client-stories/radial-empowering-digital-transformation-with-robust-network-solutions/" \
    "$BASE_DIR/case-studies/radial-network-solutions.md" \
    "Radial Network Solutions"

download_html \
    "https://www.presidio.com/client-stories/hard-rock-digital/" \
    "$BASE_DIR/case-studies/hard-rock-digital.md" \
    "Hard Rock Digital"

download_html \
    "https://www.presidio.com/client-stories/presidio-and-aws-setting-a-higher-cloud-standard-for-higher-ed/" \
    "$BASE_DIR/case-studies/higher-ed-cloud-standard.md" \
    "Higher Ed Cloud Standard"

download_html \
    "https://www.presidio.com/blog/1823/breach-prevention-in-the-cloud-a-security-case-study" \
    "$BASE_DIR/case-studies/breach-prevention-cloud-security.md" \
    "Breach Prevention Cloud Security"

download_html \
    "https://www.presidio.com/client-stories/cisco-sd-wan/" \
    "$BASE_DIR/case-studies/cisco-sd-wan.md" \
    "Cisco SD-WAN"

download_html \
    "https://www.presidio.com/client-stories/cloud-managed-services-empowering-innovation-ensuring-efficiency/" \
    "$BASE_DIR/case-studies/cloud-managed-services.md" \
    "Cloud Managed Services"

# Summary
echo ""
echo "=================================================="
echo "📊 Download Summary"
echo "=================================================="

find "$BASE_DIR" -type f -name "*.pdf" -o -name "*.md" | while read -r file; do
    dir=$(basename "$(dirname "$file")")
    filename=$(basename "$file")
    size=$(du -h "$file" | cut -f1)
    echo "  [$dir] $filename ($size)"
done

total_files=$(find "$BASE_DIR" -type f \( -name "*.pdf" -o -name "*.md" \) | wc -l)
total_size=$(du -sh "$BASE_DIR" | cut -f1)

echo ""
echo "✓ Total files: $total_files"
echo "✓ Total size: $total_size"
echo "✓ Location: $BASE_DIR/"

# Cleanup
rm -rf "$TEMP_DIR"

echo ""
echo "✅ Download complete!"
