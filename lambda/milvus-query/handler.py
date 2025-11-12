"""
Milvus Query Lambda Handler
Provides secure access to Milvus vector database from within VPC
"""

import json
import os
from typing import Dict, Any, List
from pymilvus import connections, Collection, utility

# Environment variables
MILVUS_HOST = os.environ.get('MILVUS_HOST', 'localhost')
MILVUS_PORT = os.environ.get('MILVUS_PORT', '19530')

# Global connection (reused across invocations)
_connection_alias = 'default'
_is_connected = False


def ensure_connection():
    """Establish connection to Milvus if not already connected"""
    global _is_connected

    if not _is_connected:
        try:
            connections.connect(
                alias=_connection_alias,
                host=MILVUS_HOST,
                port=MILVUS_PORT
            )
            _is_connected = True
            print(f"Connected to Milvus at {MILVUS_HOST}:{MILVUS_PORT}")
        except Exception as e:
            print(f"Failed to connect to Milvus: {str(e)}")
            raise


def query(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for querying Milvus

    Expected event format:
    {
        "action": "search" | "list_collections" | "get_stats" | "insert",
        "collection_name": "my_collection",
        "query_vector": [0.1, 0.2, ...],  // for search
        "top_k": 10,                       // for search
        "data": [...]                      // for insert
    }
    """
    try:
        ensure_connection()

        action = event.get('action', 'list_collections')

        if action == 'list_collections':
            return handle_list_collections()

        elif action == 'get_stats':
            collection_name = event.get('collection_name')
            if not collection_name:
                return error_response('collection_name required for get_stats')
            return handle_get_stats(collection_name)

        elif action == 'search':
            collection_name = event.get('collection_name')
            query_vector = event.get('query_vector')
            top_k = event.get('top_k', 10)

            if not collection_name or not query_vector:
                return error_response('collection_name and query_vector required for search')

            return handle_search(collection_name, query_vector, top_k)

        elif action == 'insert':
            collection_name = event.get('collection_name')
            data = event.get('data')

            if not collection_name or not data:
                return error_response('collection_name and data required for insert')

            return handle_insert(collection_name, data)

        else:
            return error_response(f'Unknown action: {action}')

    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return error_response(str(e))


def handle_list_collections() -> Dict[str, Any]:
    """List all collections in Milvus"""
    try:
        collections = utility.list_collections()
        return {
            'statusCode': 200,
            'body': json.dumps({
                'collections': collections,
                'count': len(collections)
            })
        }
    except Exception as e:
        return error_response(f'Failed to list collections: {str(e)}')


def handle_get_stats(collection_name: str) -> Dict[str, Any]:
    """Get statistics for a collection"""
    try:
        if not utility.has_collection(collection_name):
            return error_response(f'Collection {collection_name} does not exist')

        collection = Collection(collection_name)
        collection.load()

        stats = {
            'name': collection_name,
            'num_entities': collection.num_entities,
            'schema': str(collection.schema),
        }

        return {
            'statusCode': 200,
            'body': json.dumps(stats)
        }
    except Exception as e:
        return error_response(f'Failed to get stats: {str(e)}')


def handle_search(
    collection_name: str,
    query_vector: List[float],
    top_k: int
) -> Dict[str, Any]:
    """Perform vector similarity search"""
    try:
        if not utility.has_collection(collection_name):
            return error_response(f'Collection {collection_name} does not exist')

        collection = Collection(collection_name)
        collection.load()

        # Perform search
        search_params = {
            "metric_type": "L2",
            "params": {"nprobe": 10}
        }

        results = collection.search(
            data=[query_vector],
            anns_field="embedding",  # Adjust based on your schema
            param=search_params,
            limit=top_k,
            output_fields=["*"]
        )

        # Format results
        formatted_results = []
        for hits in results:
            for hit in hits:
                formatted_results.append({
                    'id': hit.id,
                    'distance': hit.distance,
                    'entity': hit.entity.to_dict()
                })

        return {
            'statusCode': 200,
            'body': json.dumps({
                'results': formatted_results,
                'count': len(formatted_results)
            })
        }
    except Exception as e:
        return error_response(f'Search failed: {str(e)}')


def handle_insert(collection_name: str, data: List[Dict]) -> Dict[str, Any]:
    """Insert data into collection"""
    try:
        if not utility.has_collection(collection_name):
            return error_response(f'Collection {collection_name} does not exist')

        collection = Collection(collection_name)

        # Insert data
        insert_result = collection.insert(data)
        collection.flush()

        return {
            'statusCode': 200,
            'body': json.dumps({
                'inserted_count': insert_result.insert_count,
                'primary_keys': insert_result.primary_keys[:10]  # First 10 keys
            })
        }
    except Exception as e:
        return error_response(f'Insert failed: {str(e)}')


def error_response(message: str) -> Dict[str, Any]:
    """Return error response"""
    return {
        'statusCode': 400,
        'body': json.dumps({
            'error': message
        })
    }
