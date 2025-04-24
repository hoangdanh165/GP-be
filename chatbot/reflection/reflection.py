from ..services.gemini_client_test import get_gemini_response


def reflect_response(query, initial_response):
    reflection_prompt = f"""
    You are an AI assistant. Evaluate the following response for the query "{query}":
    Response: {initial_response}
    
    Check if the response:
    1. Addresses the query accurately
    2. Provides accurate and helpful information
    3. Uses professional and friendly language
    
    If there are any issues, suggest an improved response. REMEMBER: JUST GIVE THE IMPROVED RESPONSE, DON'T SAY ANYTHING ELSE
    """
    reflection = get_gemini_response(reflection_prompt)
    return reflection if "improve" in reflection.lower() else initial_response
