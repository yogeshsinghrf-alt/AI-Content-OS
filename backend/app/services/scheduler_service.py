from apscheduler.schedulers.background import BackgroundScheduler

from app.api.package import daily_package
from app.api.email import send_latest_email


scheduler = BackgroundScheduler(
    timezone="Asia/Kolkata"
)


def run_topic_pipeline(topic: str):
    """
    Generate one topic package, save it to history,
    create its PDF and send the latest package by email.
    """
    print(f"Starting scheduled pipeline for: {topic}")

    try:
        daily_package(topic=topic)
        email_result = send_latest_email()

        print(
            f"Completed scheduled pipeline for {topic}: "
            f"{email_result}"
        )

    except Exception as error:
        print(
            f"Scheduled pipeline failed for {topic}: {error}"
        )


def run_daily_pipeline():
    """
    Generate and email AI, Telecom and Marketing packages.
    """
    for topic in ["ai", "telecom", "marketing"]:
        run_topic_pipeline(topic)


def start_scheduler():
    if scheduler.running:
        return

    scheduler.add_job(
        run_daily_pipeline,
        trigger="cron",
        hour=8,
        minute=0,
        id="daily-content-pipeline",
        replace_existing=True,
        coalesce=True,
        max_instances=1,
    )

    scheduler.start()
    print("Daily scheduler started for 08:00 AM Asia/Kolkata")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        print("Daily scheduler stopped")