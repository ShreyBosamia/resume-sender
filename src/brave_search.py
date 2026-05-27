import os
import time
import requests
from dotenv import load_dotenv
from typing import Any
from result_classifier import classify_search_result

load_dotenv()


BRAVE_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"

def brave_search(query: str, count: int = 5) -> list[dict[str, Any]]:
    api_key = os.getenv("BRAVE_SEARCH_API_KEY")

    if not api_key:
        raise ValueError("Missing BRAVE_SEARCH_API_KEY in .env")

    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": api_key
    }

    params = {
        "q": query,
        "count": count
    }

    response = requests.get(
        BRAVE_SEARCH_URL,
        headers=headers,
        params=params,
        timeout=15
    )

    if response.status_code == 429:
        print("  Rate limited by Brave Search. Skipping this query for now.")
        return []

    response.raise_for_status()

    data = response.json()
    results = data.get("web", {}).get("results", [])

    return results


def brave_results_to_jobs(
    results: list[dict[str, Any]],
    query: str
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    candidate_jobs = []
    source_pages = []

    for result in results:
        title = result.get("title", "")
        url = result.get("url", "")
        description = result.get("description", "")

        if not title or not url:
            continue

        result_type = classify_search_result(result)

        if result_type in ["job_directory", "company_careers_page"]:
            source_pages.append({
                "title": title,
                "url": url,
                "description": description,
                "source": "brave_search",
                "source_type": result_type,
                "query": query
            })
            continue

        if result_type == "educational_page":
            continue

        job = {
            "title": title,
            "organization": "Unknown",
            "location": None,
            "remote_type": None,
            "employment_type": None,
            "experience_level": None,
            "url": url,
            "source": "brave_search",
            "description": description
        }

        candidate_jobs.append(job)

    return candidate_jobs, source_pages
