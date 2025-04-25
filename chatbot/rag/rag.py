from ..services.gemini_client_test import get_gemini_response
from ..utils import search_similar_services
from datetime import datetime, timedelta


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
        from_str = discount_from.strftime("%Y-%m-%d %H:%M") if discount_from else "N/A"
        to_str = discount_to.strftime("%Y-%m-%d %H:%M") if discount_to else "N/A"
        return f"{float(discount)}% (valid from {from_str} to {to_str})"
    return "None"


def rag_response(query):
    services = search_similar_services(query)
    print("services: ", services)

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
        context_lines.append(f"   - Similarity Score: {service['similarity']:.2f}")
        context_lines.append("")

    context = "\n".join(context_lines)
    print("context: ", context)

    # Create prompt for Gemini
    prompt = f"""
    You are an assistant for Prestige Auto Garage. Based on the following information and the user's question, provide a professional response:
    Service information:
    {context}
    
    Question: {query}
    """

    print("PROMPT: ", prompt)
    return get_gemini_response(prompt)
