---
name: debug-lab
description: Diagnose a crash, test failure, wrong result, performance regression, environment issue, or intermittent bug by reproducing it, tracing evidence to root cause, and verifying the smallest complete fix. Use when the user reports an error, failure, unexpected behavior, flaky test, or broken workflow and wants diagnosis or repair.
---

# Debug Lab

## Workflow

1. Capture the exact symptom, command, environment, inputs, expected result, and first bad version if known.
2. Reproduce with the smallest case that still fails. If reproduction is impossible, collect logs and state without guessing.
3. Trace backward from the failure. Separate observations from hypotheses and test one hypothesis at a time.
4. Identify the root cause and the conditions that activate it.
5. If a fix was requested, make the smallest complete change and add a regression test that fails without it.
6. Re-run the reproduction, nearby tests, and the appropriate broader suite.

## Report

Lead with root cause and evidence. Then give the fix, verification, and any residual uncertainty. Do not present a workaround as a root-cause fix.
