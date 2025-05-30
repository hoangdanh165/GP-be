import redis
import json
import logging
import time
from django.conf import settings
from ..models.chatbot_history import ChatbotHistory
from ..services.gemini_client_test import (
    get_gemini_response,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


def format_history(history):
    formatted_texts = []

    for entry in history:
        role = "model" if entry.get("is_bot", False) else "user"
        message = entry.get("message", "")
        formatted_texts.append(f"{role}: {message}\n")
    return "".join(formatted_texts)


def reformulate_query(query, user_id=None, last_items_considered=100, cache_ttl=3600):
    start_time = time.time()
    try:
        cache_key = f"chat_history:{user_id}"

        cached_items = redis_client.lrange(cache_key, 0, -1)
        if cached_items:
            try:
                history = [json.loads(item) for item in cached_items]
                if not all(
                    isinstance(entry, dict) and "is_bot" in entry and "message" in entry
                    for entry in history
                ):
                    logger.warning(
                        f"Invalid cache data for key {cache_key}, fetching from database"
                    )
                    raise ValueError("Invalid cache data")

                new_entry = {"is_bot": False, "message": query}
                redis_client.rpush(cache_key, json.dumps(new_entry))
                redis_client.expire(cache_key, cache_ttl)

                logger.info(f"Appended new query to cache with key {cache_key}")
                logger.info(
                    f"Retrieved {len(history)} history items from Redis cache with key {cache_key}"
                )
            except json.JSONDecodeError:
                logger.error(f"Failed to decode cache data for key {cache_key}")
                history = None
        else:
            logger.info("No cache found, fetching history from database")
            history = list(
                ChatbotHistory.objects.filter(user=user_id)
                .order_by("create_at")
                .values("is_bot", "message")
            )

            with redis_client.pipeline() as pipe:
                for entry in history:
                    pipe.rpush(cache_key, json.dumps(entry))
                pipe.expire(cache_key, cache_ttl)
                pipe.execute()
            logger.info(
                f"Initialized cache with {len(history)} items for key {cache_key} with TTL {cache_ttl} seconds"
            )

        redis_client.ltrim(cache_key, -last_items_considered, -1)
        logger.info(
            f"Trimmed cache to last {last_items_considered} items for key {cache_key}"
        )

        cached_items = redis_client.lrange(cache_key, 0, -1)
        history = [json.loads(item) for item in cached_items]

        if len(history) == 1 and history[0]["message"] == query:
            logger.info("No chat history available, returning original query")
            elapsed_time = time.time() - start_time
            logger.info(f"reformulate_query execution time: {elapsed_time:.2f} seconds")
            return query

        history_string = format_history(history)

        higher_level_summaries_prompt = f"""
            You are given a chat history and the user's latest question. The user may have expressed their intent across multiple turns in the conversation. Your task is to rewrite the user's overall intent as a **standalone, clear, and complete question in English** that includes all relevant details mentioned in the chat history.

            Important instructions:
            - DO NOT answer the question.
            - Only output the rewritten question.
            - If the latest question is self-contained and doesn't rely on history, return it as-is.
            - If there are multiple relevant requests across the history (e.g., asking about multiple services), COMBINE them into one clear question.
            - The reformulated question should make sense even without the chat history.

            Chat history:
            {history_string}

            Latest question: {query}
            """

        logger.info(f"Prompt for Gemini: {higher_level_summaries_prompt}")
        reformulated_query = get_gemini_response(higher_level_summaries_prompt)

        if not reformulated_query:
            logger.warning("LLM returned empty response, returning original query")
            elapsed_time = time.time() - start_time
            logger.info(f"reformulate_query execution time: {elapsed_time:.2f} seconds")
            return query

        logger.info(f"Reformulated query: {reformulated_query}")
        elapsed_time = time.time() - start_time
        logger.info(f"reformulate_query execution time: {elapsed_time:.2f} seconds")
        return reformulated_query.strip()

    except redis.RedisError as e:
        logger.error(f"Redis error: {str(e)}")

        try:
            history = list(
                ChatbotHistory.objects.filter(user_id=user_id)
                .order_by("create_at")
                .values("is_bot", "message")
            )

            if len(history) > last_items_considered:
                history = history[-last_items_considered:]

            if len(history) == 1 and history[0]["content"] == query:
                logger.info("No chat history available, returning original query")
                elapsed_time = time.time() - start_time
                logger.info(
                    f"reformulate_query execution time: {elapsed_time:.2f} seconds"
                )
                return query

            history_string = format_history(history)

            higher_level_summaries_prompt = f"""
            Given a chat history and the latest user question which might reference context in the chat history, formulate a standalone question in English which can be understood without the chat history. Do NOT answer the question, just reformulate it if needed and otherwise return it as is.
            Chat history:
            {history_string}
            Latest question: {query}
            """
            logger.info(f"Prompt for Gemini: {higher_level_summaries_prompt}")

            reformulated_query = get_gemini_response(higher_level_summaries_prompt)

            if not reformulated_query:
                logger.warning("LLM returned empty response, returning original query")
                elapsed_time = time.time() - start_time
                logger.info(
                    f"reformulate_query execution time: {elapsed_time:.2f} seconds"
                )
                return query

            elapsed_time = time.time() - start_time
            logger.info(f"reformulate_query execution time: {elapsed_time:.2f} seconds")
            return reformulated_query.strip()

        except Exception as e:
            logger.error(f"Error reformulating query: {str(e)}")
            elapsed_time = time.time() - start_time
            logger.info(f"reformulate_query execution time: {elapsed_time:.2f} seconds")
            return query

    except Exception as e:
        logger.error(f"Error reformulating query: {str(e)}")
        elapsed_time = time.time() - start_time
        logger.info(f"reformulate_query execution time: {elapsed_time:.2f} seconds")
        return query
