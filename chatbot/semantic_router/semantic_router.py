import numpy as np
import json
import logging
from django.core.cache import cache
from ..services.gemini_client_test import get_embedding
from .route import Route
from .samples import service_samples, all_service_samples, chitchat_samples
from sklearn.metrics.pairwise import cosine_similarity
import time
from django_redis import get_redis_connection


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Route name
SERVICE_ROUTE_NAME = "services"
ALL_SERVICE_ROUTE_NAME = "all_services"
CHITCHAT_ROUTE_NAME = "chitchat"

# Route
service_route = Route(name=SERVICE_ROUTE_NAME, samples=service_samples)
all_service_route = Route(name=ALL_SERVICE_ROUTE_NAME, samples=all_service_samples)
chitchat_route = Route(name=CHITCHAT_ROUTE_NAME, samples=chitchat_samples)

ROUTES = {
    SERVICE_ROUTE_NAME: service_samples,
    ALL_SERVICE_ROUTE_NAME: all_service_samples,
    CHITCHAT_ROUTE_NAME: chitchat_samples,
}


class EmbeddingCache:
    def __init__(self, cache_prefix="embedding:", timeout=None):
        self.cache = cache
        self.cache_prefix = cache_prefix
        self.timeout = timeout

    def get(self, text):
        cache_key = f"{self.cache_prefix}{text}"
        embedding_data = self.cache.get(cache_key)
        if embedding_data:
            try:
                return np.array(json.loads(embedding_data))
            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode embedding for {text}: {str(e)}")
                return None

        try:
            embedding = get_embedding(text)
            if embedding is None or not isinstance(embedding, list) or not embedding:
                logger.error(f"Failed to get embedding for text: {text}")
                return None
            embedding = np.array(embedding)
            if not embedding.size or embedding.ndim != 1:
                logger.error(f"Invalid embedding for text: {text}")
                return None

            self.cache.set(
                cache_key, json.dumps(embedding.tolist()), timeout=self.timeout
            )
            return embedding
        except Exception as e:
            logger.error(f"Error getting embedding for {text}: {str(e)}")
            return None


def delete_all_redis_cache():
    cache.clear()
    redis_conn = get_redis_connection("default")
    redis_conn.flushall()


def view_all_cache():
    redis_conn = get_redis_connection("default")
    keys = redis_conn.keys("*")

    if not keys:
        print("No cache found in Redis.")
        return

    print(f"Found {len(keys)} cache key in Redis:\n")

    for key in keys:
        key_str = key.decode("utf-8")

        try:
            value = redis_conn.get(key).decode("utf-8")

            try:
                json_val = json.loads(value)
                pretty_val = json.dumps(json_val, indent=2, ensure_ascii=False)
            except json.JSONDecodeError:
                pretty_val = value

            print(f"{key_str}:\n{pretty_val}\n")
        except Exception as e:
            print(f"Error reading key {key_str}: {e}")


def precompute_embeddings(routes):
    embedding_cache = EmbeddingCache()
    unique_samples = set()
    for intent, samples in routes.items():
        unique_samples.update(samples)

    logger.info(f"Precomputing embeddings for {len(unique_samples)} unique samples...")
    start_time = time.time()

    for sample in unique_samples:
        embedding_cache.get(sample)

    elapsed_time = time.time() - start_time
    logger.info(f"Precomputed embeddings in {elapsed_time:.2f} seconds.")


def classify_intent(query: str, similarity_threshold: float = 0.7) -> str:
    start_time = time.time()
    embedding_cache = EmbeddingCache()

    query_embedding = embedding_cache.get(query)
    if query_embedding is None:
        logger.warning(f"Could not get embedding for query: {query}")
        elapsed_time = time.time() - start_time
        logger.info(f"classify_intent execution time: {elapsed_time:.2f} seconds")
        return "unknown"

    max_similarity = -1.0
    selected_intent = "unknown"

    for intent, samples in ROUTES.items():
        for sample in samples:
            sample_embedding = embedding_cache.get(sample)
            if sample_embedding is None:
                continue

            similarity = cosine_similarity(
                query_embedding.reshape(1, -1), sample_embedding.reshape(1, -1)
            )[0][0]

            if similarity > max_similarity:
                max_similarity = similarity
                selected_intent = intent

    if max_similarity >= similarity_threshold:
        logger.info(
            f"Classified intent: {selected_intent} (similarity: {max_similarity:.4f})"
        )
    else:
        logger.info(
            f"No intent matched for query: {query} (max similarity: {max_similarity:.4f})"
        )

    elapsed_time = time.time() - start_time
    logger.info(f"classify_intent execution time: {elapsed_time:.2f} seconds")
    return selected_intent


# view_all_cache()
# delete_all_redis_cache()
# precompute_embeddings(ROUTES)
