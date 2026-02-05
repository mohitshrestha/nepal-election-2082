# store.py

import pandas as pd


def write_parquet(data: list[dict], path: str):
    df = pd.DataFrame(data)
    if df.empty:
        raise ValueError("No data to write")

    df.to_parquet(
        path,
        index=False,
        compression="zstd",
    )
