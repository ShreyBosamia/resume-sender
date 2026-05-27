from typing import Any


def generate_search_queries(preferences: dict[str, Any]) -> list[str]:
    target_roles = preferences.get("target_roles", [])
    location = preferences.get("location", {})
    preferred_keywords = preferences.get("preferred_keywords", [])

    city = location.get("city")
    state = location.get("state")

    location_text = ""
    if city and state:
        location_text = f"{city} {state}"
    elif state:
        location_text = state

    queries = []

    for role in target_roles:
        if location_text:
            queries.append(f'{role} jobs {location_text}')
        else:
            queries.append(f'{role} jobs')

    for keyword in preferred_keywords:
        if location_text:
            queries.append(f'{keyword} jobs {location_text}')
        else:
            queries.append(f'{keyword} jobs')

    # Remove duplicates while preserving order
    unique_queries = []
    seen = set()

    for query in queries:
        normalized = query.lower().strip()

        if normalized not in seen:
            unique_queries.append(query)
            seen.add(normalized)

    return unique_queries
