# Phase 6 - AI Research Loop

## Goal
Introduce AI as a research assistant that continuously generates and evaluates hypotheses.

## AI may
- Analyze historical results
- Identify recurring failure modes
- Generate hypotheses
- Propose candidate strategies
- Suggest parameter ranges
- Analyze market regimes
- Explain experiment results
- Recommend experiments

## AI may not
- Directly modify historical results
- Bypass the backtester
- Bypass the risk engine
- Directly place real-money orders
- Decide its own evidence threshold after seeing results
- Automatically reset a dead experiment

## Research loop
1. Read experiment database.
2. Generate hypothesis.
3. Create versioned candidate.
4. Run deterministic experiment.
5. Validate.
6. Store all results.
7. Compare against prior work.
8. Decide candidate status using predefined rules.
9. Generate research notes.
10. Queue next experiment.

## Required audit trail
Store:
- Prompt/version
- Model identifier
- Inputs
- Hypothesis
- Generated strategy specification
- Experiment ID
- Results
- Decision
- Timestamp

The AI should not be able to alter past records.
