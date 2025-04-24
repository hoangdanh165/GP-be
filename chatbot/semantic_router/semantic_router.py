from ..services.gemini_client_test import get_embedding
import numpy as np

ROUTES = {
    "consult_service": ["consult services", "vehicle maintenance", "car repair"],
    "pricing": ["service pricing", "quote", "repair costs"],
    "booking": ["schedule appointment", "book repair slot", "maintenance schedule"],
}


def classify_intent(query):
    query_embedding = get_embedding(query)
    max_similarity = 0
    selected_intent = "unknown"

    for intent, examples in ROUTES.items():
        for example in examples:
            example_embedding = get_embedding(example)
            similarity = np.dot(query_embedding, example_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(example_embedding)
            )
            if similarity > max_similarity:
                max_similarity = similarity
                selected_intent = intent

    return selected_intent if max_similarity > 0.7 else "unknown"
