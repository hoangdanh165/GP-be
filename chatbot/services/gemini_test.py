from .gemini_client_test import generative_model, embedding_model


def get_gemini_response(prompt):

    try:
        response = generative_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error creating response: {str(e)}"


def get_embedding(text):

    try:
        embedding = embedding_model.embed_content(content=text)
        return embedding["embedding"]
    except Exception as e:
        return f"Error creating embedding: {str(e)}"
