# Phase 12 Prompt - Autonomous Research Paper Pipeline

Implement Phase 12 only.

## Goal

Create an automated research-publication pipeline that can identify sufficiently validated findings and produce a reproducible paper draft.

## Important distinction

Trading profit is not automatically a scientific contribution.

The system must evaluate whether a research finding is:
- clearly defined;
- reproducible;
- tested out of sample;
- robust;
- properly benchmarked;
- statistically analysed;
- accompanied by limitations.

## Evidence gate

Publication criteria must be defined BEFORE the candidate is evaluated.

Store the criteria version with the experiment.

Potential evidence:
- adequate sample;
- out-of-sample period;
- walk-forward validation;
- parameter robustness;
- cost/slippage sensitivity;
- benchmark comparison;
- statistical tests;
- reproducibility.

Do not let the AI change thresholds after seeing results.

## Paper generation

Generate:
- title;
- abstract;
- introduction;
- hypothesis;
- methodology;
- dataset description;
- experiment design;
- results;
- statistical analysis;
- figures;
- tables;
- limitations;
- reproducibility information;
- references.

Every numerical claim must be traceable to stored experiment outputs.

## Integrity

Never fabricate:
- data;
- citations;
- results;
- significance;
- experiments.

## Human review

The system may automatically prepare the paper, but final scientific claims and submission require human review.

## Publication

Do not automatically submit to a journal or repository unless a later phase explicitly implements and authorizes that integration after reviewing the destination's current policies.

## Tests

Verify:
- every result has a source experiment;
- numbers in the paper match database values;
- failed candidates are not silently omitted from internal history;
- unsupported claims are flagged;
- missing evidence prevents publication status.
