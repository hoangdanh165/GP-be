import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def get_gemini_response(prompt):
    model = genai.GenerativeModel("gemini-2.0-flash-thinking-exp-01-21")
    response = model.generate_content(prompt)
    return response.text


def get_embedding(text):
    result = genai.embed_content(
        model="models/embedding-001", content=text, task_type="retrieval_document"
    )
    return result["embedding"]

