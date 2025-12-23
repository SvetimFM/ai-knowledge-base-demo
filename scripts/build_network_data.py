#!/usr/bin/env python3
"""Build network graph data from entity profiles for vis.js visualization."""

import json
import os
from pathlib import Path

DOCS_DIR = Path(__file__).parent.parent / "docs"
PROFILES_DIR = DOCS_DIR / "data" / "entity_profiles"
ENTITIES_FILE = DOCS_DIR / "data" / "entities.json"
OUTPUT_FILE = DOCS_DIR / "data" / "network_data.json"

def main():
    # Load entities
    with open(ENTITIES_FILE) as f:
        entities_data = json.load(f)

    entities = {e["short_name"]: e for e in entities_data["entities"]}
    key_players = [e["short_name"] for e in entities_data["key_players"]]

    print(f"Loaded {len(entities)} entities, {len(key_players)} key players")

    # Load all profiles and build edges
    edges = []
    edge_set = set()  # Prevent duplicates

    for profile_file in PROFILES_DIR.glob("*.json"):
        try:
            with open(profile_file) as f:
                profile = json.load(f)
        except Exception as e:
            print(f"Error loading {profile_file}: {e}")
            continue

        source = profile.get("short_name")
        if not source or source not in entities:
            continue

        connections = profile.get("connected_entities", [])
        for conn in connections:
            target = conn.get("short_name")
            if not target or target not in entities:
                continue

            # Create canonical edge key (smaller name first)
            edge_key = tuple(sorted([source, target]))
            if edge_key in edge_set:
                continue
            edge_set.add(edge_key)

            strength = conn.get("strength", 0)
            shared_docs = conn.get("shared_docs", 0)

            # Only include meaningful connections
            if strength < 0.05 or shared_docs < 2:
                continue

            edges.append({
                "from": edge_key[0],
                "to": edge_key[1],
                "strength": round(strength, 3),
                "shared_docs": shared_docs,
                "label": f"{shared_docs} docs"
            })

    print(f"Built {len(edges)} edges")

    # Build nodes with additional info
    nodes = []
    for short_name, entity in entities.items():
        node = {
            "id": short_name,
            "label": entity["name"],
            "type": entity["type"],
            "is_key_player": entity.get("is_key_player", False),
            "doc_count": entity["doc_count"],
            "viz_file": entity.get("viz_file")
        }
        nodes.append(node)

    # Output
    output = {
        "nodes": nodes,
        "edges": sorted(edges, key=lambda e: -e["strength"]),
        "generated_at": __import__("datetime").datetime.now().isoformat()
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Wrote network data to {OUTPUT_FILE}")
    print(f"  {len(nodes)} nodes, {len(edges)} edges")

    # Summary stats
    key_player_edges = [e for e in edges
                       if e["from"] in key_players or e["to"] in key_players]
    print(f"  {len(key_player_edges)} edges involve key players")

    # Top 10 strongest connections
    print("\nTop 10 strongest connections:")
    for i, edge in enumerate(edges[:10]):
        print(f"  {i+1}. {edge['from']} <-> {edge['to']}: {edge['strength']:.1%} ({edge['shared_docs']} docs)")

if __name__ == "__main__":
    main()
