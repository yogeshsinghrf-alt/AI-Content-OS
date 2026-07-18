from fastapi import APIRouter

from app.services.scheduler_service import (
    run_topic_pipeline,
    scheduler,
)

router = APIRouter()


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
        "message": "AI pipeline completed. Check history and email.",
    }