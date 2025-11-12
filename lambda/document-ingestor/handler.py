"""
Document Ingestor Lambda
Triggered by S3 uploads via SQS, tracks state in DynamoDB, invokes embeddings Lambda
"""

import json
import os
import boto3
import time
import re
from typing import Dict, Any, Optional
from decimal import Decimal

# Environment variables
EMBEDDINGS_FUNCTION_ARN = os.environ.get('EMBEDDINGS_FUNCTION_ARN')
DYNAMODB_TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME')
DEFAULT_CHUNKING_STRATEGY = {
    'max_tokens': 512,
    'overlap_percentage': 20
}

# AWS clients
lambda_client = boto3.client('lambda')
dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')


def get_table():
    """Get DynamoDB table"""
    return dynamodb.Table(DYNAMODB_TABLE_NAME)


def get_document_state(s3_uri: str, version_id: str) -> Optional[Dict[str, Any]]:
    """Check if document has been processed"""
    table = get_table()
    try:
        response = table.get_item(
            Key={
                's3_uri': s3_uri,
                'version_id': version_id
            }
        )
        return response.get('Item')
    except Exception as e:
        print(f"Error getting document state: {str(e)}")
        return None


def update_document_state(
    s3_uri: str,
    version_id: str,
    status: str,
    knowledge_base: str,
    file_size_bytes: int = 0,
    content_type: str = '',
    chunks_created: int = 0,
    vectors_inserted: int = 0,
    error_message: str = ''
):
    """Update document processing state in DynamoDB"""
    table = get_table()

    item = {
        's3_uri': s3_uri,
        'version_id': version_id,
        'status': status,
        'knowledge_base': knowledge_base,
        'file_size_bytes': file_size_bytes,
        'content_type': content_type,
    }

    if status == 'PROCESSING':
        item['processing_started_at'] = int(time.time())
    elif status in ['COMPLETED', 'FAILED']:
        item['processing_completed_at'] = int(time.time())

    if chunks_created > 0:
        item['chunks_created'] = chunks_created
    if vectors_inserted > 0:
        item['vectors_inserted'] = vectors_inserted
    if error_message:
        item['error_message'] = error_message

    table.put_item(Item=item)
    print(f"Updated state: {s3_uri} → {status}")


def extract_knowledge_base_from_key(key: str) -> str:
    """
    Extract knowledge base name from S3 key with validation
    Expects format: {knowledge_base}/path/to/file.pdf
    Examples:
      - hpc/doc.pdf → hpc
      - presidio/guides/setup.md → presidio
      - raw/test.pdf → raw

    Security: Only allows alphanumeric, underscore, hyphen (1-50 chars)
    Prevents: Path traversal, injection attacks
    """
    parts = key.split('/')
    if len(parts) > 1:
        kb_candidate = parts[0]
        # Validate: only alphanumeric, underscore, hyphen, 1-50 chars
        if re.match(r'^[a-zA-Z0-9_-]{1,50}$', kb_candidate):
            return kb_candidate
        else:
            print(f"Invalid KB name: {kb_candidate}, using 'default'")
            return 'default'
    return 'default'


def invoke_embeddings_lambda(
    s3_uri: str,
    knowledge_base: str,
    chunking_strategy: Dict[str, Any]
) -> Dict[str, Any]:
    """Invoke embeddings Lambda function"""
    payload = {
        's3_uri': s3_uri,
        'knowledge_base': knowledge_base,
        'chunking_strategy': chunking_strategy
    }

    print(f"Invoking embeddings Lambda: {EMBEDDINGS_FUNCTION_ARN}")
    print(f"Payload: {json.dumps(payload)}")

    response = lambda_client.invoke(
        FunctionName=EMBEDDINGS_FUNCTION_ARN,
        InvocationType='RequestResponse',  # Synchronous
        Payload=json.dumps(payload)
    )

    response_payload = json.loads(response['Payload'].read())
    print(f"Embeddings Lambda response: {response_payload}")

    return response_payload


def process_s3_event(s3_event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a single S3 event

    S3 event format from SQS:
    {
      "Records": [{
        "s3": {
          "bucket": {"name": "bucket-name"},
          "object": {
            "key": "hpc/doc.pdf",
            "size": 12345,
            "versionId": "version-id"
          }
        }
      }]
    }
    """
    # Parse S3 event
    s3_record = s3_event['Records'][0]['s3']
    bucket = s3_record['bucket']['name']
    key = s3_record['object']['key']
    version_id = s3_record['object'].get('versionId', 'null')
    file_size = s3_record['object'].get('size', 0)

    s3_uri = f"s3://{bucket}/{key}"
    knowledge_base = extract_knowledge_base_from_key(key)

    print(f"Processing: {s3_uri} (KB: {knowledge_base}, Version: {version_id})")

    # Check if already processed (idempotency)
    existing_state = get_document_state(s3_uri, version_id)
    if existing_state and existing_state.get('status') == 'COMPLETED':
        print(f"Document already processed successfully, skipping: {s3_uri}")
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Document already processed',
                's3_uri': s3_uri,
                'status': 'SKIPPED'
            })
        }

    # Get content type from S3 metadata
    try:
        head_response = s3_client.head_object(Bucket=bucket, Key=key)
        content_type = head_response.get('ContentType', 'application/octet-stream')
    except Exception as e:
        print(f"Error getting S3 metadata: {str(e)}")
        content_type = 'unknown'

    # Update state: PROCESSING
    update_document_state(
        s3_uri=s3_uri,
        version_id=version_id,
        status='PROCESSING',
        knowledge_base=knowledge_base,
        file_size_bytes=file_size,
        content_type=content_type
    )

    try:
        # Invoke embeddings Lambda
        embeddings_response = invoke_embeddings_lambda(
            s3_uri=s3_uri,
            knowledge_base=knowledge_base,
            chunking_strategy=DEFAULT_CHUNKING_STRATEGY
        )

        # Check if embeddings Lambda succeeded
        if embeddings_response.get('statusCode') == 200:
            body = json.loads(embeddings_response['body'])

            # Update state: COMPLETED
            update_document_state(
                s3_uri=s3_uri,
                version_id=version_id,
                status='COMPLETED',
                knowledge_base=knowledge_base,
                file_size_bytes=file_size,
                content_type=content_type,
                chunks_created=body.get('chunks_created', 0),
                vectors_inserted=body.get('vectors_inserted', 0)
            )

            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Document processed successfully',
                    's3_uri': s3_uri,
                    'status': 'COMPLETED',
                    'chunks_created': body.get('chunks_created', 0),
                    'vectors_inserted': body.get('vectors_inserted', 0)
                })
            }
        else:
            # Embeddings Lambda returned error
            error_msg = embeddings_response.get('body', 'Unknown error from embeddings Lambda')
            raise Exception(error_msg)

    except Exception as e:
        error_message = str(e)
        print(f"Error processing document: {error_message}")

        # Update state: FAILED
        update_document_state(
            s3_uri=s3_uri,
            version_id=version_id,
            status='FAILED',
            knowledge_base=knowledge_base,
            file_size_bytes=file_size,
            content_type=content_type,
            error_message=error_message
        )

        # Re-raise to trigger SQS retry
        raise


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler

    Receives SQS messages containing S3 events

    SQS Event format:
    {
      "Records": [{
        "body": "<S3 event JSON>"
      }]
    }
    """
    print(f"Received event: {json.dumps(event)}")

    results = []

    for record in event.get('Records', []):
        try:
            # Parse S3 event from SQS message body
            s3_event = json.loads(record['body'])

            # Process document
            result = process_s3_event(s3_event)
            results.append(result)

        except Exception as e:
            print(f"Error processing record: {str(e)}")
            import traceback
            traceback.print_exc()

            # For SQS, we raise to trigger retry/DLQ
            raise

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': f'Processed {len(results)} documents',
            'results': results
        })
    }
