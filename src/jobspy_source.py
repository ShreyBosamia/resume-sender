from typing import Any

import pandas as pd
from jobspy import scrape_jobs


def is_missing(value: Any) -> bool:
    """
    Returns True for None, NaN, or empty strings.
    """
    if value is None:
        return True

    if pd.isna(value):
        return True

    if isinstance(value, str) and value.strip() == "":
        return True

    return False


def safe_string(value: Any) -> str | None:
    if is_missing(value):
        return None

    return str(value).strip()


def safe_int(value: Any) -> int | None:
    if is_missing(value):
        return None

    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None


def build_location(city: Any, state: Any) -> str | None:
    location_parts = []

    city_text = safe_string(city)
    state_text = safe_string(state)

    if city_text:
        location_parts.append(city_text)

    if state_text:
        location_parts.append(state_text)

    if not location_parts:
        return None

    return ", ".join(location_parts)


def jobspy_search(
    search_term: str,
    location: str,
    results_wanted: int = 10
) -> list[dict[str, Any]]:
    """
    Searches job boards through JobSpy and returns normalized raw job dicts.
    """

    jobs_df = scrape_jobs(
        site_name=["indeed", "linkedin", "google"],
        search_term=search_term,
        location=location,
        results_wanted=results_wanted,
        country_indeed="USA",
        hours_old=168
    )

    raw_jobs = []

    for _, row in jobs_df.iterrows():
        title = safe_string(row.get("title"))
        company = safe_string(row.get("company"))
        city = row.get("city")
        state = row.get("state")
        job_url = safe_string(row.get("job_url"))
        description = safe_string(row.get("description"))
        site = safe_string(row.get("site"))
        job_location = build_location(city, state)
        remote_type = detect_remote_type(title, description, job_location)
        salary_text = build_salary_text(
            row.get("min_amount"),
            row.get("max_amount"),
            row.get("interval")
        )

        if not title or not job_url:
            continue

        normalized_job = {
            "title": title,
            "organization": company or "Unknown",
            "location": job_location,
            "remote_type": remote_type,
            "employment_type": safe_string(row.get("job_type")),
            "experience_level": None,
            "url": job_url,
            "source": f"jobspy:{site}" if site else "jobspy",
            "description": description or "",
            "salary_min": safe_int(row.get("min_amount")),
            "salary_max": safe_int(row.get("max_amount")),
            "salary_text": salary_text
        }

        raw_jobs.append(normalized_job)

    return raw_jobs

def detect_remote_type(title: str | None, description: str | None, location: str | None) -> str | None:
    text_parts = [
        title or "",
        description or "",
        location or ""
    ]

    text = " ".join(text_parts).lower()

    if "hybrid" in text:
        return "hybrid"

    if "remote" in text or "work from home" in text:
        return "remote"

    if "on-site" in text or "onsite" in text or "in person" in text:
        return "in_person"

    return None

def build_salary_text(min_amount: Any, max_amount: Any, interval: Any) -> str:
    min_salary = safe_int(min_amount)
    max_salary = safe_int(max_amount)
    interval_text = safe_string(interval)

    if min_salary and max_salary:
        if interval_text:
            return f"${min_salary} - ${max_salary} {interval_text}"
        return f"${min_salary} - ${max_salary}"

    if min_salary:
        if interval_text:
            return f"${min_salary}+ {interval_text}"
        return f"${min_salary}+"

    return ""
