"""
RAG Query Lambda Handler
Main entry point for question-answering with retrieval-augmented generation

Flow:
1. Input validation and sanitization
2. Dual embedding search (direct + HyDE)
3. Reciprocal Rank Fusion reranking
4. LLM answer generation with GPT-OSS 120B
5. Response with citations
"""

import json
import os
import traceback
from typing import Dict, Any, List

# Import RAG modules
from kb_config import get_kb_metadata, validate_kb_name
from embeddings import dual_embedding_search, direct_search
from hyde import sanitize_user_input
from reranking import reciprocal_rank_fusion, format_reranked_results
from generation import generate_answer


def validate_input(event: Dict[str, Any]) -> Dict[str, str]:
    """
    Validate and extract input parameters from Lambda event

    Args:
        event: Lambda event payload

    Returns:
        Dict with validated 'question' and 'knowledge_base'

    Raises:
        ValueError: If required parameters are missing or invalid
    """
    # Extract question
    question = event.get('question', '').strip()
    if not question:
        raise ValueError("Missing required parameter: 'question'")

    # Extract knowledge base (default to 'hpc')
    knowledge_base = event.get('knowledge_base', 'hpc').strip().lower()

    # Validate KB name exists
    if not validate_kb_name(knowledge_base):
        raise ValueError(
            f"Invalid knowledge_base: '{knowledge_base}'. "
            f"Use one of: hpc, presidio"
        )

    # Sanitize question (defense in depth)
    try:
        safe_question = sanitize_user_input(question, max_length=500)
    except ValueError as e:
        raise ValueError(f"Invalid question: {str(e)}")

    return {
        'question': safe_question,
        'knowledge_base': knowledge_base
    }


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for RAG query pipeline

    Expected event:
    {
        "question": "How do I optimize NCCL performance?",
        "knowledge_base": "hpc",  # Optional, defaults to 'hpc'
        "top_k": 10,              # Optional, number of results to retrieve
        "use_hyde": true          # Optional, enable HyDE (defaults to true)
    }

    Response:
    {
        "statusCode": 200,
        "body": {
            "answer": "To optimize NCCL performance...",
            "sources": [
                {
                    "file": "s3://bucket/hpc/nccl-tuning.pdf",
                    "chunk_index": 5,
                    "relevance_score": 0.92
                }
            ],
            "knowledge_base": "hpc",
            "query_method": "dual_hyde"
        }
    }
    """
    try:
        print(f"[Handler] Received event: {json.dumps(event)}")

        # Step 1: Validate input
        validated = validate_input(event)
        question = validated['question']
        knowledge_base = validated['knowledge_base']

        # Optional parameters
        top_k = event.get('top_k', 10)
        use_hyde = event.get('use_hyde', True)

        print(f"[Handler] Question: {question[:100]}...")
        print(f"[Handler] KB: {knowledge_base}, Top-K: {top_k}, HyDE: {use_hyde}")

        # Step 2: Retrieve relevant chunks
        if use_hyde:
            # Dual embedding search (HyDE + direct)
            retrieval_results = dual_embedding_search(
                question=question,
                knowledge_base=knowledge_base,
                top_k=top_k
            )
            query_method = "dual_hyde"
        else:
            # Direct embedding only
            retrieval_results = direct_search(
                question=question,
                knowledge_base=knowledge_base,
                top_k=top_k
            )
            query_method = "direct"

        if not retrieval_results:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'error': 'No relevant documents found',
                    'knowledge_base': knowledge_base,
                    'query_method': query_method
                })
            }

        print(f"[Handler] Retrieved {len(retrieval_results)} chunks")

        # Step 3: Rerank results (if using HyDE, RRF is already applied in embeddings.py)
        # For direct search, we can still use RRF if we have multiple result sets
        # For now, we'll just format the results
        formatted_context = format_reranked_results(retrieval_results, top_k=5)

        print(f"[Handler] Using top {len(formatted_context)} chunks for context")

        # Step 4: Generate answer with LLM
        answer_result = generate_answer(
            question=question,
            context_chunks=formatted_context,
            knowledge_base=knowledge_base
        )

        # Step 5: Build response with sources
        sources = []
        for chunk in formatted_context:
            sources.append({
                'file': chunk.get('source_file', 'unknown'),
                'chunk_index': chunk.get('chunk_index', 0),
                'distance': chunk.get('distance', 0.0),
                'preview': chunk.get('chunk_text', '')[:150] + '...'
            })

        response_body = {
            'answer': answer_result['answer'],
            'sources': sources,
            'knowledge_base': knowledge_base,
            'query_method': query_method,
            'model_used': answer_result.get('model_used', 'unknown'),
            'metadata': {
                'chunks_retrieved': len(retrieval_results),
                'chunks_used': len(formatted_context),
                'generation_time_ms': answer_result.get('generation_time_ms', 0)
            }
        }

        print(f"[Handler] Success! Answer length: {len(answer_result['answer'])} chars")

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'  # CORS for API Gateway
            },
            'body': json.dumps(response_body, indent=2)
        }

    except ValueError as e:
        # Validation errors
        print(f"[Handler] Validation error: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'Invalid input',
                'message': str(e)
            })
        }

    except Exception as e:
        # Unexpected errors
        print(f"[Handler] Error: {str(e)}")
        traceback.print_exc()

        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }
