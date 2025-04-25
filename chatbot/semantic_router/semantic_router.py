from ..services.gemini_client_test import get_embedding
import numpy as np
from .route import Route
from .samples import service_samples
from sklearn.metrics.pairwise import cosine_similarity
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Route name
SERVICE_ROUTE_NAME = "services"

# Route
service_route = Route(name=SERVICE_ROUTE_NAME, samples=service_samples)

ROUTES = {
    SERVICE_ROUTE_NAME: service_samples
    # "pricing_inquiry": pricing_samples,
    # "booking_inquiry": booking_samples
}


class EmbeddingCache:
    def __init__(self):
        self.cache = {}

    def get(self, text):
        if text not in self.cache:
            try:
                embedding = get_embedding(text)

                if embedding is None:
                    logger.error(f"Failed to get embedding for text: {text}")
                    return None
                embedding = np.array(embedding)
                if not embedding.size or embedding.ndim != 1:
                    logger.error(f"Invalid embedding for text: {text}")
                    return None
                self.cache[text] = embedding
            except Exception as e:
                logger.error(f"Error getting embedding for {text}: {str(e)}")
                return None
        return self.cache[text]


embedding_cache = EmbeddingCache()


def classify_intent(query: str, similarity_threshold: float = 0.7) -> str:
    query_embedding = embedding_cache.get(query)

    if query_embedding is None:
        logger.warning(f"Could not get embedding for query: {query}")
        return "unknown"

    max_similarity = -1.0
    selected_intent = "unknown"

    for intent, examples in ROUTES.items():
        for example in examples:

            example_embedding = embedding_cache.get(example)

            if example_embedding is None:
                continue

            similarity = cosine_similarity(
                query_embedding.reshape(1, -1), example_embedding.reshape(1, -1)
            )[0][0]

            if similarity > max_similarity:
                max_similarity = similarity
                selected_intent = intent

    if max_similarity >= similarity_threshold:
        logger.info(
            f"Classified intent: {selected_intent} (similarity: {max_similarity:.4f})"
        )
        return selected_intent
    else:
        logger.info(
            f"No intent matched for query: {query} (max similarity: {max_similarity:.4f})"
        )
        return "unknown"
