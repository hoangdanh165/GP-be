import os
from .services.gemini_client_test import get_embedding
from django.db import connection
from service.models.service import Service
from django.core.exceptions import ObjectDoesNotExist


def search_similar_services(query, limit=3):
    query_embedding = get_embedding(query)

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT 
                s.id, 
                s.name, 
                s.description, 
                s.price, 
                s.estimated_duration, 
                s.discount, 
                s.discount_from, 
                s.discount_to, 
                s.category_id,
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

    print("results: ", results)
    return results


def get_all_services():
    try:
        services = Service.objects.all().values(
            "name",
            "description",
            "price",
            "estimated_duration",
            "discount",
            "discount_from",
            "discount_to",
            "category_id",
        )
        services = [
            {
                "name": service["name"],
                "description": service["description"],
                "price": float(service["price"]),
                "estimated_duration": service["estimated_duration"],
                "discount": float(service["discount"]) if service["discount"] else 0.0,
                "discount_from": service["discount_from"],
                "discount_to": service["discount_to"],
                "category_id": service["category_id"],
            }
            for service in services
        ]
        print(f"Retrieved {len(services)} services from Service.objects.all()")
        return services
    except ObjectDoesNotExist:
        print("No services found in database")
        return []
