#!/usr/bin/env python3
"""
Build optimized data files for the static document explorer UI.

Generates:
1. manifest.json - Compact document metadata for browsing
2. search-corpus.json - Text corpus for Lunr.js index building
3. stats.json - Aggregated statistics for dashboard
4. entities.json - Entity search index for type-ahead
5. entity_profiles/*.json - Per-entity profile data

Usage:
    python scripts/build_frontend_data.py
    python scripts/build_frontend_data.py --entities  # Only build entity data
"""

import json
import os
import sys
from pathlib import Path
from collections import defaultdict
import datetime

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"
DOCS_DATA_DIR = PROJECT_ROOT / "docs" / "data"
VIZ_DIR = DOCS_DATA_DIR / "viz"

# HuggingFace base URL
HF_BASE_URL = "https://huggingface.co/datasets/svetfm/epstein-fbi-files/resolve/main"

# Key players to prioritize
KEY_PLAYERS = {
    "maxwell": {"full_name": "Ghislaine Maxwell", "aliases": ["ghislaine", "g. maxwell"]},
    "epstein": {"full_name": "Jeffrey Epstein", "aliases": ["jeffrey", "j. epstein"]},
    "andrew": {"full_name": "Prince Andrew", "aliases": ["prince andrew", "duke of york"]},
    "clinton": {"full_name": "Bill Clinton", "aliases": ["bill", "president clinton"]},
    "trump": {"full_name": "Donald Trump", "aliases": ["donald"]},
    "dershowitz": {"full_name": "Alan Dershowitz", "aliases": ["alan"]},
    "wexner": {"full_name": "Les Wexner", "aliases": ["les", "leslie"]},
    "virginia": {"full_name": "Virginia Giuffre", "aliases": ["giuffre", "roberts"]},
    "brunel": {"full_name": "Jean-Luc Brunel", "aliases": ["jean-luc"]},
}


def load_json(path: Path) -> dict:
    """Load JSON file."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def build_manifest():
    """
    Build compact manifest.json for frontend.

    Strips to essential fields only:
    - id: bates number
    - vol: volume number
    - path: relative path for PDF URL
    - pages: page count
    - cat: category (abbreviated)
    - conf: classification confidence
    """
    print("Building manifest.json...")

    # Load source data
    manifest = load_json(OUTPUT_DIR / "document_manifest.json")
    classifications = load_json(OUTPUT_DIR / "classification_results.json")

    # Build classification lookup
    class_lookup = {r['bates_number']: r for r in classifications['results']}

    # Build compact documents list
    documents = []
    for doc in manifest['documents']:
        bates = doc['bates_number']
        classification = class_lookup.get(bates, {})

        # Build volume-prefixed path for HuggingFace
        vol_folder = f"VOL{doc['volume']:05d}"
        pdf_path = f"{vol_folder}/{doc['relative_path']}"

        compact_doc = {
            'id': bates,
            'vol': doc['volume'],
            'path': pdf_path,
            'pages': doc['page_count'],
            'cat': classification.get('category', 'unknown'),
            'conf': round(classification.get('confidence', 0), 2),
        }
        documents.append(compact_doc)

    # Sort by bates number
    documents.sort(key=lambda x: x['id'])

    # Calculate statistics
    stats = {
        'total': len(documents),
        'totalPages': manifest['metadata']['total_pages'],
        'byCategory': defaultdict(int),
        'byVolume': defaultdict(int),
    }

    for doc in documents:
        stats['byCategory'][doc['cat']] += 1
        stats['byVolume'][str(doc['vol'])] += 1

    # Convert defaultdicts to regular dicts for JSON
    stats['byCategory'] = dict(stats['byCategory'])
    stats['byVolume'] = dict(stats['byVolume'])

    output = {
        'generated': True,
        'hfBaseUrl': HF_BASE_URL,
        'stats': stats,
        'documents': documents
    }

    # Write manifest
    DOCS_DATA_DIR.mkdir(parents=True, exist_ok=True)
    manifest_path = DOCS_DATA_DIR / "manifest.json"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, separators=(',', ':'))  # Compact JSON

    size_kb = manifest_path.stat().st_size / 1024
    print(f"  Written: {manifest_path} ({size_kb:.1f} KB)")
    print(f"  Documents: {len(documents)}")

    return output


def build_search_corpus():
    """
    Build search corpus from OCR results for Lunr.js indexing.

    Creates a JSON file with document ID and searchable text.
    """
    print("\nBuilding search-corpus.json...")

    ocr_dir = OUTPUT_DIR / "ocr_results"
    corpus = []

    # Find all OCR JSON files recursively
    ocr_files = list(ocr_dir.glob("**/*.json"))
    ocr_files = [f for f in ocr_files if f.stem.startswith('EFTA')]

    print(f"  Found {len(ocr_files)} OCR files")

    for ocr_file in ocr_files:
        try:
            with open(ocr_file, 'r', encoding='utf-8') as f:
                ocr_data = json.load(f)

            bates = ocr_data.get('bates_number', ocr_file.stem)
            text = ocr_data.get('text', '')

            # Truncate text for search (first 2000 chars is usually enough)
            search_text = text[:2000].strip() if text else ''

            if search_text:
                corpus.append({
                    'id': bates,
                    'text': search_text
                })
        except Exception as e:
            print(f"  Warning: Could not process {ocr_file}: {e}")

    # Sort by ID
    corpus.sort(key=lambda x: x['id'])

    # Write corpus
    corpus_path = DOCS_DATA_DIR / "search-corpus.json"
    with open(corpus_path, 'w', encoding='utf-8') as f:
        json.dump(corpus, f, separators=(',', ':'))

    size_mb = corpus_path.stat().st_size / (1024 * 1024)
    print(f"  Written: {corpus_path} ({size_mb:.1f} MB)")
    print(f"  Indexed documents: {len(corpus)}")

    return corpus


def extract_plotly_data():
    """
    Extract Plotly trace data from existing HTML visualizations.

    Parses the embedded JavaScript to extract traces and layout.
    """
    print("\nExtracting Plotly visualization data...")

    import re

    viz_files = [
        ('epstein_doc_distribution.html', 'distribution.json'),
        ('epstein_embedding_clusters.html', 'clusters.json'),
        ('epstein_network_graph.html', 'network.json'),
    ]

    viz_dir = DOCS_DATA_DIR / "viz"
    viz_dir.mkdir(parents=True, exist_ok=True)

    for html_file, json_file in viz_files:
        html_path = PROJECT_ROOT / html_file
        if not html_path.exists():
            print(f"  Skipping {html_file} (not found)")
            continue

        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()

            # Find Plotly.newPlot call - this is a simplified extraction
            # The actual pattern depends on how the HTML was generated
            # For Plotly offline exports, data is usually in a script tag

            # Look for data embedded as JSON
            data_match = re.search(r'Plotly\.newPlot\s*\(\s*[\'"][\w-]+[\'"]\s*,\s*(\[[\s\S]*?\])\s*,\s*(\{[\s\S]*?\})\s*[,\)]', html_content)

            if data_match:
                traces_str = data_match.group(1)
                layout_str = data_match.group(2)

                # Parse and re-serialize to ensure valid JSON
                traces = json.loads(traces_str)
                layout = json.loads(layout_str)

                output = {'traces': traces, 'layout': layout}
                output_path = viz_dir / json_file

                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(output, f, separators=(',', ':'))

                size_kb = output_path.stat().st_size / 1024
                print(f"  Extracted: {json_file} ({size_kb:.1f} KB)")
            else:
                print(f"  Could not extract Plotly data from {html_file}")

        except Exception as e:
            print(f"  Error processing {html_file}: {e}")


def build_entity_index():
    """
    Build entity search index from bipartite graph data.
    Creates entities.json for type-ahead search.
    """
    print("\n=== Building Entity Search Index ===")

    # Load source data
    bipartite_path = VIZ_DIR / "bipartite_graph_data.json"
    players_path = VIZ_DIR / "players" / "summary.json"

    if not bipartite_path.exists():
        print(f"  Error: {bipartite_path} not found")
        return None

    bipartite = load_json(bipartite_path)
    players_summary = load_json(players_path) if players_path.exists() else {}

    entities = []

    for entity in bipartite["entities"]:
        entity_id = entity["id"]
        name = entity["name"]
        entity_type = entity["type"]
        doc_count = entity["doc_count"]

        # Check if this is a key player
        is_key_player = name.lower() in KEY_PLAYERS
        player_info = KEY_PLAYERS.get(name.lower(), {})

        # Build aliases
        aliases = [name.lower()]
        if player_info:
            aliases.append(player_info.get("full_name", "").lower())
            aliases.extend([a.lower() for a in player_info.get("aliases", [])])

        # Get visualization link if exists
        viz_file = None
        if name.lower() in players_summary:
            viz_file = f"data/viz/{players_summary[name.lower()]['file']}"

        entity_record = {
            "id": entity_id,
            "name": player_info.get("full_name", name.title()),
            "short_name": name,
            "type": entity_type,
            "doc_count": doc_count,
            "aliases": list(set(aliases)),
            "is_key_player": is_key_player,
            "viz_file": viz_file
        }

        entities.append(entity_record)

    # Sort by doc_count (descending) with key players first
    entities.sort(key=lambda x: (-x["is_key_player"], -x["doc_count"]))

    # Build index
    index = {
        "entities": entities,
        "total": len(entities),
        "key_players": [e for e in entities if e["is_key_player"]],
        "generated_at": datetime.datetime.now().isoformat()
    }

    # Save
    output_path = DOCS_DATA_DIR / "entities.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2)

    size_kb = output_path.stat().st_size / 1024
    print(f"  Written: {output_path} ({size_kb:.1f} KB)")
    print(f"  Total entities: {len(entities)}")
    print(f"  Key players: {len(index['key_players'])}")

    return entities


def build_entity_profiles(entities):
    """
    Build detailed profile JSON for each entity.
    Creates entity_profiles/<name>.json files.
    """
    print("\n=== Building Entity Profiles ===")

    if not entities:
        print("  No entities provided, skipping profiles")
        return

    # Load source data
    bipartite = load_json(VIZ_DIR / "bipartite_graph_data.json")

    # Load search corpus for snippets
    corpus_path = DOCS_DATA_DIR / "search-corpus.json"
    if corpus_path.exists():
        search_corpus = load_json(corpus_path)
        doc_text = {doc["id"]: doc["text"][:500] for doc in search_corpus}
    else:
        print("  Warning: search-corpus.json not found, no snippets available")
        doc_text = {}

    # Build entity-to-documents mapping
    entity_docs = defaultdict(list)

    for doc in bipartite["documents"]:
        doc_id = doc["id"]
        connected = doc.get("connected_entities", [])
        for ent_id in connected:
            entity_docs[ent_id].append(doc_id)

    # Create profiles directory
    profiles_dir = DOCS_DATA_DIR / "entity_profiles"
    profiles_dir.mkdir(parents=True, exist_ok=True)

    # Build co-occurrence matrix
    print("  Building co-occurrence matrix...")
    cooccurrence = defaultdict(lambda: defaultdict(int))

    for doc in bipartite["documents"]:
        connected = doc.get("connected_entities", [])
        for i, ent1 in enumerate(connected):
            for ent2 in connected[i+1:]:
                cooccurrence[ent1][ent2] += 1
                cooccurrence[ent2][ent1] += 1

    # Generate profiles for each entity
    entity_lookup = {e["id"]: e for e in entities}

    for entity in entities:
        entity_id = entity["id"]
        short_name = entity["short_name"]

        # Get documents
        docs = entity_docs.get(entity_id, [])

        # Get connected entities with co-occurrence counts
        connected = []
        for other_id, count in sorted(cooccurrence[entity_id].items(), key=lambda x: -x[1]):
            if other_id in entity_lookup:
                other = entity_lookup[other_id]
                connected.append({
                    "id": other_id,
                    "name": other["name"],
                    "short_name": other["short_name"],
                    "type": other["type"],
                    "shared_docs": count,
                    "strength": round(count / len(docs), 3) if docs else 0
                })

        # Build document list with snippets
        doc_list = []
        for doc_id in docs[:100]:  # Limit to first 100
            snippet = doc_text.get(doc_id, "")[:200]
            doc_list.append({
                "id": doc_id,
                "snippet": snippet.strip()
            })

        profile = {
            "id": entity_id,
            "name": entity["name"],
            "short_name": short_name,
            "type": entity["type"],
            "doc_count": entity["doc_count"],
            "is_key_player": entity["is_key_player"],
            "viz_file": entity.get("viz_file"),
            "connected_entities": connected[:20],  # Top 20 connections
            "documents": doc_list,
            "total_documents": len(docs)
        }

        # Save profile
        filename = short_name.replace(" ", "_").lower() + ".json"
        profile_path = profiles_dir / filename
        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(profile, f, indent=2)

    print(f"  Generated {len(entities)} entity profiles in {profiles_dir}")


def main():
    print("=" * 60)
    print("Building frontend data files")
    print("=" * 60)

    # Parse arguments
    entities_only = "--entities" in sys.argv

    # Ensure output directory exists
    DOCS_DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not entities_only:
        # Build manifest
        build_manifest()

        # Build search corpus
        build_search_corpus()

        # Extract Plotly data (optional, may not work for all HTML formats)
        try:
            extract_plotly_data()
        except Exception as e:
            print(f"\nNote: Plotly extraction skipped ({e})")

    # Build entity search index and profiles
    entities = build_entity_index()
    if entities:
        build_entity_profiles(entities)

    print("\n" + "=" * 60)
    print("Frontend data build complete!")
    print(f"Output directory: {DOCS_DATA_DIR}")
    print("=" * 60)


if __name__ == '__main__':
    main()
