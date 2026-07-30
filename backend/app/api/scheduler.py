import os

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException

from app.services.scheduler_service import (
    run_daily_pipeline,
    run_topic_pipeline,
    scheduler,
)


router = APIRouter()


def verify_scheduler_secret(
    x_scheduler_secret: str | None,
) -> None:
    expected_secret = os.getenv("SCHEDULER_SECRET")

    if not expected_secret:
        raise HTTPException(
            status_code=500,
            detail="SCHEDULER_SECRET is not configured.",
        )

    if x_scheduler_secret != expected_secret:
        raise HTTPException(
            status_code=401,
            detail="Invalid scheduler secret.",
        )


@router.get("/status")
def scheduler_status():
    jobs = scheduler.get_jobs()

    return {
        "running": scheduler.running,
        "jobs": [
            {
                "id": job.id,
                "next_run_time": (
                    str(job.next_run_time)
                    if job.next_run_time
                    else None
                ),
            }
            for job in jobs
        ],
    }


@router.get("/test-ai")
def test_ai_pipeline():
    run_topic_pipeline("ai")

    return {
        "status": "success",
        "message": "AI pipeline completed.",
    }


@router.get("/run-ai")
def run_ai(
    background_tasks: BackgroundTasks,
    x_scheduler_secret: str | None = Header(default=None),
):
    verify_scheduler_secret(x_scheduler_secret)

    background_tasks.add_task(
        run_topic_pipeline,
        "ai",
    )

    return {
        "status": "accepted",
        "message": "AI pipeline started in the background.",
    }


@router.get("/run-telecom")
def run_telecom(
    background_tasks: BackgroundTasks,
    x_scheduler_secret: str | None = Header(default=None),
):
    verify_scheduler_secret(x_scheduler_secret)

    background_tasks.add_task(
        run_topic_pipeline,
        "telecom",
    )

    return {
        "status": "accepted",
        "message": "Telecom pipeline started in the background.",
    }


@router.get("/run-marketing")
def run_marketing(
    background_tasks: BackgroundTasks,
    x_scheduler_secret: str | None = Header(default=None),
):
    verify_scheduler_secret(x_scheduler_secret)

    background_tasks.add_task(
        run_topic_pipeline,
        "marketing",
    )

    return {
        "status": "accepted",
        "message": "Marketing pipeline started in the background.",
    }


@router.get("/run-daily")
def run_daily_now(
    background_tasks: BackgroundTasks,
    x_scheduler_secret: str | None = Header(default=None),
):
    verify_scheduler_secret(x_scheduler_secret)

    background_tasks.add_task(run_daily_pipeline)

    return {
        "status": "accepted",
        "message": "Daily pipeline started in the background.",
    }