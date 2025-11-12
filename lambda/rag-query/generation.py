"""
Answer Generation Module
LLM-powered answer generation with retrieval context

Model Priority:
1. Claude 3.5 Sonnet (primary) - Best reasoning, context understanding
2. Claude 3 Haiku (fast fallback) - Quick answers for simple queries
3. GPT-OSS 120B (future) - When available on Bedrock in us-west-2

KB-agnostic design: System prompts adapt to any knowledge base via metadata
"""

import json
import os
import time
import boto3
from typing import Dict, Any, List
from kb_config import get_kb_metadata
from botocore.config import Config


# Model IDs
CLAUDE_SONNET_MODEL = "anthropic.claude-3-5-sonnet-20241022-v2:0"
CLAUDE_HAIKU_MODEL = "anthropic.claude-3-haiku-20240307-v1:0"
# GPT_OSS_MODEL = "openai.gpt-oss-120b-v1"  # Placeholder for future

# Configure retry logic
retry_config = Config(
    retries={'max_attempts': 3, 'mode': 'adaptive'},
    read_timeout=300  # 5 min for long responses
)

bedrock_client = boto3.client(
    'bedrock-runtime',
    region_name=os.environ.get('AWS_REGION', 'us-east-1'),
    config=retry_config
)


def build_system_prompt(knowledge_base: str) -> str:
    """
    Build KB-agnostic system prompt with domain hints

    Args:
        knowledge_base: KB identifier (e.g., 'hpc', 'presidio')

    Returns:
        System prompt tailored to the KB domain
    """
    kb_meta = get_kb_metadata(knowledge_base)

    system_prompt = f"""You are a technical expert assistant for the {kb_meta['name']} knowledge base.

Your expertise covers: {kb_meta['domain_hint']}

Your role:
- Answer questions using ONLY the provided context documents
- Provide technically accurate, actionable answers
- Cite specific documents when making claims
- Be concise but comprehensive (aim for 3-5 paragraphs)
- If the context doesn't contain the answer, say so explicitly

Response format:
1. Direct answer to the question
2. Supporting details and explanations
3. Relevant commands, configurations, or procedures (if applicable)
4. Caveats or important notes (if applicable)

Quality standards:
- Technical accuracy is paramount
- Use domain-specific terminology correctly
- Provide concrete examples when possible
- Flag any ambiguities or missing information"""

    return system_prompt


def format_context(chunks: List[Dict[str, Any]]) -> str:
    """
    Format retrieved chunks into LLM context

    Args:
        chunks: List of retrieved chunks with metadata

    Returns:
        Formatted context string for LLM prompt
    """
    if not chunks:
        return "No relevant context found."

    context_parts = []

    for i, chunk in enumerate(chunks, 1):
        source_file = chunk.get('source_file', 'unknown')
        chunk_index = chunk.get('chunk_index', 0)
        chunk_text = chunk.get('chunk_text', '')
        distance = chunk.get('distance', 0.0)

        # Format: [Source N] file.pdf (chunk 5, relevance: 0.92)
        header = f"[Source {i}] {source_file.split('/')[-1]} (chunk {chunk_index}, distance: {distance:.3f})"

        context_parts.append(f"{header}\n{chunk_text}")

    return "\n\n---\n\n".join(context_parts)


def invoke_claude(
    system_prompt: str,
    user_message: str,
    model_id: str = CLAUDE_SONNET_MODEL,
    max_tokens: int = 2048,
    temperature: float = 0.3
) -> Dict[str, Any]:
    """
    Invoke Claude model via Bedrock

    Args:
        system_prompt: System instructions
        user_message: User query with context
        model_id: Claude model ID
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature (0.0-1.0)

    Returns:
        Dict with 'answer', 'model_used', 'generation_time_ms'

    Raises:
        Exception: If Bedrock invocation fails
    """
    start_time = time.time()

    try:
        request_body = {
            'anthropic_version': 'bedrock-2023-05-31',
            'max_tokens': max_tokens,
            'temperature': temperature,
            'system': system_prompt,
            'messages': [
                {
                    'role': 'user',
                    'content': user_message
                }
            ]
        }

        response = bedrock_client.invoke_model(
            modelId=model_id,
            body=json.dumps(request_body)
        )

        response_body = json.loads(response['body'].read())
        answer = response_body['content'][0]['text']

        elapsed_ms = int((time.time() - start_time) * 1000)

        return {
            'answer': answer,
            'model_used': model_id,
            'generation_time_ms': elapsed_ms,
            'stop_reason': response_body.get('stop_reason', 'unknown')
        }

    except Exception as e:
        print(f"[Generation] Claude invocation failed: {str(e)}")
        raise


def generate_answer(
    question: str,
    context_chunks: List[Dict[str, Any]],
    knowledge_base: str,
    model_preference: str = 'sonnet'
) -> Dict[str, Any]:
    """
    Generate answer using LLM with retrieval context

    Auto-fallback strategy:
    1. Try Claude 3.5 Sonnet (best quality)
    2. Fall back to Claude 3 Haiku if Sonnet fails

    Args:
        question: User's question
        context_chunks: Retrieved and reranked chunks
        knowledge_base: KB identifier
        model_preference: 'sonnet' (default) or 'haiku'

    Returns:
        Dict with answer, model used, and metadata
    """
    # Build KB-agnostic system prompt
    system_prompt = build_system_prompt(knowledge_base)

    # Format context
    formatted_context = format_context(context_chunks)

    # Build user message
    user_message = f"""Context documents:

{formatted_context}

---

Question: {question}

Please provide a comprehensive answer based solely on the context documents above. If the context doesn't contain enough information to answer the question, state this clearly."""

    print(f"[Generation] Generating answer for KB '{knowledge_base}'")
    print(f"[Generation] Context length: {len(formatted_context)} chars")

    # Try primary model
    try:
        if model_preference == 'haiku':
            result = invoke_claude(
                system_prompt=system_prompt,
                user_message=user_message,
                model_id=CLAUDE_HAIKU_MODEL,
                max_tokens=1024,
                temperature=0.3
            )
        else:
            # Sonnet (default)
            result = invoke_claude(
                system_prompt=system_prompt,
                user_message=user_message,
                model_id=CLAUDE_SONNET_MODEL,
                max_tokens=2048,
                temperature=0.3
            )

        print(f"[Generation] Success with {result['model_used']}")
        print(f"[Generation] Answer length: {len(result['answer'])} chars")
        print(f"[Generation] Generation time: {result['generation_time_ms']}ms")

        return result

    except Exception as e:
        print(f"[Generation] Primary model failed: {str(e)}")

        # Fallback to Haiku if Sonnet failed
        if model_preference != 'haiku':
            print("[Generation] Falling back to Claude Haiku...")
            try:
                result = invoke_claude(
                    system_prompt=system_prompt,
                    user_message=user_message,
                    model_id=CLAUDE_HAIKU_MODEL,
                    max_tokens=1024,
                    temperature=0.3
                )
                result['fallback'] = True
                return result

            except Exception as fallback_error:
                print(f"[Generation] Fallback also failed: {str(fallback_error)}")
                raise

        # No fallback available
        raise


def generate_streaming_answer(
    question: str,
    context_chunks: List[Dict[str, Any]],
    knowledge_base: str
):
    """
    Generate answer with streaming response (future enhancement)

    Useful for long answers where we want to start displaying results
    before the full response is complete.

    Args:
        question: User's question
        context_chunks: Retrieved chunks
        knowledge_base: KB identifier

    Yields:
        Answer chunks as they're generated
    """
    # Placeholder for future streaming implementation
    # Bedrock supports streaming via invoke_model_with_response_stream
    raise NotImplementedError("Streaming not yet implemented")
