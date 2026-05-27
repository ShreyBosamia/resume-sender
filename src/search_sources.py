from typing import Any


def fake_job_search(query: str) -> list[dict[str, Any]]:
    """
    Fake search results for testing the pipeline.

    Later, this function can be replaced with Brave Search,
    Google Custom Search, direct job board APIs, etc.
    """

    fake_results = [
        {
            "title": "Public Health Program Coordinator",
            "organization": "Multnomah County",
            "location": "Portland, OR",
            "remote_type": "hybrid",
            "employment_type": "full_time",
            "experience_level": "entry_level",
            "url": "https://example.com/jobs/123",
            "source": "fake_search",
            "description": "Supports public health program operations and community health initiatives."
        },
        {
            "title": "Community Health Program Assistant",
            "organization": "Oregon Health Authority",
            "location": "Salem, OR",
            "remote_type": "hybrid",
            "employment_type": "full_time",
            "experience_level": "early_career",
            "url": "https://example.com/jobs/456",
            "source": "fake_search",
            "description": "Assists with community health programs, data entry, and administrative coordination."
        },
        {
            "title": "Public Health Program Coordinator",
            "organization": "Multnomah County",
            "location": "Portland, OR",
            "remote_type": "hybrid",
            "employment_type": "full_time",
            "experience_level": "entry_level",
            "url": "https://indeed.com/viewjob?jk=duplicate-example",
            "source": "fake_search_indeed",
            "description": "Duplicate posting from another source."
        },
        {
            "title": "Physical Therapist Assistant",
            "organization": "Example Rehab Clinic",
            "location": "Portland, OR",
            "remote_type": "in_person",
            "employment_type": "full_time",
            "experience_level": "entry_level",
            "url": "https://example.com/jobs/pta-999",
            "source": "fake_search",
            "description": "Provides physical therapy treatments under PT supervision."
        }
    ]

    # Pretend the search query affects the result.
    # For now, return all fake results for every query.
    return fake_results
