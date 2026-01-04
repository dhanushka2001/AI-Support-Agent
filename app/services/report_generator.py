from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from datetime import datetime
from pathlib import Path

REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def generate_report_pdf(conversation: dict, output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph(
        f"<b>{conversation.get('title', 'Conversation Report')}</b>",
        styles["Title"],
    ))
    story.append(Spacer(1, 12))

    # Metadata
    story.append(Paragraph(
        f"<b>Conversation ID:</b> {conversation['conversation_id']}",
        styles["Normal"],
    ))

    created_at = conversation.get("created_at")
    updated_at = conversation.get("updated_at")

    if created_at:
        story.append(Paragraph(
            f"<b>Created:</b> {created_at.strftime('%Y-%m-%d %H:%M:%S')}",
            styles["Normal"],
        ))

    if updated_at:
        story.append(Paragraph(
            f"<b>Last updated:</b> {updated_at.strftime('%Y-%m-%d %H:%M:%S')}",
            styles["Normal"],
        ))

    story.append(Spacer(1, 20))

    # Messages (Q&A)
    messages = conversation["messages"]

    for i in range(0, len(messages), 2):
        user_msg = messages[i]
        assistant_msg = messages[i + 1] if i + 1 < len(messages) else None

        story.append(Paragraph(
            f"<b>Q:</b> {user_msg['content']}",
            styles["Normal"],
        ))
        story.append(Spacer(1, 6))

        if assistant_msg:
            story.append(Paragraph(
                f"<b>A:</b> {assistant_msg['content']}",
                styles["Normal"],
            ))

        story.append(Spacer(1, 14))

    doc.build(story)

