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

    return escape(str(value)).replace("\n", "<br>")


@router.get("/test")
def test_email():
    return send_email(
        subject="AI Content OS Test Email",
        body="Email delivery is working successfully.",
    )


@router.get("/send-latest")
def send_latest_email():
    latest = get_latest_history_file()

    if latest is None:
        return {
            "status": "error",
            "message": "No history found. Generate content first.",
        }

    content = latest.get("content_package", {})

    if isinstance(content, str):
        try:
            content = json.loads(content)
        except json.JSONDecodeError:
            content = {}

    topic = str(
        latest.get("topic", "unknown")
    ).lower()

    pdf_path = create_package_pdf(latest)

    plain_body = f"""
AI CONTENT OS

Topic: {latest.get("topic", "")}
Source: {latest.get("source", "")}
Article: {latest.get("article_title", "")}

Editorial headline:
{content.get("editorial_headline", "")}

LinkedIn Option 1:
{content.get("linkedin_option_1", "")}

The complete content package is attached as a PDF.
"""

    html_body = f"""
<!DOCTYPE html>
<html>
<body style="
    margin:0;
    padding:24px;
    background:#F5F2EA;
    font-family:Arial, sans-serif;
    color:#171615;
">
  <div style="
      max-width:720px;
      margin:auto;
      background:#FFFDF8;
      border:1px solid #E7E1D8;
      border-radius:24px;
      padding:32px;
  ">

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
      Your latest editorial and social content package is ready.
    </p>

    <div style="
        background:#F8F6F1;
        border-radius:16px;
        padding:20px;
        margin:24px 0;
    ">
      <p>
        <strong>Topic:</strong>
        {safe_text(latest.get("topic", "")).upper()}
      </p>

      <p>
        <strong>Source:</strong>
        {safe_text(latest.get("source", ""))}
      </p>

      <p>
        <strong>Article:</strong>
        {safe_text(latest.get("article_title", ""))}
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
      The complete package is attached as a branded PDF.
    </p>

  </div>
</body>
</html>
"""

    return send_email(
        subject=(
            f"AI Content OS — "
            f"{topic.upper()} Package"
        ),
        body=plain_body,
        html_body=html_body,
        attachments=[pdf_path],
    )