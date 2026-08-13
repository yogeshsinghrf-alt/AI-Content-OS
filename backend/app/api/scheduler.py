import os
import threading

from fastapi import (
    APIRouter,
    Header,
    HTTPException,
    Response,
)

from app.services.scheduler_service import (
    run_topic_pipeline,
    scheduler,
)


router = APIRouter()


# ---------------------------------------------------------
# Prevent duplicate manual pipeline runs
# ---------------------------------------------------------

pipeline_lock = threading.Lock()

active_pipelines: set[str] = set()


def verify_scheduler_secret(
    x_scheduler_secret: str | None,
) -> None:
    expected_secret = os.getenv(
        "SCHEDULER_SECRET"
    )

    if not expected_secret:
        raise HTTPException(
            status_code=500,
            detail=(
                "SCHEDULER_SECRET is not configured."
            ),
        )

    if (
        x_scheduler_secret
        != expected_secret
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid scheduler secret.",
        )


def _pipeline_worker(
    topic: str,
) -> None:
    """
    Run one topic and always release
    its active lock when finished.
    """

    try:
        run_topic_pipeline(
            topic
        )

    finally:
        with pipeline_lock:
            active_pipelines.discard(
                topic
            )


def start_pipeline(
    topic: str,
) -> bool:
    """
    Start one topic only if the same
    topic is not already running.

    Returns True when started.
    Returns False when already active.
    """

    with pipeline_lock:
        if topic in active_pipelines:
            return False

        if "daily" in active_pipelines:
            return False

        active_pipelines.add(
            topic
        )

    worker = threading.Thread(
        target=_pipeline_worker,
        args=(topic,),
        daemon=True,
    )

    worker.start()

    return True


def _daily_worker() -> None:
    """
    Run AI, Telecom and Marketing
    sequentially in one worker.
    """

    try:
        for topic in [
            "ai",
            "telecom",
            "marketing",
        ]:
            run_topic_pipeline(
                topic
            )

    finally:
        with pipeline_lock:
            active_pipelines.discard(
                "daily"
            )


def start_daily_pipeline() -> bool:
    """
    Start the complete daily pipeline
    only when no other pipeline is active.
    """

    with pipeline_lock:
        if active_pipelines:
            return False

        active_pipelines.add(
            "daily"
        )

    thread = threading.Thread(
        target=_daily_worker,
        daemon=True,
    )

    thread.start()

    return True


# ---------------------------------------------------------
# STATUS
# ---------------------------------------------------------

@router.get("/status")
def scheduler_status():
    jobs = scheduler.get_jobs()

    with pipeline_lock:
        currently_active = sorted(
            active_pipelines
        )

    return {
        "running": scheduler.running,
        "active_pipelines":
            currently_active,
        "jobs": [
            {
                "id": job.id,
                "next_run_time": (
                    str(
                        job.next_run_time
                    )
                    if job.next_run_time
                    else None
                ),
            }
            for job in jobs
        ],
    }


# ---------------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------------

@router.get(
    "/ping",
    status_code=204,
)
def scheduler_ping():
    return Response(
        status_code=204
    )


# ---------------------------------------------------------
# MANUAL TOPIC RUNS
# ---------------------------------------------------------

@router.get(
    "/run-ai",
    status_code=202,
)
def run_ai(
    x_scheduler_secret: str | None = Header(
        default=None
    ),
):
    verify_scheduler_secret(
        x_scheduler_secret
    )

    started = start_pipeline(
        "ai"
    )

    if not started:
        raise HTTPException(
            status_code=409,
            detail=(
                "AI pipeline is already running "
                "or the daily pipeline is active."
            ),
        )

    return {
        "status": "accepted",
        "started": True,
        "topic": "ai",
        "message": (
            "AI pipeline started in the background."
        ),
    }


@router.get(
    "/run-telecom",
    status_code=202,
)
def run_telecom(
    x_scheduler_secret: str | None = Header(
        default=None
    ),
):
    verify_scheduler_secret(
        x_scheduler_secret
    )

    started = start_pipeline(
        "telecom"
    )

    if not started:
        raise HTTPException(
            status_code=409,
            detail=(
                "Telecom pipeline is already running "
                "or the daily pipeline is active."
            ),
        )

    return {
        "status": "accepted",
        "started": True,
        "topic": "telecom",
        "message": (
            "Telecom pipeline started "
            "in the background."
        ),
    }


@router.get(
    "/run-marketing",
    status_code=202,
)
def run_marketing(
    x_scheduler_secret: str | None = Header(
        default=None
    ),
):
    verify_scheduler_secret(
        x_scheduler_secret
    )

    started = start_pipeline(
        "marketing"
    )

    if not started:
        raise HTTPException(
            status_code=409,
            detail=(
                "Marketing pipeline is already running "
                "or the daily pipeline is active."
            ),
        )

    return {
        "status": "accepted",
        "started": True,
        "topic": "marketing",
        "message": (
            "Marketing pipeline started "
            "in the background."
        ),
    }


# ---------------------------------------------------------
# COMPLETE DAILY RUN
# ---------------------------------------------------------

@router.get(
    "/run-daily",
    status_code=202,
)
def run_daily(
    x_scheduler_secret: str | None = Header(
        default=None
    ),
):
    verify_scheduler_secret(
        x_scheduler_secret
    )

    started = start_daily_pipeline()

    if not started:
        raise HTTPException(
            status_code=409,
            detail=(
                "Another scheduler pipeline "
                "is already running."
            ),
        )

    return {
        "status": "accepted",
        "started": True,
        "topics": [
            "ai",
            "telecom",
            "marketing",
        ],
        "message": (
            "Daily content pipeline started "
            "in the background."
        ),
    }