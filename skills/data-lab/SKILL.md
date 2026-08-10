---
name: data-lab
description: Profile, clean, analyze, visualize, and model tabular or scientific data with a reproducible notebook and explicit assumptions. Use for CSV, Parquet, Excel, JSON, SQL, statistical analysis, exploratory data analysis, experiment results, forecasting, and machine-learning comparisons.
---

# Data Lab

Make the analysis rerunnable and the conclusion auditable.

## Workflow

1. Preserve the raw input. Record file hashes, extraction filters, units, time zone, and observation grain.
2. Run `scripts/profile_table.py INPUT` for a first-pass schema and missingness report.
3. Define the question, target population, outcome, comparison, and leakage boundary before modeling.
4. Clean with explicit transformations. Track excluded rows and never silently coerce failed parses.
5. Use a notebook for exploration and a script or parameterized notebook for the final run. Seed stochastic operations.
6. Report effect sizes, uncertainty, sample size, and failure modes. Do not substitute a model score for a decision.
7. Save the environment, code, tables, and figures needed to reproduce the result.

Read `references/analysis-checklist.md` before causal claims, model comparisons, or time-series splits.

## Quality Gate

- Check duplicates, missingness patterns, units, outliers, and time leakage.
- Split data before fitting preprocessors.
- Compare against a simple baseline.
- Label exploratory findings as exploratory.
- Keep exact numbers in tables and use charts to show relationships.
