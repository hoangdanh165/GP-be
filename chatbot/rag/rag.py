from ..services.gemini_client_test import get_gemini_response
from ..utils import search_similar_services


def rag_response(query):
    services = search_similar_services(query)
    context = "\n".join([f"{s['name']}: {s['description']}" for s in services])

    # Create prompt for Gemini
    prompt = f"""
    You are an assistant for Prestige Auto Garage. Based on the following information and the user's question, provide a professional response:
    Service information:
    {context}
    
    Question: {query}
    """
    return get_gemini_response(prompt)
