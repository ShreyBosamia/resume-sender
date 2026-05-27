from storage import (
    create_run,
    start_step,
    complete_step,
    fail_step,
    complete_run,
    load_preferences,
    upsert_job,
    load_jobs,
    update_run_counts,
    record_job_feedback,
    load_feedback
)
import argparse
import time
from query_generator import generate_search_queries
from brave_search import brave_search, brave_results_to_jobs
from scorer import score_job
from jobspy_source import jobspy_search

def run_search():
    run_id = create_run()
    current_step = None

    try:
        current_step = "loading_preferences"
        start_step(run_id, current_step)

        preferences = load_preferences()

        complete_step(run_id, current_step)

        current_step = "generating_queries"
        start_step(run_id, current_step)

        queries = generate_search_queries(preferences)
        queries = queries[:3]

        complete_step(run_id, current_step)

        
        current_step = "searching_jobspy"
        start_step(run_id, current_step)
        
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
                results_wanted=10
            )
        
            raw_jobs.extend(jobs)
        
        complete_step(run_id, current_step)

        '''
        current_step = "searching_source"
        start_step(run_id, current_step)

        raw_jobs = []
        source_pages = []

        for query in queries:
            print(f"Searching: {query}")

            search_results = brave_search(query, count=5)
            jobs, pages = brave_results_to_jobs(search_results, query)

            raw_jobs.extend(jobs)
            source_pages.extend(pages)

            time.sleep(1)

        complete_step(run_id, current_step)
        '''
        current_step = "saving_jobs"
        start_step(run_id, current_step)

        new_count = 0
        duplicate_count = 0

        for job in raw_jobs:
            scored_job = score_job(job, preferences)
            is_new = upsert_job(scored_job)

            if is_new:
                new_count += 1
            else:
                duplicate_count += 1

        update_run_counts(
            run_id,
            jobs_found=len(raw_jobs),
            new_jobs=new_count,
            duplicates=duplicate_count
        )

        complete_step(run_id, current_step)

        current_step = "printing_results"
        start_step(run_id, current_step)

        data = load_jobs()
        jobs = list(data["jobs"].values())

        jobs.sort(
            key=lambda job: job["fit_score"] if job["fit_score"] is not None else -1,
            reverse=True
        )

        print("\nSearch pipeline complete.")
        print(f"Run ID: {run_id}")
        print(f"Queries generated: {len(queries)}")
        print(f"Raw jobs found: {len(raw_jobs)}")
        # print(f"Source pages found: {len(source_pages)}")
        print(f"New jobs added: {new_count}")
        print(f"Duplicates updated: {duplicate_count}")
        print(f"Total jobs stored: {len(jobs)}")

        print("\nStored jobs:")
        for job in jobs:
            print(f"- [{job.get('fit_score')}] {job['title']} at {job['organization']}")
            print(f"  Job ID: {job.get('id')}")
            print(f"  Location: {job.get('location')}")
            print(f"  Remote: {job.get('remote_type')}")
            print(f"  Sources: {len(job.get('source_urls', []))}")
            print(f"  Status: {job.get('job_status')}")
            print(f"  Reason: {job.get('fit_reason')}")

            if job.get("fit_concerns"):
                print(f" Concerns: {', '.join(job.get('fit_concerns'))}")
                
            print(f"  URL: {job.get('canonical_url')}")
            print()

        #print("\nSource pages found:")
        #for page in source_pages:
         #   print(f"- [{page['source_type']}] {page['title']}")
          #  print(f"  URL: {page['url']}")
           # print()

        complete_step(run_id, current_step)
        complete_run(run_id)

    except Exception as error:
        if current_step is not None:
            fail_step(run_id, current_step, str(error))
        else:
            fail_step(run_id, "pipeline_error", str(error))

        raise

def approve_job(job_id: str, reason: str | None) -> None:
    record_job_feedback(
        job_id=job_id,
        feedback_type="approved",
        reason=reason
    )

    print("\nApproved job feedback recorded.")
    print(f"Job ID: {job_id}")

    if reason:
        print(f"Reason: {reason}")


def deny_job(job_id: str, reason: str | None) -> None:
    record_job_feedback(
        job_id=job_id,
        feedback_type="denied",
        reason=reason
    )

    print("\nDenied job feedback recorded.")
    print(f"Job ID: {job_id}")

    if reason:
        print(f"Reason: {reason}")


def show_feedback() -> None:
    feedback = load_feedback()

    approved_jobs = feedback.get("approved_jobs", {})
    denied_jobs = feedback.get("denied_jobs", {})

    print("\nFeedback summary")
    print(f"Approved jobs: {len(approved_jobs)}")
    print(f"Denied jobs: {len(denied_jobs)}")

    print("\nApproved jobs:")
    for record in approved_jobs.values():
        snapshot = record.get("job_snapshot", {})
        print(f"- {snapshot.get('title')} at {snapshot.get('organization')}")
        print(f"  Job ID: {record.get('job_id')}")
        print(f"  Reason: {record.get('reason')}")
        print()

    print("\nDenied jobs:")
    for record in denied_jobs.values():
        snapshot = record.get("job_snapshot", {})
        print(f"- {snapshot.get('title')} at {snapshot.get('organization')}")
        print(f"  Job ID: {record.get('job_id')}")
        print(f"  Reason: {record.get('reason')}")
        print()


def review_jobs(limit: int = 15) -> None:
    data = load_jobs()
    jobs = list(data.get("jobs", {}).values())

    jobs.sort(
        key=lambda job: job["fit_score"] if job["fit_score"] is not None else -1,
        reverse=True
    )

    print("\nTop jobs for review:")
    print(f"Showing top {min(limit, len(jobs))} of {len(jobs)} jobs\n")

    for index, job in enumerate(jobs[:limit], start=1):
        print(f"[{index}] [{job.get('fit_score')}] {job.get('title')} at {job.get('organization')}")
        print(f"    Job ID: {job.get('id')}")
        print(f"    Status: {job.get('job_status')}")
        print(f"    Location: {job.get('location')}")
        print(f"    Remote: {job.get('remote_type')}")
        print(f"    Employment Type: {job.get('employment_type')}")
        print(f"    Reason: {job.get('fit_reason')}")

        if job.get("fit_concerns"):
            print(f"    Concerns: {', '.join(job.get('fit_concerns'))}")

        if job.get("matched_keywords"):
            print(f"    Matched: {', '.join(job.get('matched_keywords'))}")

        print(f"    URL: {job.get('canonical_url') or job.get('url')}")
        print()
        
def main():
    parser = argparse.ArgumentParser(
        description="Resume Sender job discovery tool"
    )

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("search", help="Search for jobs")

    approve_parser = subparsers.add_parser("approve", help="Approve a job")
    approve_parser.add_argument("job_id", help="The job ID to approve")
    approve_parser.add_argument(
        "--reason",
        default=None,
        help="Why this job is a good fit"
    )

    deny_parser = subparsers.add_parser("deny", help="Deny a job")
    deny_parser.add_argument("job_id", help="The job ID to deny")
    deny_parser.add_argument(
        "--reason",
        default=None,
        help="Why this job is not a good fit"
    )

    subparsers.add_parser("feedback", help="Show feedback summary")

    review_parser = subparsers.add_parser("review", help="Review top ranked jobs")
    review_parser.add_argument(
        "--limit",
        type=int,
        default=15,
        help="Number of jobs to show"
    )

    args = parser.parse_args()

    if args.command == "search":
        run_search()
    elif args.command == "approve":
        approve_job(args.job_id, args.reason)
    elif args.command == "deny":
        deny_job(args.job_id, args.reason)
    elif args.command == "feedback":
        show_feedback()
    elif args.command == "review":
        review_jobs(args.limit)
    else:
        parser.print_help()



if __name__ == "__main__":
    main()
