
import json
import os

import openai
from jinja2 import Template


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


    # Load the Jinja2 template from file
    with open(os.path.join(os.path.dirname(__file__), "prompt_template_classify_account.jinja2")) as f:
        template_str = f.read()
    prompt_classify_account = Template(template_str)
    prompt = prompt_classify_account.render(notes=notes)

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
