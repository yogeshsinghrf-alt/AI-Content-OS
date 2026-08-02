import base64
import os
from pathlib import Path

import requests
from dotenv import load_dotenv


load_dotenv()


def send_email(
    subject: str,
    body: str,
    html_body: str | None = None,
    attachments: list[str] | None = None,
):
    api_key = os.getenv("RESEND_API_KEY")
    email_to = os.getenv("EMAIL_TO")
    email_from = os.getenv(
        "RESEND_FROM",
        "AI Content OS <onboarding@resend.dev>",
    )

    if not api_key:
        return {
            "status": "error",
            "message": "RESEND_API_KEY is missing.",
        }

    if not email_to:
        return {
            "status": "error",
            "message": "EMAIL_TO is missing.",
        }

    payload = {
        "from": email_from,
        "to": [email_to],
        "subject": subject,
        "text": body,
    }

    if html_body:
        payload["html"] = html_body

    resend_attachments = []

    for attachment_path in attachments or []:
        path = Path(attachment_path)

        if not path.exists():
            print(f"Attachment missing: {path}")
            continue

        encoded_content = base64.b64encode(
            path.read_bytes()
        ).decode("utf-8")

        resend_attachments.append(
            {
                "filename": path.name,
                "content": encoded_content,
            }
        )

    if resend_attachments:
        payload["attachments"] = resend_attachments

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    print("Sending email through Resend HTTP API")
    print("TO:", email_to)
    print("FROM:", email_from)
    print("Attachments:", len(resend_attachments))

    try:
        response = requests.post(
            "https://api.resend.com/emails",
            headers=headers,
            json=payload,
            timeout=(10, 120),
        )

        print("Resend HTTP status:", response.status_code)
        print("Resend response:", response.text)

        response.raise_for_status()
        result = response.json()

        return {
            "status": "success",
            "message": "Email sent successfully through Resend.",
            "email_id": result.get("id"),
        }

    except requests.Timeout:
        return {
            "status": "error",
            "message": "Resend request timed out.",
        }

    except requests.RequestException as error:
        error_details = str(error)

        if error.response is not None:
            error_details = error.response.text

        return {
            "status": "error",
            "message": error_details,
        }

    except Exception as error:
        return {
            "status": "error",
            "message": str(error),
        }