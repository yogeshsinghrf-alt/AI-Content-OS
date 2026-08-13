from apscheduler.schedulers.background import BackgroundScheduler

from app.api.package import daily_package
from app.api.email import send_package_email
from app.services.package_service import (
    get_package_by_id,
)

from app.services.visual_asset_service import (
    create_social_image_asset,
    create_linkedin_creative,
    create_instagram_creative,
    create_x_creative,
    create_infographic_asset,
    create_carousel_assets,
)

scheduler = BackgroundScheduler(
    timezone="Asia/Kolkata"
)


def run_topic_pipeline(topic: str):
    """
    Generate one fresh topic package,
    create its backend visual assets,
    and email that exact package.

    Never send an older package when
    fresh generation fails.
    """

    print(
        f"Starting scheduled pipeline for: {topic}"
    )

    try:
        # -------------------------------------------------
        # STEP 1 — GENERATE FRESH PACKAGE
        # -------------------------------------------------

        package_result = daily_package(
            topic=topic
        )

        if not package_result:
            raise RuntimeError(
                f"Fresh content generation returned "
                f"no result for {topic}."
            )

        if not isinstance(
            package_result,
            dict,
        ):
            raise RuntimeError(
                f"Fresh {topic} package returned "
                f"an invalid response."
            )

        package_status = package_result.get(
            "status"
        )

        if package_status in {
            "error",
            "unavailable",
            "quota_exceeded",
        }:
            raise RuntimeError(
                f"Fresh {topic} package could not "
                f"be generated: {package_result}"
            )

        package_id = package_result.get(
            "package_id"
        )

        if not package_id:
            raise RuntimeError(
                f"Fresh {topic} package has "
                f"no package_id."
            )

        print(
            f"Fresh package successfully generated "
            f"for {topic}: {package_id}"
        )
                # -------------------------------------------------
        # STEP 2 — CREATE SOCIAL PLATFORM IMAGES
        # -------------------------------------------------

        for platform in [
            "linkedin",
            "instagram",
            "x",
        ]:
            for option in [
                1,
                2,
            ]:
                social_result = (
                    create_social_image_asset(
                        package_result,
                        platform,
                        option,
                    )
                )

                if (
                    not isinstance(
                        social_result,
                        dict,
                    )
                    or social_result.get(
                        "status"
                    ) != "success"
                ):
                    raise RuntimeError(
                        f"{platform} option {option} "
                        f"image generation failed "
                        f"for {topic}: "
                        f"{social_result}"
                    )

                print(
                    f"Scheduled {platform} option "
                    f"{option} image created "
                    f"for {topic}."
                )
        # -------------------------------------------------
        # STEP 3 — CREATE FINISHED SOCIAL CREATIVES
        # -------------------------------------------------

        creative_functions = {
            "linkedin": create_linkedin_creative,
            "instagram": create_instagram_creative,
            "x": create_x_creative,
        }

        for platform, creative_function in (
            creative_functions.items()
        ):
            for option in [
                1,
                2,
            ]:
                creative_result = creative_function(
                    package_result,
                    option,
                )

                if (
                    not isinstance(
                        creative_result,
                        dict,
                    )
                    or creative_result.get(
                        "status"
                    ) != "success"
                ):
                    raise RuntimeError(
                        f"{platform} option {option} "
                        f"final creative failed "
                        f"for {topic}: "
                        f"{creative_result}"
                    )

                print(
                    f"Finished {platform} option "
                    f"{option} creative created "
                    f"for {topic}."
                )    
        # -------------------------------------------------
        # STEP 2 — CREATE INFOGRAPHIC
        # -------------------------------------------------

        infographic_result = (
            create_infographic_asset(
                package_result
            )
        )

        if (
            not isinstance(
                infographic_result,
                dict,
            )
            or infographic_result.get(
                "status"
            ) != "success"
        ):
            raise RuntimeError(
                f"Infographic generation failed "
                f"for {topic}: "
                f"{infographic_result}"
            )

        print(
            f"Scheduled infographic created "
            f"for {topic}."
        )

        # -------------------------------------------------
        # STEP 3 — CREATE 6-SLIDE CAROUSEL
        # -------------------------------------------------

        carousel_result = (
            create_carousel_assets(
                package_result
            )
        )

        if (
            not isinstance(
                carousel_result,
                dict,
            )
            or carousel_result.get(
                "status"
            ) != "success"
        ):
            raise RuntimeError(
                f"Carousel generation failed "
                f"for {topic}: "
                f"{carousel_result}"
            )

        if carousel_result.get(
            "slides"
        ) != 6:
            raise RuntimeError(
                f"Expected 6 carousel slides "
                f"for {topic}, but received "
                f"{carousel_result.get('slides')}."
            )

        print(
            f"6 scheduled carousel slides "
            f"created for {topic}."
        )
        
        # -------------------------------------------------
        # STEP 4 — RELOAD EXACT PACKAGE
        # -------------------------------------------------

        updated_package = get_package_by_id(
            package_id
        )

        if not updated_package:
            raise RuntimeError(
                f"Could not reload updated package "
                f"{package_id} for {topic}."
            )
        print(

            f"Updated package reloaded "
            f"for {topic}: {package_id}"
        )
        # -------------------------------------------------
        # STEP 5 — EMAIL THIS EXACT PACKAGE
        # -------------------------------------------------

        email_result = send_package_email(
            updated_package
        )

        if (
            not isinstance(
                email_result,
                dict,
            )
            or email_result.get(
                "status"
            ) != "success"
        ):
            raise RuntimeError(
                f"Email delivery failed for "
                f"{topic}: {email_result}"
            )

        result = {
            "status": "success",
            "topic": topic,
            "package_id": package_id,
            "infographic": "success",
            "carousel_slides": 6,
            "email_id": email_result.get(
                "email_id"
            ),
            "message": email_result.get(
                "message"
            ),
        }

        print(
            f"Completed scheduled pipeline "
            f"for {topic}: {result}"
        )

        return result

    except Exception as error:

        # Never fall back to an older package.
        result = {
            "status": "error",
            "topic": topic,
            "message": str(error),
        }

        print(
            f"Scheduled pipeline failed "
            f"for {topic}: {result}"
        )

        return result


def run_daily_pipeline():
    """
    Generate and email AI, Telecom
    and Marketing packages.
    """

    results = []

    for topic in [
        "ai",
        "telecom",
        "marketing",
    ]:
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

        # 08:00 AM India time
        hour=8,
        minute=00,

        id="daily-content-pipeline",
        replace_existing=True,
        coalesce=True,
        max_instances=1,
    )

    scheduler.start()

    print(
        "Daily scheduler started for "
        "08:00 AM Asia/Kolkata"
    )


def stop_scheduler():

    if scheduler.running:
        scheduler.shutdown(
            wait=False
        )

        print(
            "Daily scheduler stopped"
        )