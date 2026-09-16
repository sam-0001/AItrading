# Phase 12 - Autonomous Research-Paper Pipeline

## Goal
Automatically turn sufficiently validated research findings into a reproducible paper draft.

## Evidence gate
Define publication criteria before evaluating a result.

Potential criteria:
- Adequate historical sample
- Out-of-sample evidence
- Walk-forward validation
- Robustness tests
- Realistic costs/slippage
- Benchmark comparison
- Statistical analysis
- Reproducibility

The exact thresholds must be specified in the research protocol before the system uses them.

## Pipeline
Strategy/experiment
-> Evidence evaluator
-> Reproducibility check
-> Statistical analysis
-> Figures/tables
-> Manuscript draft
-> Citation check
-> Human review
-> Submission decision

## AI role
AI may prepare:
- Abstract
- Introduction
- Methodology draft
- Results narrative
- Figures/tables descriptions
- Limitations
- Reproducibility notes

## Human gate
A human must review and approve scientific claims and any submission.

The system must never fabricate data, citations, statistical significance, or results.

## Required artifacts
Every paper must link to:
- Dataset versions
- Code versions
- Experiment IDs
- Strategy versions
- Statistical outputs
- Limitations
