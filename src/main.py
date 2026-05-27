import argparse

from services.job_service import get_ranked_jobs, search_and_save_jobs
from services.feedback_service import (
    approve_job_feedback,
    deny_job_feedback,
    get_feedback_summary
)


def run_search() -> None:
    summary = search_and_save_jobs()

    print("\nSearch pipeline complete.")
    print(f"Queries generated: {summary['queries_generated']}")
    print(f"Raw jobs found: {summary['raw_jobs_found']}")
    print(f"New jobs added: {summary['new_jobs_added']}")
    print(f"Duplicates updated: {summary['duplicates_updated']}")
    print(f"Total jobs stored: {summary['total_jobs_stored']}")


def review_jobs(limit: int = 15) -> None:
    jobs = get_ranked_jobs(limit=limit)

    print("\nTop jobs for review:")
    print(f"Showing top {len(jobs)} jobs\n")

    for index, job in enumerate(jobs, start=1):
        print(
            f"[{index}] [{job.get('fit_score')}] "
            f"{job.get('title')} at {job.get('organization')}"
        )
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


def approve_job(job_id: str, reason: str | None) -> None:
    result = approve_job_feedback(job_id, reason)

    print("\nApproved job feedback recorded.")
    print(f"Job ID: {result['job_id']}")

    if result["reason"]:
        print(f"Reason: {result['reason']}")


def deny_job(job_id: str, reason: str | None) -> None:
    result = deny_job_feedback(job_id, reason)

    print("\nDenied job feedback recorded.")
    print(f"Job ID: {result['job_id']}")

    if result["reason"]:
        print(f"Reason: {result['reason']}")


def show_feedback() -> None:
    summary = get_feedback_summary()

    print("\nFeedback summary")
    print(f"Approved jobs: {summary['approved_count']}")
    print(f"Denied jobs: {summary['denied_count']}")

    print("\nApproved jobs:")
    for record in summary["approved_jobs"]:
        snapshot = record.get("job_snapshot", {})
        print(f"- {snapshot.get('title')} at {snapshot.get('organization')}")
        print(f"  Job ID: {record.get('job_id')}")
        print(f"  Reason: {record.get('reason')}")
        print()

    print("\nDenied jobs:")
    for record in summary["denied_jobs"]:
        snapshot = record.get("job_snapshot", {})
        print(f"- {snapshot.get('title')} at {snapshot.get('organization')}")
        print(f"  Job ID: {record.get('job_id')}")
        print(f"  Reason: {record.get('reason')}")
        print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Resume Sender job discovery tool"
    )

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("search", help="Search for jobs")

    review_parser = subparsers.add_parser("review", help="Review top ranked jobs")
    review_parser.add_argument(
        "--limit",
        type=int,
        default=15,
        help="Number of jobs to show"
    )

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

    args = parser.parse_args()

    if args.command == "search":
        run_search()
    elif args.command == "review":
        review_jobs(args.limit)
    elif args.command == "approve":
        approve_job(args.job_id, args.reason)
    elif args.command == "deny":
        deny_job(args.job_id, args.reason)
    elif args.command == "feedback":
        show_feedback()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
