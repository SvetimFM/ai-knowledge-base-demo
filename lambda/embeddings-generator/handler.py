"""
Embeddings Generator Lambda
Converts documents to embeddings using Bedrock Titan v2 and stores in Milvus
"""

import json
import os
import boto3
import uuid
import io
from typing import Dict, Any, List
from urllib.parse import urlparse
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
from PyPDF2 import PdfReader

# Environment variables
MILVUS_HOST = os.environ.get('MILVUS_HOST', 'localhost')
MILVUS_PORT = os.environ.get('MILVUS_PORT', '19530')
BEDROCK_REGION = os.environ.get('AWS_REGION', 'us-east-1')
DOCUMENTS_BUCKET_NAME = os.environ.get('DOCUMENTS_BUCKET_NAME', '')

# Constants
COLLECTION_NAME = "knowledge_base_vectors"
EMBEDDING_MODEL = "amazon.titan-embed-text-v2:0"
EMBEDDING_DIM = 1024

# Security limits
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
MAX_CHUNKS = 1000  # Limit total chunks per document

# AWS clients with retry configuration
from botocore.config import Config

retry_config = Config(
    retries={
        'max_attempts': 3,
        'mode': 'adaptive'  # Exponential backoff for throttling
    }
)

s3_client = boto3.client('s3', config=retry_config)
bedrock_client = boto3.client('bedrock-runtime', region_name=BEDROCK_REGION, config=retry_config)

# Global Milvus connection
_is_connected = False


def ensure_milvus_connection():
    """Establish connection to Milvus if not already connected"""
    global _is_connected

    if not _is_connected:
        try:
            connections.connect(
                alias="default",
                host=MILVUS_HOST,
                port=MILVUS_PORT
            )
            _is_connected = True
            print(f"Connected to Milvus at {MILVUS_HOST}:{MILVUS_PORT}")
        except Exception as e:
            print(f"Failed to connect to Milvus: {str(e)}")
            raise


def ensure_collection_exists():
    """Create collection if it doesn't exist"""
    ensure_milvus_connection()

    if utility.has_collection(COLLECTION_NAME):
        print(f"Collection '{COLLECTION_NAME}' already exists")
        return

    # Define schema with partition key
    fields = [
        FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=36),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=EMBEDDING_DIM),
        FieldSchema(name="knowledge_base", dtype=DataType.VARCHAR, max_length=100, is_partition_key=True),
        FieldSchema(name="source_file", dtype=DataType.VARCHAR, max_length=500),
        FieldSchema(name="chunk_index", dtype=DataType.INT64),
        FieldSchema(name="chunk_text", dtype=DataType.VARCHAR, max_length=8192),
        FieldSchema(name="timestamp", dtype=DataType.INT64),
    ]

    schema = CollectionSchema(
        fields=fields,
        description="Knowledge base vectors with partition key",
        enable_dynamic_field=True  # For additional metadata
    )

    # Create collection with auto-partitioning
    collection = Collection(name=COLLECTION_NAME, schema=schema)

    # Create index for vector search
    index_params = {
        "metric_type": "L2",
        "index_type": "IVF_FLAT",
        "params": {"nlist": 128}
    }
    collection.create_index(field_name="embedding", index_params=index_params)

    print(f"Created collection '{COLLECTION_NAME}' with partition key 'knowledge_base'")


def validate_s3_uri(s3_uri: str) -> None:
    """
    Validate S3 URI format and bucket access
    Security: Prevents SSRF and unauthorized bucket access
    """
    parsed = urlparse(s3_uri)

    # Check scheme
    if parsed.scheme != 's3':
        raise ValueError(f"Invalid S3 URI scheme: {parsed.scheme}")

    # Check bucket matches allowed bucket
    if DOCUMENTS_BUCKET_NAME and parsed.netloc != DOCUMENTS_BUCKET_NAME:
        raise ValueError(f"Access denied: bucket {parsed.netloc} not allowed")

    # Check key is not empty
    if not parsed.path or parsed.path == '/':
        raise ValueError("S3 key cannot be empty")


def download_from_s3(s3_uri: str) -> str:
    """Download file from S3 and return content with size validation"""
    # Validate S3 URI
    validate_s3_uri(s3_uri)

    parsed = urlparse(s3_uri)
    bucket = parsed.netloc
    key = parsed.path.lstrip('/')

    print(f"Downloading {key} from bucket {bucket}")

    try:
        # Check file size before downloading
        head_response = s3_client.head_object(Bucket=bucket, Key=key)
        file_size = head_response['ContentLength']

        if file_size > MAX_FILE_SIZE:
            raise ValueError(
                f"File too large: {file_size} bytes (max {MAX_FILE_SIZE})"
            )

        print(f"File size: {file_size} bytes")

        # Download file
        response = s3_client.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read()

        # Handle text files
        if key.endswith(('.txt', '.md')):
            return content.decode('utf-8')

        # Handle PDFs with PyPDF2
        elif key.endswith('.pdf'):
            pdf_file = io.BytesIO(content)
            pdf_reader = PdfReader(pdf_file)

            text_parts = []
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text.strip():  # Only add non-empty pages
                    text_parts.append(page_text)

            full_text = '\n\n'.join(text_parts)
            print(f"Extracted {len(text_parts)} pages from PDF, total {len(full_text)} characters")
            return full_text

        else:
            return content.decode('utf-8', errors='ignore')

    except Exception as e:
        print(f"Error downloading from S3: {str(e)}")
        raise


def chunk_text(text: str, strategy: Dict[str, Any]) -> List[str]:
    """
    Chunk text according to strategy

    Strategy format:
    {
        "max_tokens": 512,
        "overlap_percentage": 20
    }
    """
    max_tokens = strategy.get('max_tokens', 512)
    overlap_pct = strategy.get('overlap_percentage', 20)

    # Simple word-based chunking (approximate tokens)
    # In production, use tiktoken or similar for exact token counting
    words = text.split()
    words_per_chunk = max_tokens  # Rough approximation: 1 word ≈ 1 token
    overlap_words = int(words_per_chunk * overlap_pct / 100)

    chunks = []
    i = 0

    while i < len(words):
        chunk_end = min(i + words_per_chunk, len(words))
        chunk = ' '.join(words[i:chunk_end])
        chunks.append(chunk)

        if chunk_end >= len(words):
            break

        i += words_per_chunk - overlap_words

    print(f"Created {len(chunks)} chunks from text ({len(words)} words)")

    # Security: Limit total chunks
    if len(chunks) > MAX_CHUNKS:
        raise ValueError(
            f"Too many chunks: {len(chunks)}, max {MAX_CHUNKS}. "
            f"Consider increasing chunk size or splitting document."
        )

    return chunks


def generate_embedding(text: str) -> List[float]:
    """Generate embedding using Bedrock Titan v2"""
    try:
        request_body = json.dumps({
            "inputText": text
        })

        response = bedrock_client.invoke_model(
            modelId=EMBEDDING_MODEL,
            body=request_body
        )

        response_body = json.loads(response['body'].read())
        embedding = response_body['embedding']

        return embedding

    except Exception as e:
        print(f"Error generating embedding: {str(e)}")
        raise


def insert_embeddings(
    knowledge_base: str,
    source_file: str,
    chunks: List[str],
    embeddings: List[List[float]]
) -> int:
    """Insert embeddings into Milvus collection"""
    ensure_collection_exists()

    collection = Collection(COLLECTION_NAME)
    collection.load()

    # Prepare data for insertion
    import time
    timestamp = int(time.time())

    data = {
        "id": [str(uuid.uuid4()) for _ in chunks],
        "embedding": embeddings,
        "knowledge_base": [knowledge_base] * len(chunks),
        "source_file": [source_file] * len(chunks),
        "chunk_index": list(range(len(chunks))),
        "chunk_text": chunks,
        "timestamp": [timestamp] * len(chunks),
    }

    # Insert data
    insert_result = collection.insert(data)
    collection.flush()

    print(f"Inserted {insert_result.insert_count} vectors into '{COLLECTION_NAME}'")
    return insert_result.insert_count


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for embedding generation

    Expected event:
    {
        "s3_uri": "s3://bucket/path/to/document.pdf",
        "knowledge_base": "hpc",
        "chunking_strategy": {
            "max_tokens": 512,
            "overlap_percentage": 20
        }
    }
    """
    try:
        # Parse input
        s3_uri = event.get('s3_uri')
        knowledge_base = event.get('knowledge_base')
        chunking_strategy = event.get('chunking_strategy', {
            'max_tokens': 512,
            'overlap_percentage': 20
        })

        if not s3_uri or not knowledge_base:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 's3_uri and knowledge_base are required'})
            }

        print(f"Processing document: {s3_uri} for KB: {knowledge_base}")

        # Step 1: Download from S3
        text = download_from_s3(s3_uri)

        # Step 2: Chunk text
        chunks = chunk_text(text, chunking_strategy)

        # Step 3: Generate embeddings (batch for efficiency)
        embeddings = []
        for i, chunk in enumerate(chunks):
            print(f"Generating embedding for chunk {i+1}/{len(chunks)}")
            embedding = generate_embedding(chunk)
            embeddings.append(embedding)

        # Step 4: Insert into Milvus
        inserted_count = insert_embeddings(
            knowledge_base=knowledge_base,
            source_file=s3_uri,
            chunks=chunks,
            embeddings=embeddings
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Successfully processed document',
                'knowledge_base': knowledge_base,
                'source_file': s3_uri,
                'chunks_created': len(chunks),
                'vectors_inserted': inserted_count
            })
        }

    except Exception as e:
        print(f"Error processing document: {str(e)}")
        import traceback
        traceback.print_exc()

        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }
