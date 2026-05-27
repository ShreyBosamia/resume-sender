# Resume Sender

Resume Sender is an early-stage job discovery and review tool. It searches for jobs based on user preferences, normalizes job data into a local JSON store, scores jobs using rule-based preferences, and allows the user to approve or deny jobs from the terminal.

The long-term goal is to evolve this into an AI-assisted job search and application workflow that can help users discover relevant jobs, review them, learn from feedback, and eventually assist with resume tailoring and application workflows.

## Current Status

This project currently supports:

- Local JSON-based job storage
- User preferences through `preferences.json`
- Job search using JobSpy
- Rule-based job scoring
- Job deduplication
- Ranked terminal job review
- Approve / deny feedback collection
- A service-layer structure that can later support a FastAPI backend and web frontend

This is still an early development version. The terminal interface is mainly for backend testing before building a web UI.

## Project Goals

### Short-Term Goals

- Search for jobs based on user preferences
- Score and rank jobs by relevance
- Avoid duplicate job records
- Allow the user to approve or deny jobs
- Store feedback for future AI preference learning

### Long-Term Goals

- Add a web frontend for reviewing jobs
- Add a FastAPI backend
- Use AI to suggest improved preferences based on approved and denied jobs
- Use AI to compare jobs against a user's resume
- Generate tailored resume and cover letter suggestions
- Eventually support semi-automated application workflows with human review

## Current Architecture

```text
preferences.json
  -> JobSpy search
  -> Job normalization
  -> Rule-based scoring
  -> jobs.json
  -> Terminal review
  -> Approve / deny feedback
  -> feedback.json
```

The project is intentionally structured so that the terminal CLI, future API, and future frontend can share the same backend service logic.

## Folder Structure

```text
resume-sender/
  data/
    preferences.json
    jobs.json
    feedback.json
    runs.json

  src/
    main.py
    storage.py
    models.py
    scorer.py
    query_generator.py
    jobspy_source.py

    services/
      __init__.py
      job_service.py
      feedback_service.py
```

### Important Files

| File | Purpose |
|---|---|
| `src/main.py` | CLI entry point and command router |
| `src/storage.py` | JSON loading, saving, deduplication, and feedback persistence |
| `src/models.py` | Pydantic models for validating job and run data |
| `src/scorer.py` | Rule-based job scoring logic |
| `src/query_generator.py` | Generates search queries from user preferences |
| `src/jobspy_source.py` | Searches external job boards using JobSpy |
| `src/services/job_service.py` | Reusable job search and ranking functions |
| `src/services/feedback_service.py` | Reusable approve / deny feedback functions |
| `data/preferences.json` | User job preferences |
| `data/jobs.json` | Stored job records |
| `data/feedback.json` | Approved and denied job feedback |
| `data/runs.json` | Run tracking data from earlier pipeline work |

## Setup

### 1. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

On Windows:

```bash
venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install pydantic pandas python-jobspy requests python-dotenv
```

### 3. Create required data files

Create the `data/` directory:

```bash
mkdir -p data
```

Create `data/jobs.json`:

```json
{
  "jobs": {}
}
```

Create `data/feedback.json`:

```json
{
  "approved_jobs": {},
  "denied_jobs": {}
}
```

Create `data/runs.json`:

```json
{
  "runs": {}
}
```

Create `data/preferences.json` using the preference structure below.

## Example `preferences.json`

```json
{
  "target_roles": [
    "public health coordinator",
    "program coordinator",
    "health program assistant",
    "community health coordinator",
    "population health coordinator"
  ],
  "location": {
    "city": "Portland",
    "state": "OR",
    "radius_miles": 50
  },
  "remote_preference": [
    "remote",
    "hybrid",
    "in_person"
  ],
  "job_type": [
    "full_time",
    "part_time",
    "temporary"
  ],
  "experience_level": [
    "entry_level",
    "early_career"
  ],
  "preferred_keywords": [
    "public health",
    "program coordination",
    "program coordinator",
    "health equity",
    "community health",
    "health administration",
    "population health",
    "care coordination",
    "health program",
    "community outreach",
    "grant",
    "research assistant"
  ],
  "hard_excluded_keywords": [
    "physical therapist assistant",
    "physical therapy assistant",
    "certified medical assistant",
    "medical assistant",
    "nursing supervisor",
    "registered nurse",
    "rn license",
    "physician assistant",
    "md required",
    "do required"
  ],
  "soft_excluded_keywords": [
    "vital signs",
    "administer medications",
    "clinical procedures",
    "direct patient care",
    "hands-on patient care",
    "retail",
    "food service",
    "catering",
    "teacher",
    "delivery driver",
    "truck driver",
    "helper driver",
    "route driver",
    "pharmacy technician",
    "store manager",
    "sales associate"
  ],
  "seniority_penalty_keywords": [
    "director",
    "senior director",
    "executive director",
    "manager",
    "senior manager",
    "supervisor",
    "lead",
    "principal",
    "10 years",
    "8 years",
    "7 years",
    "6 years",
    "5 years of experience"
  ],
  "minimum_salary": null,
  "requires_mph_ok": true,
  "incoming_student_ok": true
}
```

Validate the JSON with:

```bash
python -m json.tool data/preferences.json
```

## CLI Usage

### Search for jobs

```bash
python src/main.py search
```

This runs a JobSpy search based on the target roles in `preferences.json`, scores the jobs, deduplicates them, and stores them in `data/jobs.json`.

### Review ranked jobs

```bash
python src/main.py review
```

Show more jobs:

```bash
python src/main.py review --limit 25
```

The review command prints ranked jobs with their job IDs, score, status, reason, concerns, matched keywords, and URL.

### Approve a job

```bash
python src/main.py approve <job_id> --reason "Good clinic admin/front office role"
```

Example:

```bash
python src/main.py approve abc123 --reason "Good program coordination role with community-facing responsibilities"
```

### Deny a job

```bash
python src/main.py deny <job_id> --reason "Too similar to direct clinical work"
```

Example:

```bash
python src/main.py deny def456 --reason "Physical therapy role, not public health admin"
```

### View feedback summary

```bash
python src/main.py feedback
```

## Data Model

### Job Record

Jobs are stored in `data/jobs.json`.

Each job has fields like:

```json
{
  "id": "sha256-url-hash",
  "title": "Program Coordinator",
  "organization": "Example Organization",
  "location": "Portland, OR",
  "remote_type": "hybrid",
  "employment_type": "fulltime",
  "experience_level": null,
  "url": "https://example.com/job",
  "canonical_url": "https://example.com/job",
  "source": "jobspy:indeed",
  "source_urls": [
    "https://example.com/job"
  ],
  "date_found": "2026-05-26",
  "last_seen": "2026-05-26",
  "job_status": "recommended",
  "application_status": "not_started",
  "description": "...",
  "requirements": [],
  "preferred_qualifications": [],
  "salary_min": 60000,
  "salary_max": 75000,
  "salary_text": "$60000 - $75000 yearly",
  "fit_score": 75,
  "fit_reason": "Strong match based on title, preferred keywords, and role fit.",
  "fit_concerns": [],
  "matched_keywords": [
    "program coordinator"
  ],
  "missing_keywords": [
    "public health"
  ],
  "applied": false
}
```

### Feedback Record

Feedback is stored in `data/feedback.json`.

Approved and denied jobs are stored separately:

```json
{
  "approved_jobs": {
    "job_id_here": {
      "job_id": "job_id_here",
      "feedback": "approved",
      "reason": "Good clinic admin role",
      "created_at": "2026-05-26T13:30:00",
      "job_snapshot": {
        "title": "Patient Care Coordinator",
        "organization": "Example Clinic",
        "location": "Salem, OR",
        "remote_type": null,
        "employment_type": "fulltime",
        "url": "https://example.com/job",
        "fit_score": 10,
        "fit_reason": "Weak match based on current preferences.",
        "fit_concerns": [],
        "matched_keywords": []
      }
    }
  },
  "denied_jobs": {}
}
```

The snapshot preserves what the job looked like at the time the user gave feedback.

## Scoring System

The current scorer is rule-based.

It starts with a baseline score, then adjusts based on:

- Target role matches
- Preferred keyword matches
- Hard excluded keywords
- Soft excluded keywords
- Remote preference
- Organization signals
- Seniority / experience penalties

### Score Meaning

| Score Range | Meaning |
|---:|---|
| `75-100` | Recommended |
| `50-74` | Maybe / review manually |
| `0-49` | Rejected or weak match |

### Job Statuses

| Status | Meaning |
|---|---|
| `recommended` | Strong fit based on current rules |
| `maybe` | Worth manual review |
| `rejected` | Weak fit or excluded |
| `discovered` | Found but not fully categorized or older status |

The scoring system is intentionally simple for now. It is expected to be replaced or supplemented by AI later.

## Known Limitations

### 1. Keyword scoring lacks context

A phrase like `patient care` can mean either direct clinical care or administrative clinic coordination. This is difficult to classify with simple keyword rules.

Example:

- `Physical Therapist Assistant` should be rejected.
- `Patient Care Coordinator` might be a good clinic admin role.

This is one reason the project now stores approval and denial feedback.

### 2. JobSpy data can be incomplete

Some sources, especially LinkedIn, may return jobs with empty descriptions or missing location fields.

### 3. Remote detection is imperfect

Remote status is currently inferred from title, location, and description text. This can produce false positives when job posts include generic policy language about remote work.

### 4. JSON is not a long-term database

JSON is fine for the current local prototype, but the project may eventually move to SQLite, PostgreSQL, or Supabase.

### 5. No frontend yet

The current interface is terminal-based. The terminal interface is only intended as a development tool before adding a web UI.

## Future Roadmap

### Near-Term

- Add better service-layer separation
- Add FastAPI backend
- Add simple web frontend for reviewing jobs
- Add approve / deny buttons in the UI
- Add job detail view
- Add filtering by score, status, source, and keyword matches

### AI Features

- AI-generated preferences from resume
- AI scoring based on resume + preferences
- AI preference learner from approved / denied jobs
- AI-suggested preference updates
- AI-generated resume tailoring suggestions
- AI-generated cover letter drafts
- AI-generated application question answers

### Application Automation

Long-term possible features:

- Resume upload support
- Structured resume profile extraction
- Application form autofill assistance
- Human-reviewed application submission
- Application status tracking

The project should avoid blind auto-applying. Any application submission should require human review.

## Future AI Preference Learning Design

The feedback system is designed to support future preference learning.

Example flow:

```text
User approves jobs
User denies jobs
  -> feedback.json accumulates examples
  -> AI analyzes patterns
  -> AI proposes preference changes
  -> User approves or rejects preference changes
  -> preferences.json is updated
```

Example AI suggestion:

```json
{
  "suggested_additions_to_preferred_keywords": [
    "clinic operations",
    "front office",
    "referral coordination",
    "insurance verification",
    "patient intake"
  ],
  "suggested_removals_from_soft_excluded_keywords": [
    "patient care"
  ],
  "reason": "The user approved administrative patient care coordinator roles but denied direct clinical care roles."
}
```

AI should suggest preference changes, not silently rewrite user preferences.

## Development Notes

### Run a clean search

```bash
rm data/jobs.json
python src/main.py search
```

If `jobs.json` does not exist, the storage layer should recreate it.

### Validate JSON files

```bash
python -m json.tool data/preferences.json
python -m json.tool data/jobs.json
python -m json.tool data/feedback.json
```

### Suggested `.gitignore`

```gitignore
.env
venv/
__pycache__/
*.pyc

data/jobs.json
data/feedback.json
data/runs.json

.DS_Store
```

You may want to commit a sample preferences file later, such as:

```text
data/preferences.example.json
```

but avoid committing personal job search data.

## Current Design Philosophy

This project is being built in layers:

```text
1. Local JSON backend
2. Terminal CLI
3. Service layer
4. FastAPI backend
5. Web frontend
6. AI agents
7. Application assistance
```

The terminal CLI is not the final product. It exists to test the backend workflow before building the web app.

The backend does not need to be perfect before adding a frontend. It only needs enough stable functionality to support:

- Listing ranked jobs
- Viewing job details
- Approving jobs
- Denying jobs
- Showing feedback
- Running job search

Once those functions are stable, the project can move toward FastAPI and a web UI.
