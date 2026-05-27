from typing import Any

from storage import (
    load_jobs,
    load_preferences,
    upsert_job,
    update_run_counts
)
from query_generator import generate_search_queries
from jobspy_source import jobspy_search
from scorer import score_job


def get_ranked_jobs(limit: int | None = None) -> list[dict[str, Any]]:
    data = load_jobs()
    jobs = list(data.get("jobs", {}).values())

    jobs.sort(
        key=lambda job: job["fit_score"] if job.get("fit_score") is not None else -1,
        reverse=True
    )

    if limit is not None:
        return jobs[:limit]

    return jobs


def search_and_save_jobs() -> dict[str, Any]:
    preferences = load_preferences()
    queries = generate_search_queries(preferences)

    location = preferences.get("location", {})
    city = location.get("city")
    state = location.get("state")
    location_text = f"{city}, {state}" if city and state else state or ""

    target_roles = preferences.get("target_roles", [])
    jobspy_terms = target_roles[:3]

    raw_jobs = []

    for term in jobspy_terms:
        print(f"JobSpy searching: {term} in {location_text}")

        jobs = jobspy_search(
            search_term=term,
            location=location_text,
            results_wanted=20
        )

        raw_jobs.extend(jobs)

    new_count = 0
    duplicate_count = 0

    for job in raw_jobs:
        scored_job = score_job(job, preferences)
        is_new = upsert_job(scored_job)

        if is_new:
            new_count += 1
        else:
            duplicate_count += 1

    return {
        "queries_generated": len(queries),
        "raw_jobs_found": len(raw_jobs),
        "new_jobs_added": new_count,
        "duplicates_updated": duplicate_count,
        "total_jobs_stored": len(get_ranked_jobs())
    }
