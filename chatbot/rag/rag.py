from ..services.gemini_client_test import get_gemini_response
from ..utils import search_similar_services, get_all_services
from datetime import datetime, timedelta
from django.core.exceptions import ObjectDoesNotExist
from service.models.service import Service
import pytz
import time


def format_duration(duration: timedelta) -> str:
    total_seconds = int(duration.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    if hours > 0 and minutes > 0:
        return f"{hours} hour{'s' if hours > 1 else ''} {minutes} minute{'s' if minutes > 1 else ''}"
    elif hours > 0:
        return f"{hours} hour{'s' if hours > 1 else ''}"
    elif minutes > 0:
        return f"{minutes} minute{'s' if minutes > 1 else ''}"
    else:
        return "0 minutes"


def format_discount(
    discount: float, discount_from: datetime, discount_to: datetime
) -> str:
    if discount and float(discount) > 0:
        vn_tz = pytz.timezone("Asia/Ho_Chi_Minh")

        from_vn = discount_from.astimezone(vn_tz) if discount_from else None
        to_vn = discount_to.astimezone(vn_tz) if discount_to else None

        from_str = from_vn.strftime("%Y-%m-%d %H:%M") if from_vn else "N/A"
        to_str = to_vn.strftime("%Y-%m-%d %H:%M") if to_vn else "N/A"

        return f"{float(discount)}% (valid from {from_str} to {to_str})"
    return "None"


def rag_response(query, all_services=False):
    start_time = time.time()

    if all_services:
        services = get_all_services()
    else:
        services = search_similar_services(query)
        print("services: ", services)

    if not services:
        print(f"No services available for query: {query}")
        return "Sorry, we couldn't find any services matching your request. Please try a different query or contact us for more information."

    # Create context for gemini from services
    context_lines = ["Available Services:"]

    for idx, service in enumerate(services, 1):
        context_lines.append(f"{idx}. {service['name']}")
        context_lines.append(f"   - Description: {service['description']}")
        context_lines.append(f"   - Price: ${service['price']:.2f}")
        context_lines.append(
            f"   - Estimated Duration: {format_duration(service['estimated_duration'])}"
        )
        context_lines.append(
            f"   - Discount: {format_discount(service['discount'], service['discount_from'], service['discount_to'])}"
        )
        context_lines.append(f"   - Category ID: {service['category_id']}")
        if "similarity" in service:
            context_lines.append(f"   - Similarity Score: {service['similarity']:.2f}")
        context_lines.append("")

    context = "\n".join(context_lines)
    print("context: ", context)

    # Create enhanced prompt for Gemini
    prompt = f"""
        You are a friendly and professional assistant for Prestige Auto Garage. Your goal is to provide a conversational and helpful response to the user's question, using the provided service information as context. Follow these guidelines:
        - Anser the user's question in their language.
        - Answer the user's question directly and concisely, focusing on their intent.
        - Use a natural, engaging tone as if you were speaking to a customer in person.
        - Incorporate relevant details from the service information (e.g., price, duration, description) in a seamless way, without listing them like a database entry.
        - If the question is broad or vague, provide a brief overview of the most relevant service and its benefits.
        - Avoid repeating the service description verbatim; instead, paraphrase or summarize it to fit the response.
        - If applicable, suggest related services or add value by explaining why the service is beneficial.
        - If service information is too long, summarize the key points and provide a concise answer.
        
        Service information:
        {context}

        Question: {query}
    """

    elapsed_time = time.time() - start_time
    print(f"rag_response execution time: {elapsed_time:.2f} seconds")

    return get_gemini_response(prompt)
