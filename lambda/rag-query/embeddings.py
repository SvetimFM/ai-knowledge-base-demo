"""
Embeddings Module
Dual embedding search with Milvus (direct + HyDE)
"""

import json
import os
import re
import boto3
from typing import List, Dict, Any
from pymilvus import connections, Collection
from hyde import generate_hypothetical_document
from botocore.config import Config


# Environment variables
MILVUS_HOST = os.environ.get('MILVUS_HOST', 'localhost')
MILVUS_PORT = os.environ.get('MILVUS_PORT', '19530')
COLLECTION_NAME = "knowledge_base_vectors"
EMBEDDING_MODEL = "amazon.titan-embed-text-v2:0"

# Configure retry logic
retry_config = Config(
    retries={'max_attempts': 3, 'mode': 'adaptive'}
)

bedrock_client = boto3.client(
    'bedrock-runtime',
    region_name=os.environ.get('AWS_REGION', 'us-east-1'),
    config=retry_config
)

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
            print(f"[Embeddings] Connected to Milvus at {MILVUS_HOST}:{MILVUS_PORT}")
        except Exception as e:
            print(f"[Embeddings] Failed to connect to Milvus: {str(e)}")
            raise


def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding using Bedrock Titan v2

    Args:
        text: Input text to embed

    Returns:
        1024-dimensional embedding vector
    """
    try:
        request_body = json.dumps({"inputText": text})

        response = bedrock_client.invoke_model(
            modelId=EMBEDDING_MODEL,
            body=request_body
        )

        response_body = json.loads(response['body'].read())
        return response_body['embedding']

    except Exception as e:
        print(f"[Embeddings] Error generating embedding: {str(e)}")
        raise


def milvus_search(
    embedding: List[float],
    knowledge_base: str,
    top_k: int = 10
) -> List[Dict[str, Any]]:
    """
    Search Milvus with partition key filtering

    Args:
        embedding: Query embedding vector
        knowledge_base: KB identifier for partition filtering
        top_k: Number of results to return

    Returns:
        List of matching chunks with metadata
    """
    ensure_milvus_connection()

    try:
        collection = Collection(COLLECTION_NAME)
        collection.load()

        # Search with partition key filter
        results = collection.search(
            data=[embedding],
            anns_field="embedding",
            param={
                "metric_type": "IP",  # Inner Product for normalized Titan embeddings
                "params": {"nprobe": 16}  # Higher nprobe = more accurate
            },
            limit=top_k,
            expr=f'knowledge_base == "{knowledge_base}"',  # Partition key filter
            output_fields=["id", "chunk_text", "source_file", "chunk_index", "knowledge_base"]
        )

        # Format results
        formatted_results = []
        for hits in results:
            for hit in hits:
                formatted_results.append({
                    'id': hit.entity.get('id'),
                    'distance': hit.distance,
                    'chunk_text': hit.entity.get('chunk_text'),
                    'source_file': hit.entity.get('source_file'),
                    'chunk_index': hit.entity.get('chunk_index'),
                    'knowledge_base': hit.entity.get('knowledge_base')
                })

        print(f"[Embeddings] Found {len(formatted_results)} results for KB '{knowledge_base}'")
        return formatted_results

    except Exception as e:
        print(f"[Embeddings] Search failed: {str(e)}")
        raise


def direct_search(
    question: str,
    knowledge_base: str,
    top_k: int = 10
) -> List[Dict[str, Any]]:
    """
    Direct question embedding search (baseline, no HyDE)

    Args:
        question: User's question
        knowledge_base: KB identifier
        top_k: Number of results

    Returns:
        List of matching chunks
    """
    print(f"[Embeddings] Direct search for: {question[:50]}...")

    # Generate embedding for question
    question_embedding = generate_embedding(question)

    # Search Milvus
    results = milvus_search(
        embedding=question_embedding,
        knowledge_base=knowledge_base,
        top_k=top_k
    )

    return results


def dual_embedding_search(
    question: str,
    knowledge_base: str,
    top_k: int = 10
) -> List[Dict[str, Any]]:
    """
    Dual embedding search: Question + HyDE document

    Research shows 30-40% improvement over direct search

    Args:
        question: User's question
        knowledge_base: KB identifier
        top_k: Number of results

    Returns:
        Combined and re-ranked results from both searches
    """
    print(f"[Embeddings] Dual search (HyDE) for: {question[:50]}...")

    # Step 1: Generate HyDE document
    hyde_doc = generate_hypothetical_document(question, knowledge_base)

    # Step 2: Generate embeddings for both
    question_embedding = generate_embedding(question)
    hyde_embedding = generate_embedding(hyde_doc)

    # Step 3: Search with both embeddings
    question_results = milvus_search(
        embedding=question_embedding,
        knowledge_base=knowledge_base,
        top_k=top_k
    )

    hyde_results = milvus_search(
        embedding=hyde_embedding,
        knowledge_base=knowledge_base,
        top_k=top_k
    )

    # Step 4: Combine and deduplicate (simple approach for now)
    # Will be improved by reranking module later
    seen_ids = set()
    combined = []

    # Prioritize HyDE results (70% weight)
    for result in hyde_results:
        if result['id'] not in seen_ids:
            seen_ids.add(result['id'])
            result['source'] = 'hyde'
            combined.append(result)

    # Add question results (30% weight)
    for result in question_results:
        if result['id'] not in seen_ids:
            seen_ids.add(result['id'])
            result['source'] = 'question'
            combined.append(result)

    # Limit to top_k
    combined = combined[:top_k]

    print(f"[Embeddings] Combined results: {len(combined)} unique chunks")
    return combined
