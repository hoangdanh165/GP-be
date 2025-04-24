from supabase import create_client
import os
from .services.gemini_client_test import get_embedding
from django.db import connection


def get_supabase_client():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    return create_client(url, key)


# def search_similar_services(query, limit=3):
#     supabase = get_supabase_client()
#     query_embedding = get_embedding(query)
#     result = supabase.rpc(
#         "match_service_embeddings",
#         {
#             "query_embedding": query_embedding,
#             "match_threshold": 0.8,
#             "match_count": limit,
#         },
#     ).execute()
#     return result.data


def search_similar_services(query, limit=3):
    query_embedding = get_embedding(query)

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT service_id, (1 - (embedding <=> CAST(%s AS vector))) AS similarity
            FROM service_embeddings
            WHERE (1 - (embedding <=> CAST(%s AS vector))) > %s
            ORDER BY similarity DESC
            LIMIT %s
            """,
            [query_embedding, query_embedding, 0.8, limit],
        )
        rows = cursor.fetchall()

    results = [{"service_id": row[0], "similarity": row[1]} for row in rows]
    return results
