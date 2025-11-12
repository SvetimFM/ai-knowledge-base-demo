"""
HyDE (Hypothetical Document Embeddings) Module
Generates hypothetical documents to improve retrieval accuracy

Research shows 30-40% improvement in precision vs direct question embedding
"""

import json
import os
import re
import html
import boto3
from kb_config import get_kb_metadata
from botocore.config import Config


# Configure retry logic
retry_config = Config(
    retries={'max_attempts': 3, 'mode': 'adaptive'}
)

bedrock_client = boto3.client(
    'bedrock-runtime',
    region_name=os.environ.get('AWS_REGION', 'us-east-1'),
    config=retry_config
)


def sanitize_user_input(text: str, max_length: int = 500) -> str:
    """
    Sanitize user input to prevent prompt injection attacks

    Security measures:
    - Length limiting (prevent excessive LLM costs)
    - Control character removal (prevent prompt manipulation)
    - HTML escaping (prevent XSS-like attacks)
    - Malicious pattern detection (basic jailbreak attempts)

    Args:
        text: User input to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized text

    Raises:
        ValueError: If malicious input is detected
    """
    # Truncate to max length
    text = text[:max_length]

    # Remove control characters (except newline, tab)
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)

    # HTML escape to prevent injection
    text = html.escape(text, quote=False)

    # Detect common jailbreak patterns
    dangerous_patterns = [
        r'ignore\s+previous\s+instructions',
        r'ignore\s+all\s+previous',
        r'system\s+prompt',
        r'you\s+are\s+now',
        r'new\s+instructions',
        r'disregard\s+previous',
        r'forget\s+everything',
        r'act\s+as',
        r'pretend\s+to\s+be',
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            raise ValueError(f"Potentially malicious input detected: pattern '{pattern}'")

    return text


def generate_hypothetical_document(
    question: str,
    knowledge_base: str
) -> str:
    """
    Generate KB-agnostic hypothetical document with domain hints

    Uses fast LLM (Claude Haiku) to create synthetic document
    that matches the style/content of the target KB

    Args:
        question: User's question
        knowledge_base: KB identifier (e.g., 'hpc', 'presidio')

    Returns:
        Hypothetical document text (3-5 sentences)

    Example:
        question = "GPUs underutilized during training"
        kb = "hpc"
        → "GPU underutilization in distributed training stems from
           communication bottlenecks in collective operations..."
    """

    # Sanitize user input to prevent prompt injection
    safe_question = sanitize_user_input(question, max_length=500)

    # Get KB metadata for context
    kb_meta = get_kb_metadata(knowledge_base)

    # Build generic prompt with KB context injection
    prompt = f"""You are writing technical documentation for the "{kb_meta['name']}" knowledge base.

Domain: {kb_meta['domain_hint']}

Write a concise technical document (3-5 sentences) that would contain the answer to this question:

Question: {safe_question}

Write as if this is an excerpt from documentation, NOT a conversational response. Focus on:
- Technical accuracy and specificity
- Relevant terminology from the domain
- Actionable information (commands, configurations, procedures)
- Common troubleshooting steps if applicable

Document:"""

    try:
        response = bedrock_client.invoke_model(
            modelId='anthropic.claude-3-haiku-20240307-v1:0',
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 500,
                'temperature': 0.3,  # Low temp for consistency
                'messages': [{'role': 'user', 'content': prompt}]
            })
        )

        result = json.loads(response['body'].read())
        hyde_doc = result['content'][0]['text']

        print(f"[HyDE] Generated {len(hyde_doc)} chars for KB '{knowledge_base}'")
        return hyde_doc

    except Exception as e:
        print(f"[HyDE] Error generating hypothetical document: {str(e)}")
        # Fallback: return original question
        return question
