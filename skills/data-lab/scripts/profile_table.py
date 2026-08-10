#!/usr/bin/env python3

import argparse
import json
from pathlib import Path

import pandas as pd


def load_table(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix in {".parquet", ".pq"}:
        return pd.read_parquet(path)
    if suffix in {".xlsx", ".xlsm", ".xls"}:
        return pd.read_excel(path)
    if suffix in {".json", ".jsonl"}:
        return pd.read_json(path, lines=suffix == ".jsonl")
    raise ValueError(f"unsupported table format: {suffix}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a compact JSON profile for a table.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    frame = load_table(args.input)
    report = {
        "path": str(args.input),
        "rows": len(frame),
        "columns": len(frame.columns),
        "duplicate_rows": int(frame.duplicated().sum()),
        "fields": {
            str(column): {
                "dtype": str(frame[column].dtype),
                "missing": int(frame[column].isna().sum()),
                "unique": int(frame[column].nunique(dropna=True)),
            }
            for column in frame.columns
        },
    }
    payload = json.dumps(report, indent=2)
    if args.output:
        args.output.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
