"""
Reranking Module
Reciprocal Rank Fusion (RRF) for combining multiple retrieval result sets

RRF is a simple but effective algorithm for combining ranked lists:
- Doesn't require score normalization (unlike CombSUM/CombMNZ)
- Robust to differences in score scales across different retrievers
- Typically outperforms simple score averaging

Research: Cormack et al. (2009) - "Reciprocal Rank Fusion outperforms
the best known automatic evaluation measures based on relevance judgments"
"""

from typing import List, Dict, Any
from collections import defaultdict


def reciprocal_rank_fusion(
    results_lists: List[List[Dict[str, Any]]],
    weights: List[float] = None,
    k: int = 60
) -> List[Dict[str, Any]]:
    """
    Combine multiple ranked result lists using Reciprocal Rank Fusion

    Args:
        results_lists: List of result lists from different retrievers
                      Each result dict must have 'id' field
        weights: Optional weights for each result list (default: equal weights)
                Example: [0.7, 0.3] gives 70% weight to first list
        k: RRF constant (default: 60, from original paper)
           Higher k = less emphasis on rank position

    Returns:
        Combined and reranked results, sorted by RRF score (descending)

    Example:
        hyde_results = [{'id': 'doc1', ...}, {'id': 'doc2', ...}]
        direct_results = [{'id': 'doc2', ...}, {'id': 'doc3', ...}]

        combined = reciprocal_rank_fusion(
            [hyde_results, direct_results],
            weights=[0.7, 0.3]  # Prefer HyDE results
        )
        # doc2 will rank highest (appears in both lists)
    """
    # Default to equal weights if not specified
    if weights is None:
        weights = [1.0] * len(results_lists)

    # Normalize weights to sum to 1.0
    weight_sum = sum(weights)
    normalized_weights = [w / weight_sum for w in weights]

    # Calculate RRF scores
    rrf_scores = defaultdict(float)
    result_map = {}  # Store full result objects by ID

    for results, weight in zip(results_lists, normalized_weights):
        for rank, result in enumerate(results):
            doc_id = result['id']

            # RRF formula: weight / (k + rank + 1)
            # rank is 0-indexed, so first result has rank=0
            rrf_score = weight / (k + rank + 1)
            rrf_scores[doc_id] += rrf_score

            # Store full result object (use first occurrence)
            if doc_id not in result_map:
                result_map[doc_id] = result

    # Sort by RRF score (descending)
    sorted_ids = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

    # Build final result list with RRF scores
    reranked_results = []
    for doc_id, score in sorted_ids:
        result = result_map[doc_id].copy()
        result['rrf_score'] = score
        reranked_results.append(result)

    return reranked_results


def format_reranked_results(
    results: List[Dict[str, Any]],
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Format reranked results for LLM context

    Args:
        results: Reranked results from RRF or direct search
        top_k: Number of top results to return

    Returns:
        Top-K results, deduplicated and formatted
    """
    # Take top-K results
    top_results = results[:top_k]

    # Deduplicate by chunk_text (in case of duplicates)
    seen_texts = set()
    deduplicated = []

    for result in top_results:
        chunk_text = result.get('chunk_text', '')
        text_signature = chunk_text[:200]  # Use first 200 chars for dedup

        if text_signature not in seen_texts:
            seen_texts.add(text_signature)
            deduplicated.append(result)

    return deduplicated


def calculate_diversity_score(results: List[Dict[str, Any]]) -> float:
    """
    Calculate diversity of result set based on source files

    Higher diversity = results from more different source files
    Useful metric for evaluating retrieval quality

    Args:
        results: List of results with 'source_file' field

    Returns:
        Diversity score (0.0 to 1.0)
        - 1.0 = all results from different files
        - 0.0 = all results from same file
    """
    if not results:
        return 0.0

    unique_sources = set(r.get('source_file', '') for r in results)
    diversity = (len(unique_sources) - 1) / max(len(results) - 1, 1)

    return diversity


def explain_ranking(
    original_results: List[Dict[str, Any]],
    reranked_results: List[Dict[str, Any]],
    top_k: int = 5
) -> Dict[str, Any]:
    """
    Generate ranking explanation for debugging

    Shows how RRF changed the ordering compared to original results

    Args:
        original_results: Original results before reranking
        reranked_results: Results after RRF
        top_k: Number of results to explain

    Returns:
        Explanation dict with rank changes
    """
    original_ranks = {r['id']: i for i, r in enumerate(original_results)}

    explanations = []
    for new_rank, result in enumerate(reranked_results[:top_k]):
        doc_id = result['id']
        old_rank = original_ranks.get(doc_id, -1)

        explanations.append({
            'id': doc_id,
            'source_file': result.get('source_file', 'unknown'),
            'old_rank': old_rank,
            'new_rank': new_rank,
            'rank_change': old_rank - new_rank if old_rank >= 0 else None,
            'rrf_score': result.get('rrf_score', 0.0),
            'preview': result.get('chunk_text', '')[:100]
        })

    return {
        'top_k': top_k,
        'diversity_score': calculate_diversity_score(reranked_results[:top_k]),
        'rank_changes': explanations
    }
