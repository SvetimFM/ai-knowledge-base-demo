#!/bin/bash

# Deploy HPC documentation to S3 bucket
# This script uploads all documentation from the docs/ directory to the S3 bucket
# created by the CDK stack.

set -e

STACK_NAME="HpcKnowledgeBaseStack"
AWS_PROFILE="${AWS_PROFILE:-default}"

echo "==================================="
echo "HPC Documentation Deployment Script"
echo "==================================="
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "ERROR: AWS CLI is not installed. Please install it first."
    echo "Visit: https://aws.amazon.com/cli/"
    exit 1
fi

# Check if docs directory exists
if [ ! -d "docs" ]; then
    echo "ERROR: docs/ directory not found."
    echo "Please run this script from the project root directory."
    exit 1
fi

# Get the S3 bucket name from CloudFormation outputs
echo "Retrieving S3 bucket name from CloudFormation stack..."
echo "Using AWS profile: $AWS_PROFILE"
BUCKET_NAME=$(aws cloudformation describe-stacks \
    --profile "$AWS_PROFILE" \
    --stack-name "$STACK_NAME" \
    --query 'Stacks[0].Outputs[?OutputKey==`DocsBucketName`].OutputValue' \
    --output text 2>/dev/null)

if [ -z "$BUCKET_NAME" ]; then
    echo "ERROR: Could not retrieve bucket name from stack '$STACK_NAME'."
    echo "Please ensure the stack is deployed and you have the correct AWS credentials."
    exit 1
fi

echo "Found bucket: $BUCKET_NAME"
echo ""

# Count files to upload
FILE_COUNT=$(find docs -type f -name "*.md" | wc -l)
echo "Uploading $FILE_COUNT documentation files to S3..."
echo ""

# Upload documentation to S3
aws s3 sync ./docs/ "s3://$BUCKET_NAME/" \
    --profile "$AWS_PROFILE" \
    --exclude "*" \
    --include "*.md" \
    --delete

echo ""
echo "✅ Documentation uploaded successfully!"
echo ""
echo "Bucket: $BUCKET_NAME"
echo "Files uploaded: $FILE_COUNT"
echo ""
echo "Next steps:"
echo "1. Run ./scripts/sync-kb.sh to trigger knowledge base ingestion"
echo "2. Wait 2-5 minutes for ingestion to complete"
echo "3. Start querying with Amazon Q Developer CLI"
echo ""
