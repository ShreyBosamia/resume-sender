import json
import hashlib
from pathlib import Path
from datetime import date, datetime
from typing import Dict, Any, Optional

from models import JobRecord, PipelineRun, RunStep


DATA_DIR = Path("data")
JOBS_PATH = DATA_DIR / "jobs.json"
PREFERENCES_PATH = DATA_DIR / "preferences.json"
RUNS_PATH = DATA_DIR / "runs.json"
FEEDBACK_PATH = DATA_DIR / "feedback.json"
def load_json(path: Path, default: Dict[str, Any]) -> Dict[str, Any]:
    if not path.exists():
        return default

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)

def save_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

def load_jobs() -> Dict[str, Any]:
    return load_json(JOBS_PATH, {"jobs": {}})


def save_jobs(data: Dict[str, Any]) -> None:
    save_json(JOBS_PATH, data)

def load_preferences() -> Dict[str, Any]:
    return load_json(PREFERENCES_PATH, {})


def normalize_url(url: str) -> str:
    """
    Basic v1 URL normalization.
    Later, we can improve this to remove tracking params.
    """
    return url.strip().lower().split("#")[0]


def make_url_hash(url: str) -> str:
    normalized = normalize_url(url)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def make_content_hash(title: str, organization: str, location: str | None) -> str:
    normalized = f"{organization}|{title}|{location or ''}".lower().strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def upsert_job(raw_job: Dict[str, Any]) -> bool:
    """
    Adds or updates a job.

    Returns:
        True if this is a new job.
        False if it updated an existing job.
    """
    data = load_jobs()

    url_hash = make_url_hash(raw_job["url"])
    content_hash = make_content_hash(
        raw_job["title"],
        raw_job["organization"],
        raw_job.get("location")
    )

    jobs = data["jobs"]

    existing_id = None

    # Layer 1: exact URL match
    if url_hash in jobs:
        existing_id = url_hash

    # Layer 2: title + organization + location match
    if existing_id is None:
        for job_id, job in jobs.items():
            existing_content_hash = make_content_hash(
                job["title"],
                job["organization"],
                job.get("location")
            )

            if existing_content_hash == content_hash:
                existing_id = job_id
                break

    if existing_id:
        existing_job = jobs[existing_id]

        source_urls = set(existing_job.get("source_urls", []))
        source_urls.add(raw_job["url"])

        updated_job = {
            **existing_job,
            **raw_job,
            "id": existing_id,
            "source_urls": sorted(source_urls),
            "last_seen": str(date.today())
        }

        jobs[existing_id] = JobRecord(**updated_job).model_dump()
        save_jobs(data)
        return False

    new_job = {
        **raw_job,
        "id": url_hash,
        "canonical_url": raw_job.get("canonical_url") or raw_job["url"],
        "source_urls": [raw_job["url"]],
        "date_found": str(date.today()),
        "last_seen": str(date.today()),
        "job_status": "discovered",
        "application_status": "not_started"
    }

    jobs[url_hash] = JobRecord(**new_job).model_dump()
    save_jobs(data)
    return True

def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")

def load_runs() -> Dict[str, Any]:
    return load_json(RUNS_PATH, {"runs": {}})

def save_runs(data: Dict[str, Any]) -> None:
    save_json(RUNS_PATH, data)

def create_run() -> str:
    """
    Creates a new pipeline run and returns its run_id.
    """
    data = load_runs()

    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    run_id = f"run_{timestamp}"

    run = PipelineRun(
        id=run_id,
        started_at=now_iso(),
        run_status="running",
        current_step=None,
        steps=[]
    )

    data["runs"][run_id] = run.model_dump()
    save_runs(data)

    return run_id

def get_run(run_id: str) -> Dict[str, Any]:
    data = load_runs()

    if run_id not in data["runs"]:
        raise ValueError(f"Run not found: {run_id}")
    
    return data["runs"][run_id]

def save_run(run: Dict[str, Any]) -> None:
    data = load_runs()

    run_id = run["id"]
    data["runs"][run_id] = PipelineRun(**run).model_dump()

    save_runs(data)


def start_step(run_id: str, step_name: str) -> None:
    run = get_run(run_id)

    step = RunStep(
        name=step_name,
        status="running",
        started_at=now_iso()
    )

    run["current_step"] = step_name
    run["steps"].append(step.model_dump())

    save_run(run)


def complete_step(run_id: str, step_name: str) -> None:
    run = get_run(run_id)

    for step in reversed(run["steps"]):
        if step["name"] == step_name and step["status"] == "running":
            step["status"] = "completed"
            step["ended_at"] = now_iso()
            break

    save_run(run)


def fail_step(run_id: str, step_name: str, error_message: str) -> None:
    run = get_run(run_id)

    for step in reversed(run["steps"]):
        if step["name"] == step_name and step["status"] == "running":
            step["status"] = "failed"
            step["ended_at"] = now_iso()
            step["error"] = error_message
            break

    run["run_status"] = "failed"
    run["current_step"] = step_name
    run["errors"].append(error_message)
    run["ended_at"] = now_iso()

    save_run(run)


def update_run_counts(
    run_id: str,
    jobs_found: int | None = None,
    new_jobs: int | None = None,
    duplicates: int | None = None
) -> None:
    run = get_run(run_id)

    if jobs_found is not None:
        run["jobs_found"] = jobs_found

    if new_jobs is not None:
        run["new_jobs"] = new_jobs

    if duplicates is not None:
        run["duplicates"] = duplicates

    save_run(run)


def complete_run(run_id: str) -> None:
    run = get_run(run_id)

    run["run_status"] = "completed"
    run["current_step"] = "completed"
    run["ended_at"] = now_iso()

    save_run(run)
    
def load_feedback() -> Dict[str, Any]:
    return load_json(FEEDBACK_PATH, {"approved_jobs": {}, "denied_jobs": {}})


def save_feedback(data: Dict[str, Any]) -> None:
    save_json(FEEDBACK_PATH, data)


def get_job_by_id(job_id: str) -> Dict[str, Any]:
    data = load_jobs()
    jobs = data.get("jobs", {})

    if job_id not in jobs:
        raise ValueError(f"Job not found: {job_id}")

    return jobs[job_id]


def record_job_feedback(
    job_id: str,
    feedback_type: str,
    reason: Optional[str] = None
) -> None:
    """
    Records user feedback for a job.

    feedback_type must be either:
    - approved
    - denied
    """

    if feedback_type not in ["approved", "denied"]:
        raise ValueError("feedback_type must be either 'approved' or 'denied'")

    job = get_job_by_id(job_id)
    feedback_data = load_feedback()

    record = {
        "job_id": job_id,
        "feedback": feedback_type,
        "reason": reason or "",
        "created_at": now_iso(),
        "job_snapshot": {
            "title": job.get("title"),
            "organization": job.get("organization"),
            "location": job.get("location"),
            "remote_type": job.get("remote_type"),
            "employment_type": job.get("employment_type"),
            "url": job.get("canonical_url") or job.get("url"),
            "fit_score": job.get("fit_score"),
            "fit_reason": job.get("fit_reason"),
            "fit_concerns": job.get("fit_concerns", []),
            "matched_keywords": job.get("matched_keywords", [])
        }
    }

    if feedback_type == "approved":
        feedback_data["approved_jobs"][job_id] = record

        # If it was previously denied, remove it from denied.
        feedback_data["denied_jobs"].pop(job_id, None)

    if feedback_type == "denied":
        feedback_data["denied_jobs"][job_id] = record

        # If it was previously approved, remove it from approved.
        feedback_data["approved_jobs"].pop(job_id, None)

    save_feedback(feedback_data)
