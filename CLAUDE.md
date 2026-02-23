# CLAUDE.md — AI Assistant Guide

This file documents the codebase structure, development workflows, and conventions for AI assistants working in this repository.

## Project Overview

**AI Health Billing** is a Python practice project that:
- Reads simulated FHIR Communication bundles from a JSON dataset
- Extracts plain-text patient communication notes from each bundle
- Sends those notes to OpenAI GPT-4 via a Jinja2-rendered prompt
- Returns a structured classification and summary for each patient billing account

This is a learning/experimental project. No real patient data is used.

## Repository Structure

```
practice-ai-health-billing/
├── .mise.toml                     # Tool version management (uv + Python 3.12)
├── .python-version                # Pin Python to 3.12
├── .gitignore
├── pyproject.toml                 # Project metadata and dependencies
├── uv.lock                        # Locked dependency versions
├── README.md                      # User-facing setup instructions
├── CLAUDE.md                      # This file
└── src/
    ├── main.py                    # Async entry point; batch-processes FHIR bundles
    ├── ai_classifier.py           # OpenAI client, prompt builder, and classify_account()
    ├── fake_fhir_bundle.json      # Single FHIR bundle example (currently empty)
    ├── fake_fhir_bundles.json     # Dataset: 10 simulated FHIR Communication bundles
    ├── prompt_template.jinja2     # Legacy empty template file (not used)
    └── prompts/
        └── classify_account.j2   # Active Jinja2 prompt template
```

## Key Files

### `src/main.py`
- Entry point; run with `uv run python src/main.py`
- Loads `.env`, reads `src/fake_fhir_bundles.json`, and calls `classify_account()` on each bundle
- Uses `asyncio.gather` for concurrent batch processing; batch size is configurable via `CLASSIFY_ACCOUNT_BATCH_SIZE` (default: 3)
- Handles per-task exceptions gracefully without aborting the batch

### `src/ai_classifier.py`
- `openai_client()` — instantiates `openai.AsyncOpenAI` using `OPENAI_API_KEY`
- `build_prompt(bundle)` — extracts `Communication` resources from the bundle, strips HTML tags from `text.div`, joins notes into a string, and renders `classify_account.j2`
- `classify_account(bundle)` — sends the prompt to `gpt-4`, parses the JSON response, and returns `(category, summary)`; falls back to `("needs_manual_review", "No summary available")` on any parse failure

### `src/prompts/classify_account.j2`
- Jinja2 template loaded via `FileSystemLoader("src/prompts")`
- Instructs the model to act as a medical billing expert and return a JSON object
- Template variable: `{{ notes }}` (plain-text communication notes)

### `src/fake_fhir_bundles.json`
- Array of FHIR `Bundle` objects (type: `collection`)
- Each bundle contains one or more `Communication` entries with an HTML `text.div` field
- Add new bundles here to test additional scenarios

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `OPENAI_API_KEY` | Yes | — | OpenAI API key for GPT-4 calls |
| `CLASSIFY_ACCOUNT_BATCH_SIZE` | No | `3` | Number of bundles processed concurrently per batch |

Store these in a `.env` file at the project root (already in `.gitignore`).

## Setup and Development

### Prerequisites
- [mise](https://mise.jdx.dev) — polyglot tool manager (manages uv and Python)

### First-time setup
```sh
curl https://mise.run | sh   # install mise
mise install                  # install uv and Python 3.12 per .mise.toml
uv sync                       # install Python dependencies
cp .env.example .env          # then add OPENAI_API_KEY (no .env.example exists yet; create manually)
```

### Running the project
```sh
uv run python src/main.py
```

Output prints each bundle's classification category and summary to stdout.

### Adding dependencies
```sh
uv add <package>   # updates pyproject.toml and uv.lock
```

## AI Classification Schema

The prompt instructs GPT-4 to respond with valid JSON:

```json
{
  "category": "awaiting_guarantor | payer_pending_response | likely_writeoff | needs_manual_review",
  "summary": "1-2 sentence concise summary"
}
```

`ai_classifier.py:classify_account()` returns `(category, summary)` as a Python tuple.

## FHIR Bundle Format

Each entry in `fake_fhir_bundles.json` follows this shape:

```json
{
  "resourceType": "Bundle",
  "type": "collection",
  "entry": [
    {
      "resource": {
        "resourceType": "Communication",
        "id": "comm1",
        "text": {
          "status": "generated",
          "div": "<div>HTML content of communication note</div>"
        }
      }
    }
  ]
}
```

Only resources with `resourceType == "Communication"` are extracted; HTML is stripped before the text is sent to the model.

## Code Conventions

- **Python 3.12+** — use modern type hint syntax (e.g., `tuple[str, str]`, not `Tuple`)
- **Async-first** — all OpenAI calls are async; use `asyncio.gather` for concurrency
- **Jinja2 templates** — prompts live in `src/prompts/` with `.j2` extension; load via `FileSystemLoader("src/prompts")`
- **dotenv** — `load_dotenv()` is called once at the top of `main.py`; access env vars via `os.environ.get()`
- **No tests** — this is a practice project; no testing framework is configured

## Extending the Project

- **New FHIR bundles**: Append entries to `src/fake_fhir_bundles.json`
- **New prompt**: Add a `.j2` file to `src/prompts/`, load it with `env.get_template()`
- **New classification categories**: Update both the template (`classify_account.j2`) and downstream consumers
- **Different model**: Change the `model=` argument in `ai_classifier.py:classify_account()`
- **Web API**: The classifier is model-agnostic and easy to wrap in FastAPI or similar frameworks

## Notes for AI Assistants

- The project uses `uv` for dependency management — do not use `pip` directly
- `src/prompt_template.jinja2` is an empty legacy file; the active template is `src/prompts/classify_account.j2`
- `src/fake_fhir_bundle.json` (singular) is empty; the working dataset is `src/fake_fhir_bundles.json` (plural)
- Run scripts from the **project root**, not from inside `src/`, because `main.py` opens `src/fake_fhir_bundles.json` relative to the working directory and `ai_classifier.py` loads templates from `src/prompts`
- There is no linter or formatter configured; maintain consistency with existing style
