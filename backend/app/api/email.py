import json
from html import escape

from fastapi import APIRouter

from app.services.email_service import send_email
from app.services.export_service import create_package_pdf
from app.services.history_service import get_latest_history_file


router = APIRouter()


def safe_text(value) -> str:
    if value is None:
        return ""

    if isinstance(value, list):
        return "<br>".join(
            f"• {escape(str(item))}"
            for item in value
        )

    return escape(str(value)).replace(
        "\n",
        "<br>",
    )


def send_package_email(package: dict):
    """
    Send one specific content package.

    This is used by the scheduler so the email always
    contains the exact package generated during that run.
    """

    if not package:
        return {
            "status": "error",
            "message": "No package supplied for email.",
        }

    if package.get("status") != "success":
        return {
            "status": "error",
            "message": (
                "The supplied package was not generated "
                "successfully, so no email was sent."
            ),
        }

    content = package.get(
        "content_package",
        {},
    )

    if isinstance(content, str):
        try:
            content = json.loads(content)
        except json.JSONDecodeError:
            return {
                "status": "error",
                "message": (
                    "Content package contains invalid JSON."
                ),
            }

    topic = str(
        package.get(
            "topic",
            "unknown",
        )
    ).lower()

    # IMPORTANT:
    # Build PDF from THIS exact package,
    # not from history/latest.
    pdf_path = create_package_pdf(
        package
    )

    plain_body = f"""
AI CONTENT OS

Topic: {package.get("topic", "")}
Source: {package.get("source", "")}
Article: {package.get("article_title", "")}

Editorial headline:
{content.get("editorial_headline", "")}

LinkedIn Option 1:
{content.get("linkedin_option_1", "")}

The complete content package generated during this run
is attached as a PDF.
"""

    html_body = f"""
<p style="
    font-size:12px;
    letter-spacing:3px;
    color:#8B8175;
    margin:0 0 12px;
">
  AI SOCIAL CONTENT STUDIO
</p>

<h1 style="
    font-family:Georgia, serif;
    font-size:42px;
    margin:0 0 12px;
">
  AI Content OS
</h1>

<p style="
    color:#6F675E;
    font-size:16px;
">
  Your newly generated editorial and social
  content package is ready.
</p>

<div style="
    background:#F8F6F1;
    border-radius:16px;
    padding:20px;
    margin:24px 0;
">
  <p>
    <strong>Topic:</strong>
    {safe_text(package.get("topic", "")).upper()}
  </p>

  <p>
    <strong>Source:</strong>
    {safe_text(package.get("source", ""))}
  </p>

  <p>
    <strong>Article:</strong>
    {safe_text(package.get("article_title", ""))}
  </p>
</div>

<h2 style="
    font-family:Georgia, serif;
    font-size:28px;
">
  {safe_text(
      content.get(
          "editorial_headline",
          "Latest Content Package",
      )
  )}
</h2>

<p style="
    font-size:16px;
    line-height:1.7;
    color:#5F574F;
">
  {safe_text(
      content.get(
          "editorial_subtitle",
          "",
      )
  )}
</p>

<hr style="
    border:none;
    border-top:1px solid #E7E1D8;
    margin:28px 0;
">

<h3>LinkedIn Option 1</h3>

<p style="line-height:1.7;">
  {safe_text(
      content.get(
          "linkedin_option_1",
          "",
      )
  )}
</p>

<p style="
    margin-top:30px;
    color:#8B8175;
    font-size:13px;
">
  This PDF was generated from the same package
  created during this email run.
</p>
"""

    return send_email(
        subject=(
            f"AI Content OS — "
            f"{topic.upper()} Package"
        ),
        body=plain_body,
        html_body=html_body,
        attachments=[
            pdf_path
        ],
    )


@router.get("/test")
def test_email():
    return send_email(
        subject="AI Content OS Test Email",
        body="Email delivery is working successfully.",
    )


@router.get("/send-latest")
def send_latest_email():
    """
    Manual endpoint only.

    Useful when the user explicitly wants to resend
    the most recently saved history package.
    """

    latest = get_latest_history_file()

    if latest is None:
        return {
            "status": "error",
            "message": (
                "No history found. "
                "Generate content first."
            ),
        }

    return send_package_email(
        latest
    )