import re
from typing import Any


def normalize_text(value: str | None) -> str:
    if value is None:
        return ""

    return str(value).lower().strip()


def safe_text(value: Any) -> str:
    if value is None:
        return ""

    return str(value)


def keyword_matches(keyword: str, text: str) -> bool:
    keyword = keyword.lower().strip()

    if not keyword:
        return False

    pattern = rf"\b{re.escape(keyword)}\b"
    return re.search(pattern, text, re.IGNORECASE) is not None


def job_text(job: dict[str, Any]) -> str:
    parts = [
        safe_text(job.get("title")),
        safe_text(job.get("organization")),
        safe_text(job.get("location")),
        safe_text(job.get("remote_type")),
        safe_text(job.get("employment_type")),
        safe_text(job.get("experience_level")),
        safe_text(job.get("description")),
        safe_text(job.get("salary_text"))
    ]

    requirements = job.get("requirements", [])
    preferred_qualifications = job.get("preferred_qualifications", [])

    parts.extend(safe_text(item) for item in requirements)
    parts.extend(safe_text(item) for item in preferred_qualifications)

    return normalize_text(" ".join(parts))


def get_title_text(job: dict[str, Any]) -> str:
    return normalize_text(job.get("title"))


def get_description_text(job: dict[str, Any]) -> str:
    return normalize_text(job.get("description"))


def score_job(job: dict[str, Any], preferences: dict[str, Any]) -> dict[str, Any]:
    title_text = get_title_text(job)
    description_text = get_description_text(job)
    full_text = job_text(job)

    preferred_keywords = preferences.get("preferred_keywords", [])
    hard_excluded_keywords = preferences.get("hard_excluded_keywords", [])
    soft_excluded_keywords = preferences.get("soft_excluded_keywords", [])
    target_roles = preferences.get("target_roles", [])
    remote_preferences = preferences.get("remote_preference", [])

    score = 25
    matched_keywords = []
    missing_keywords = []
    concerns = []

    hard_exclusion_found = False

    # Hard exclusions: reject if these appear.
    for keyword in hard_excluded_keywords:
        if keyword_matches(keyword, title_text):
            score -= 100
            hard_exclusion_found = True
            concerns.append(f"Hard excluded title keyword: {keyword}")
        elif keyword_matches(keyword, description_text):
            score -= 25
            concerns.append(f"Possible clinical mismatch keyword: {keyword}")
    # Soft exclusions: penalize, but do not automatically reject.
    for keyword in soft_excluded_keywords:
        if keyword_matches(keyword, full_text):
            score -= 15
            concerns.append(f"Contains soft excluded keyword: {keyword}")

    seniority_penalty_keywords = preferences.get("seniority_penalty_keywords", [])

    for keyword in seniority_penalty_keywords:
        if keyword_matches(keyword, title_text):
            score -= 25
            concerns.append(f"Seniority/title penalty: {keyword}")
        elif keyword_matches(keyword, full_text):
            score -= 10
            concerns.append(f"Seniority/experience penalty: {keyword}")

    # Target roles matter most when they appear in the title.
    for role in target_roles:
        if keyword_matches(role, title_text):
            score += 30
            matched_keywords.append(role)
        elif keyword_matches(role, description_text):
            score += 12
            matched_keywords.append(role)

    # Preferred keywords also matter more in title than description.
    for keyword in preferred_keywords:
        if keyword_matches(keyword, title_text):
            score += 15
            matched_keywords.append(keyword)
        elif keyword_matches(keyword, description_text):
            score += 8
            matched_keywords.append(keyword)
        else:
            missing_keywords.append(keyword)

    # Remote preference gives a small boost.
    remote_type = normalize_text(job.get("remote_type"))

    if remote_type and remote_type in remote_preferences:
        score += 5

    # Healthcare/public-health organizations get a small boost.
    organization_text = normalize_text(job.get("organization"))
    organization_boost_terms = [
        "health",
        "clinic",
        "hospital",
        "county",
        "public health",
        "community health",
        "oregon health",
        "ohsu"
    ]

    if any(term in organization_text for term in organization_boost_terms):
        score += 8

    # Clamp score between 0 and 100.
    score = max(0, min(100, score))

    if hard_exclusion_found:
        job_status = "rejected"
        fit_reason = "Rejected because the title matched a hard excluded keyword."
    elif score >= 75:
        job_status = "recommended"
        fit_reason = "Strong match based on title, preferred keywords, and role fit."
    elif score >= 50:
        job_status = "maybe"
        fit_reason = "Possible match, but needs review."
    else:
        job_status = "rejected"
        fit_reason = "Weak match based on current preferences."

    return {
        **job,
        "fit_score": score,
        "fit_reason": fit_reason,
        "fit_concerns": concerns,
        "matched_keywords": sorted(set(matched_keywords)),
        "missing_keywords": sorted(set(missing_keywords)),
        "job_status": job_status
    }
