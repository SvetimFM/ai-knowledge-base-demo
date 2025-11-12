"""
Knowledge Base Configuration
Metadata and domain hints for KB-agnostic RAG queries

Single source of truth for KB information - easy to extend
"""

from typing import Dict, List, Any


KB_METADATA = {
    'hpc': {
        'name': 'High Performance Computing',
        'domain_hint': 'GPU computing, distributed training, NCCL, RCCL, InfiniBand, RoCE, cluster management, CUDA, ROCm, MPI',
        'example_topics': [
            'CUDA programming and optimization',
            'Distributed training performance tuning',
            'Network fabric configuration (InfiniBand, RoCE)',
            'Slurm job scheduling and resource management',
            'NCCL/RCCL communication optimization',
            'GPU memory management',
            'LLM training and inference'
        ]
    },
    'presidio': {
        'name': 'Presidio IT Solutions',
        'domain_hint': 'cloud infrastructure, managed services, enterprise IT solutions, AWS architecture, IT consulting',
        'example_topics': [
            'Cloud migration strategies',
            'Managed AWS services',
            'Enterprise security solutions',
            'IT consulting best practices',
            'Infrastructure as Code',
            'DevOps and CI/CD pipelines'
        ]
    },
    'default': {
        'name': 'General Knowledge Base',
        'domain_hint': 'general technical documentation and best practices',
        'example_topics': []
    }
}


def get_kb_metadata(kb_name: str) -> Dict[str, Any]:
    """
    Get metadata for a knowledge base

    Args:
        kb_name: Knowledge base identifier (e.g., 'hpc', 'presidio')

    Returns:
        Dict with name, domain_hint, and example_topics
        Falls back to 'default' if KB not found
    """
    return KB_METADATA.get(kb_name, KB_METADATA['default'])


def list_knowledge_bases() -> List[str]:
    """
    List all configured knowledge bases

    Returns:
        List of KB identifiers
    """
    return [kb for kb in KB_METADATA.keys() if kb != 'default']


def validate_kb_name(kb_name: str) -> bool:
    """
    Validate if a knowledge base is configured

    Args:
        kb_name: Knowledge base identifier

    Returns:
        True if KB exists, False otherwise
    """
    return kb_name in KB_METADATA
