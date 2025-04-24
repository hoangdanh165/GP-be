from google.genai import types
from .gemini_client import client, model_name
from django.conf import settings
import redis
from uuid import UUID
from chatbot.models.chatbot_history import ChatbotHistory
import json

redis_client = redis.from_url(settings.REDIS_URL)

START_PROMPT = """
You are an AI assistant for "Prestige Auto Garage", a high-quality car service center.
Your role is to help customers by answering questions about our garage, suggesting services, booking appointments, and proactively provide general information about the garage. When answering questions, remember to provide short, succinct answers while remaining polite and professional.

Key rules:
- Politely refuse to answer questions unrelated to the garage, its services, or booking appointments. If such questions arise (e.g., about the weather, news, or unrelated topics), respond with: "I'm sorry, but I can only assist with information related to Prestige Auto Garage and its services."
- Greet customers politely and professionally.
- Suggest appropriate services based on customer needs.
- Help customers schedule service appointments.
- Answer common questions about prices, working hours, and service duration.
- Be friendly, helpful, and patient at all times.
- If you are unsure about any information or cannot answer a question accurately, advise the customer to contact the garage staff directly for further assistance.

Always maintain a supportive and trustworthy tone. Do not mention that you are an AI unless asked directly.
"""

# chat_history_cache = {}

contents = []


def build_contents_from_history(chat_history, new_question):
    if len(contents) == 0:
        # 1. Start Prompt
        contents.append(
            types.Content(
                role="model",
                parts=[types.Part.from_text(text=START_PROMPT)],
            )
        )

        # 2. Add chat history
        for message in chat_history:
            role = "model" if message.get("is_bot", False) else "user"
            contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=message["message"])],
                )
            )
    else:
        # 3. Add new question
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=new_question)],
            )
        )
    print(contents)
    return contents


def ask_gemini(question: str, user_id: UUID) -> str:
    # Get chat history from cache or database
    # if user_id not in chat_history_cache:
    #     chat_history = (
    #         ChatbotHistory.objects.filter(user_id=user_id)
    #         .order_by("create_at")
    #         .values("is_bot", "message")
    #     )
    #     chat_history = list(chat_history)
    #     chat_history_cache[user_id] = chat_history
    # else:
    #     chat_history = chat_history_cache[user_id]

    cache_key = f"chat_history:{user_id}"

    # Try to get chat history from Redis
    cached_history = redis_client.get(cache_key)

    if cached_history:
        chat_history = json.loads(cached_history)
    else:
        chat_history = (
            ChatbotHistory.objects.filter(user_id=user_id)
            .order_by("create_at")
            .values("is_bot", "message")
        )
        chat_history = list(chat_history)
        # Store in Redis with a TTL of 1 hour (3600 seconds)
        redis_client.setex(cache_key, 3600, json.dumps(chat_history))

    contents = build_contents_from_history(chat_history, question)

    # Config
    generate_content_config = types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(
                category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_ONLY_HIGH"
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_ONLY_HIGH"
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_ONLY_HIGH"
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_ONLY_HIGH"
            ),
        ],
        response_mime_type="text/plain",
    )

    full_response = ""

    for chunk in client.models.generate_content_stream(
        model=model_name,
        contents=contents,
        config=generate_content_config,
    ):
        full_response += chunk.text

    return full_response
