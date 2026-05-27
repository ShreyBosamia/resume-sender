from typing import Any


JOB_BOARD_DOMAINS = [
    "indeed.com",
    "linkedin.com",
    "glassdoor.com",
    "ziprecruiter.com",
    "monster.com"
]


DIRECTORY_PHRASES = [
    "jobs in",
    "jobs, employment",
    "job openings",
    "hiring now",
    "now hiring",
    "employment in",
    "jobs near",
    "new)",
    "+",
    "job search"
]


EDUCATIONAL_PHRASES = [
    "what can i do with",
    "degree in",
    "career guide",
    "salary guide",
    "career paths",
    "major in"
]


def classify_search_result(result: dict[str, Any]) -> str:
    title = str(result.get("title") or "").lower()
    description = str(result.get("description") or "").lower()
    url = str(result.get("url") or "").lower()

    combined_text = f"{title} {description} {url}"

    if any(phrase in combined_text for phrase in EDUCATIONAL_PHRASES):
        return "educational_page"

    is_job_board = any(domain in url for domain in JOB_BOARD_DOMAINS)
    looks_like_directory = any(phrase in combined_text for phrase in DIRECTORY_PHRASES)

    if is_job_board and looks_like_directory:
        return "job_directory"

    if "careers" in url or "human-resources" in url or "/jobs/" in url:
        return "company_careers_page"

    return "unknown"
