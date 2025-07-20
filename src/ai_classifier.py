
import json
import os
import re

import openai
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader("src/prompts"))
template = env.get_template("classify_account.j2")


def openai_client():
    return openai.AsyncOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )


def build_prompt(bundle: dict) -> str:

    def strip_html(text):
        return re.sub(r'<[^>]+>', '', text)

    notes = "\n".join([
        strip_html(entry["resource"]["text"]["div"])
        for entry in bundle["entry"]
        if entry["resource"]["resourceType"] == "Communication"
    ])

    return template.render({"notes": notes})


async def classify_account(bundle: dict) -> tuple[str, str]:
    prompt = build_prompt(bundle)
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
