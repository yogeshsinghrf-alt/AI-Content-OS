import mimetypes
import os
import smtplib
from email.message import EmailMessage
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def send_email(
    subject: str,
    body: str,
    html_body: str | None = None,
    attachments: list[str] | None = None,
):
    email_user = os.getenv("EMAIL_USER")
    email_password = os.getenv("EMAIL_PASSWORD")
    email_to = os.getenv("EMAIL_TO")

    if not email_user or not email_password or not email_to:
        return {
            "status": "error",
            "message": "Email settings are missing in backend/.env",
        }

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = email_user
    message["To"] = email_to
    message.set_content(body)

    if html_body:
        message.add_alternative(html_body, subtype="html")

    for attachment_path in attachments or []:
        path = Path(attachment_path)

        if not path.exists():
            continue

        mime_type, _ = mimetypes.guess_type(path.name)

        if mime_type:
            main_type, sub_type = mime_type.split("/", 1)
        else:
            main_type, sub_type = "application", "octet-stream"

        with path.open("rb") as file:
            message.add_attachment(
                file.read(),
                maintype=main_type,
                subtype=sub_type,
                filename=path.name,
            )

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(email_user, email_password)
            smtp.send_message(message)

        return {
            "status": "success",
            "message": "Email sent successfully",
        }

    except Exception as error:
        return {
            "status": "error",
            "message": str(error),
        }