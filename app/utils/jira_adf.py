"""Build Atlassian Document Format (ADF) for Jira Cloud REST API v3."""

from __future__ import annotations


def plain_text_to_adf(text: str) -> dict:
    """Convert plain text (with newlines) to minimal ADF document."""
    body = (text or "").strip() or "(empty)"
    paragraphs = []
    for block in body.split("\n\n"):
        lines = block.split("\n")
        content = []
        for i, line in enumerate(lines):
            if line:
                content.append({"type": "text", "text": line})
            if i < len(lines) - 1:
                content.append({"type": "hardBreak"})
        if not content:
            content = [{"type": "text", "text": " "}]
        paragraphs.append(
            {"type": "paragraph", "content": content},
        )
    if not paragraphs:
        paragraphs = [
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": body}],
            },
        ]
    return {
        "type": "doc",
        "version": 1,
        "content": paragraphs,
    }
