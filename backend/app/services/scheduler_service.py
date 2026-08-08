from apscheduler.schedulers.background import BackgroundScheduler

from app.api.package import daily_package
from app.api.email import send_latest_email


scheduler = BackgroundScheduler(
    timezone="Asia/Kolkata"
)


def run_topic_pipeline(topic: str):
    """
    Generate one topic package, save it to history,
    create its PDF and send it by email.
    """
    print(f"Starting scheduled pipeline for: {topic}")

    try:
        package_result = daily_package(topic=topic)

        if not package_result:
            raise RuntimeError(
                f"Content generation returned no result for {topic}."
            )

        email_result = send_latest_email()

        if (
            not isinstance(email_result, dict)
            or email_result.get("status") != "success"
        ):
            raise RuntimeError(
                f"Email delivery failed for {topic}: {email_result}"
            )

        result = {
            "status": "success",
            "topic": topic,
            "email_id": email_result.get("email_id"),
            "message": email_result.get("message"),
        }

        print(
            f"Completed scheduled pipeline for {topic}: "
            f"{result}"
        )

        return result

    except Exception as error:
        result = {
            "status": "error",
            "topic": topic,
            "message": str(error),
        }

        print(
            f"Scheduled pipeline failed for {topic}: "
            f"{result}"
        )

        return result


def run_daily_pipeline():
    """
    Generate and email AI, Telecom and Marketing packages.
    """
    results = []

    for topic in ["ai", "telecom", "marketing"]:
        results.append(
            run_topic_pipeline(topic)
        )

    return results


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