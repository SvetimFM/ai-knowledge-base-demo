#!/bin/bash

# Sync Amazon Bedrock Knowledge Base
# This script triggers an ingestion job to sync the knowledge base with
# the S3 documentation.

set -e

STACK_NAME="HpcKnowledgeBaseStack"
AWS_PROFILE="${AWS_PROFILE:-default}"

echo "===================================="
echo "Knowledge Base Sync Script"
echo "===================================="
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "ERROR: AWS CLI is not installed. Please install it first."
    echo "Visit: https://aws.amazon.com/cli/"
    exit 1
fi

# Get Knowledge Base ID from CloudFormation outputs
echo "Retrieving Knowledge Base ID from CloudFormation stack..."
echo "Using AWS profile: $AWS_PROFILE"
KB_ID=$(aws cloudformation describe-stacks \
    --profile "$AWS_PROFILE" \
    --stack-name "$STACK_NAME" \
    --query 'Stacks[0].Outputs[?OutputKey==`KnowledgeBaseId`].OutputValue' \
    --output text 2>/dev/null)

if [ -z "$KB_ID" ]; then
    echo "ERROR: Could not retrieve Knowledge Base ID from stack '$STACK_NAME'."
    echo "Please ensure the stack is deployed and you have the correct AWS credentials."
    exit 1
fi

echo "Knowledge Base ID: $KB_ID"
echo ""

# Get Data Source ID from CloudFormation outputs
echo "Retrieving Data Source ID from CloudFormation stack..."
DS_ID=$(aws cloudformation describe-stacks \
    --profile "$AWS_PROFILE" \
    --stack-name "$STACK_NAME" \
    --query 'Stacks[0].Outputs[?OutputKey==`DataSourceId`].OutputValue' \
    --output text 2>/dev/null)

if [ -z "$DS_ID" ]; then
    echo "ERROR: Could not retrieve Data Source ID from stack '$STACK_NAME'."
    exit 1
fi

echo "Data Source ID: $DS_ID"
echo ""

# Start ingestion job
echo "Starting ingestion job..."
JOB_ID=$(aws bedrock-agent start-ingestion-job \
    --profile "$AWS_PROFILE" \
    --knowledge-base-id "$KB_ID" \
    --data-source-id "$DS_ID" \
    --query 'ingestionJob.ingestionJobId' \
    --output text)

if [ -z "$JOB_ID" ]; then
    echo "ERROR: Failed to start ingestion job."
    exit 1
fi

echo "✅ Ingestion job started successfully!"
echo ""
echo "Job ID: $JOB_ID"
echo ""
echo "Monitoring ingestion job status..."
echo "(This may take 2-5 minutes)"
echo ""

# Poll for job completion
MAX_ATTEMPTS=60
ATTEMPT=0
while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    STATUS=$(aws bedrock-agent get-ingestion-job \
        --profile "$AWS_PROFILE" \
        --knowledge-base-id "$KB_ID" \
        --data-source-id "$DS_ID" \
        --ingestion-job-id "$JOB_ID" \
        --query 'ingestionJob.status' \
        --output text)

    echo "Status: $STATUS (attempt $((ATTEMPT + 1))/$MAX_ATTEMPTS)"

    if [ "$STATUS" == "COMPLETE" ]; then
        echo ""
        echo "✅ Ingestion completed successfully!"
        echo ""
        echo "Your knowledge base is ready to use!"
        echo ""
        echo "To test with Amazon Q Developer CLI:"
        echo "1. Navigate to this project directory"
        echo "2. Run: q"
        echo "3. Try a query like: 'What are the key differences between NCCL and RCCL?'"
        echo ""
        exit 0
    elif [ "$STATUS" == "FAILED" ]; then
        echo ""
        echo "❌ Ingestion job failed."
        echo ""
        echo "To troubleshoot:"
        echo "1. Check CloudWatch logs for errors"
        echo "2. Verify S3 bucket has documents"
        echo "3. Ensure IAM role has correct permissions"
        echo ""
        exit 1
    elif [ "$STATUS" == "IN_PROGRESS" ]; then
        sleep 10
    else
        echo "Unexpected status: $STATUS"
        sleep 10
    fi

    ATTEMPT=$((ATTEMPT + 1))
done

echo ""
echo "⚠️  Ingestion job is still running after $MAX_ATTEMPTS attempts."
echo ""
echo "You can check the status manually with:"
echo "aws bedrock-agent get-ingestion-job \\"
echo "  --profile $AWS_PROFILE \\"
echo "  --knowledge-base-id $KB_ID \\"
echo "  --data-source-id $DS_ID \\"
echo "  --ingestion-job-id $JOB_ID"
echo ""
