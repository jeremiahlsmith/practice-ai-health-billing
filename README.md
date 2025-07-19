# AI Health Billing Practice Project

## Project Goal
This project is designed for hands-on practice with:
- Extracting and processing FHIR Communication bundles
- Using OpenAI's GPT models to summarize and classify patient billing scenarios
- Efficient, cost-aware prompt engineering and parallel processing

The main objective is to automate the classification of patient billing accounts based on real-world communication notes, using only the essential information for each case.

## How to Run


1. **Install [mise](https://mise.jdx.dev) (cross-platform tool manager, drop-in replacement for asdf)**
   - macOS/Linux/Windows:
     ```sh
     curl https://mise.run | sh
     # or see https://mise.jdx.dev/docs/install for other options
     ```
   - The included `.mise.toml` and `.tool-versions` files ensure everyone uses the same version of `uv`.
   - In the project directory, run:
     ```sh
     mise install
     ```

2. **Install dependencies with uv**
   ```sh
   uv sync
   ```

4. **Set your OpenAI API key**
   - Create a `.env` file in the project root with:
     ```
     OPENAI_API_KEY=your-openai-api-key
     CLASSIFY_ACCOUNT_BATCH_SIZE=batch-size (defaults to 3)
     ```

5. **Run the main script**
   ```sh
   uv run python src/main.py
   ```
   This will process all example FHIR bundles in parallel batches and print the AI's classification and summary for each.

## Practice Focus
- Minimal, cost-effective prompts: Only the text from FHIR Communication notes is sent to the AI.
- Robust async batching: Bundles are processed in parallel, in batches, with error handling for real-world reliability.
- Easy to extend: Add your own FHIR bundles to `src/fake_fhir_bundles.json` to test more scenarios.

---
This project is for experimentation and learning. No real patient data is used.
