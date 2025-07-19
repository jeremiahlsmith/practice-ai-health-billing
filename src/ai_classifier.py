import json
import os

import openai


def openai_client():
    return openai.AsyncOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )


async def classify_account(bundle: dict) -> tuple[str, str]:

    # Extract only the essential text: the inner text from each Communication's div, stripped of HTML tags
    import re
    def strip_html(text):
        return re.sub(r'<[^>]+>', '', text)

    notes = "\n".join([
        strip_html(entry["resource"]["text"]["div"])
        for entry in bundle["entry"]
        if entry["resource"]["resourceType"] == "Communication"
    ])

    prompt = f"""
    You are a medical billing expert. Read the following patient communication notes and respond in the following structured JSON format:

    {{
      "category": "<One of: awaiting_guarantor, payer_pending_response, likely_writeoff, needs_manual_review>"
      "summary": "<Concise summary of the patient's billing situation in 1-2 sentences>",
    }}

    Choose the category that best fits the situation based on the notes. If unsure, use "needs_manual_review".

    Patient Communication Notes:
    {notes}
    """

    response = await openai_client().chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    output = response.choices[0].message.content

    if not output:
        return "No summary available", "needs_manual_review"

    try:
        data = json.loads(output)
        category = data.get("category", "needs_manual_review")
        summary = data.get("summary", "No summary available")
    except Exception:
        summary = "No summary available"
        category = "needs_manual_review"

    return category, summary
