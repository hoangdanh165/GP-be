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
            SELECT s.id, s.name, s.description, s.price, s.estimated_duration, s.discount, s.discount_from, s.discount_to, s.category_id,
                   (1 - (s.embedding <=> CAST(%s AS vector))) AS similarity
            FROM service s
            WHERE (1 - (s.embedding <=> CAST(%s AS vector))) > %s
            ORDER BY similarity DESC
            LIMIT %s
            """,
            [query_embedding, query_embedding, 0.8, limit],
        )
        rows = cursor.fetchall()

    results = [
        {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "price": float(row[3]),
            "estimated_duration": row[4],
            "discount": row[5],
            "discount_from": row[6],
            "discount_to": row[7],
            "category_id": row[8],
            "similarity": float(row[9]),
        }
        for row in rows
    ]

    return results
