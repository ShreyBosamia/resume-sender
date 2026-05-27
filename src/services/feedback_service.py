from typing import Any

from storage import (
    load_feedback,
    record_job_feedback
)


def approve_job_feedback(job_id: str, reason: str | None = None) -> dict[str, Any]:
    record_job_feedback(
        job_id=job_id,
        feedback_type="approved",
        reason=reason
    )

    return {
        "job_id": job_id,
        "feedback": "approved",
        "reason": reason or ""
    }


def deny_job_feedback(job_id: str, reason: str | None = None) -> dict[str, Any]:
    record_job_feedback(
        job_id=job_id,
        feedback_type="denied",
        reason=reason
    )

    return {
        "job_id": job_id,
        "feedback": "denied",
        "reason": reason or ""
    }


def get_feedback_summary() -> dict[str, Any]:
    feedback = load_feedback()

    approved_jobs = feedback.get("approved_jobs", {})
    denied_jobs = feedback.get("denied_jobs", {})

    return {
        "approved_count": len(approved_jobs),
        "denied_count": len(denied_jobs),
        "approved_jobs": list(approved_jobs.values()),
        "denied_jobs": list(denied_jobs.values())
    }
