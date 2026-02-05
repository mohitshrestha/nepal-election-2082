# pipeline.py

import asyncio
import datetime
from pathlib import Path

import pandas as pd

from src.fetch import fetch_raw_text
from src.parse import parse_json_with_ctzdist
from src.store import write_parquet
from src.validate import validate_entries

# Processed & raw data directories
PROCESSED_DIR = Path("data/processed")
RAW_DIR = Path("data/raw")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
RAW_DIR.mkdir(parents=True, exist_ok=True)


async def save_raw_text(raw_text: str, raw_dir: Path) -> Path:
    """Save the raw fetched text to a timestamped file in data/raw"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"election_raw_{timestamp}.txt"
    file_path = raw_dir / filename

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(raw_text)

    return file_path


def write_json(data: list[dict], path: Path):
    """Save validated data as JSON for browser-friendly access"""
    df = pd.DataFrame(data)
    if df.empty:
        raise ValueError("No data to write")
    df.to_json(path, orient="records", force_ascii=False, indent=2)


async def run():
    # 1️⃣ Fetch raw data
    raw = await fetch_raw_text()

    # 2️⃣ Save raw data
    raw_file_path = await save_raw_text(raw, RAW_DIR)
    print(f"Raw data saved to: {raw_file_path}")

    # 3️⃣ Parse JSON and handle CTZDIST
    parsed = parse_json_with_ctzdist(raw)

    # 4️⃣ Validate entries
    validated = validate_entries(parsed)

    # 5️⃣ Save processed data as Parquet
    parquet_path = PROCESSED_DIR / "election.parquet"
    write_parquet(validated, parquet_path)
    print(f"Processed data saved to: {parquet_path}")

    # 6️⃣ Save processed data as JSON for WASM/Marimo dashboard
    json_path = PROCESSED_DIR / "election.json"
    write_json(validated, json_path)
    print(f"Processed data saved as JSON: {json_path}")


if __name__ == "__main__":
    asyncio.run(run())
