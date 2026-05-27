from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import date

class JobRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    id: str

    title:str
    organization:str
    location: Optional[str] = None
    remote_type: Optional[str] = None
    employment_type: Optional[str] = None
    experience_level: Optional[str] = None

    url: str
    canonical_url: Optional[str] = None
    source: str
    source_urls: List[str] = Field(default_factory=list)

    date_found: str = Field(default_factory=lambda: str(date.today()))
    last_seen: str = Field(default_factory=lambda: str(date.today()))

    job_status: str = "discovered"
    application_status: str = "not_started"

    description: str = ""
    requirements: List[str] = Field(default_factory=list)
    preferred_qualifications: List[str] = Field(default_factory=list)

    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_text: str = ""

    fit_score: Optional[int] = None
    fit_reason: Optional[str] = None
    fit_concerns: List[str] = Field(default_factory=list)

    matched_keywords: List[str] = Field(default_factory=list)
    missing_keywords: List[str] = Field(default_factory=list)

    applied: bool = False

class RunStep(BaseModel):
    name: str
    status: str = "pending"
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    error: Optional[str] = None

class PipelineRun(BaseModel):
    id: str
    started_at: str
    ended_at: Optional[str] = None
    run_status: str = "running"
    current_step: Optional[str] = None
    steps: List[RunStep] = Field(default_factory=list)
    jobs_found: int = 0
    new_jobs: int = 0
    duplicates: int = 0
    errors: List[str] = Field(default_factory=list)

    
