import sys
import traceback
from datetime import datetime, timezone

from app.services.scheduler_service import run_topic_pipeline


TOPICS = ["ai", "telecom", "marketing"]


def main() -> int:
    print("=" * 60)
    print(
        "AI Content OS daily job started:",
        datetime.now(timezone.utc).isoformat(),
    )
    print("=" * 60)

    failures = []

    for topic in TOPICS:
        print(f"\nStarting topic: {topic}")

        try:
            result = run_topic_pipeline(topic)

            print(f"Result for {topic}: {result}")

            if not result or result.get("status") != "success":
                failures.append(
                    {
                        "topic": topic,
                        "result": result,
                    }
                )
            else:
                print(f"Successfully completed: {topic}")

        except Exception as error:
            traceback.print_exc()

            failures.append(
                {
                    "topic": topic,
                    "error": str(error),
                }
            )

    if failures:
        print("\nDaily job completed with failures:")
        print(failures)
        return 1

    print("\nAll three topics completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())