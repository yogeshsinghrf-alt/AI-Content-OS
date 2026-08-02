import base64
import os
from pathlib import Path

import resend
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

    resend.api_key = api_key
    print("RESEND_API_KEY prefix:", api_key[:12])
    print("Sending email TO:", email_to)
    print("Sending email FROM:", email_from)
    resend_attachments = []

    for attachment_path in attachments or []:
        path = Path(attachment_path)

        if not path.exists():
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

    params: resend.Emails.SendParams = {
        "from": email_from,
        "to": [email_to],
        "subject": subject,
        "text": body,
    }

    if html_body:
        params["html"] = html_body

    if resend_attachments:
        params["attachments"] = resend_attachments

    try:
        result = resend.Emails.send(params)

        print("RESEND RESULT:")
        print(result)

        return {
            "status": "success",
            "message": "Email sent successfully through Resend.",
            "email_id": result.get("id"),
        }

    except Exception as error:
        return {
            "status": "error",
            "message": str(error),
        }