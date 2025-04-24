import redis
import json
from django.conf import settings

redis_client = redis.from_url(settings.REDIS_URL)


def get_cached_response(query):
    cached = redis_client.get(query)
    return json.loads(cached) if cached else None


def cache_response(query, response):
    redis_client.setex(query, 3600, json.dumps(response))
