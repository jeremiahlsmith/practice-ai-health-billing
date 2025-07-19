import asyncio
import json
import os

from dotenv import load_dotenv

from ai_classifier import classify_account

load_dotenv()


async def main():
    with open('src/fake_fhir_bundles.json', 'r') as f:
        bundles = json.load(f)

    batch_size = int(os.getenv("CLASSIFY_ACCOUNT_BATCH_SIZE", 3))

    total = len(bundles)
    results = []
    start_index = 1
    for start in range(0, total, batch_size):
        batch = bundles[start:start+batch_size]
        tasks = [classify_account(bundle) for bundle in batch]
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        results.extend(batch_results)

        for i, result in enumerate(batch_results, start_index):
            print(f"\n--- Bundle {i} ---")
            if isinstance(result, Exception):
                print(f"Error: {result}")
            elif isinstance(result, tuple) and len(result) == 2:
                category, summary = result
                print(f"Category: {category}\nSummary: {summary}")
            else:
                print(f"Unexpected result: {result}")

            start_index += 1


if __name__ == "__main__":
    asyncio.run(main())

