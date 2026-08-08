import os
import threading

from fastapi import APIRouter, Header, HTTPException, Response

from app.services.scheduler_service import (
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


def start_pipeline(topic: str) -> None:
    worker = threading.Thread(
        target=run_topic_pipeline,
        args=(topic,),
        daemon=True,
    )
    worker.start()
def start_daily_pipeline() -> None:
    """
    Run AI, Telecom and Marketing sequentially
    in one background worker.
    """
    def worker():
        for topic in ["ai", "telecom", "marketing"]:
            run_topic_pipeline(topic)

    thread = threading.Thread(
        target=worker,
        daemon=True,
    )
    thread.start()

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


@router.get("/ping", status_code=204)
def scheduler_ping():
    return Response(status_code=204)


@router.get("/run-ai", status_code=204)
def run_ai(
    x_scheduler_secret: str | None = Header(default=None),
):
    verify_scheduler_secret(x_scheduler_secret)
    start_pipeline("ai")
    return Response(status_code=204)


@router.get("/run-telecom", status_code=204)
def run_telecom(
    x_scheduler_secret: str | None = Header(default=None),
):
    verify_scheduler_secret(x_scheduler_secret)
    start_pipeline("telecom")
    return Response(status_code=204)


@router.get("/run-marketing", status_code=204)
def run_marketing(
    x_scheduler_secret: str | None = Header(default=None),
):
    verify_scheduler_secret(x_scheduler_secret)
    start_pipeline("marketing")
    return Response(status_code=204)
@router.get("/run-daily", status_code=204)
def run_daily(
    x_scheduler_secret: str | None = Header(default=None),
):
    verify_scheduler_secret(x_scheduler_secret)
    start_daily_pipeline()

    return Response(status_code=204)    