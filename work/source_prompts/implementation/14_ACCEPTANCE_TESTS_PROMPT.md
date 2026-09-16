# Final Acceptance Prompt - Full System

Run this only after all previous phases are implemented.

## Goal

Audit the complete system end-to-end.

## Scenario A - Profitable learning

Start with:
- wallet ₹1,000;
- maximum deployment ₹500.

Run simulated trades.

Verify:
- profits increase wallet;
- permitted exposure increases only according to configured rules;
- every trade is logged;
- research records are created.

## Scenario B - Losing system

Run a deterministic losing strategy.

Verify:
- wallet decreases;
- exposure is reduced according to rules;
- no negative accounting bug is hidden;
- at ₹0 or below the system becomes DEAD.

## Scenario C - Restart after death

Restart all services.

Verify:
- state remains DEAD;
- no trade is executed;
- no wallet reset occurs;
- no AI process can resurrect it.

## Scenario D - Market closed

Set a closed-market test timestamp.

Verify:
- no market trading occurs;
- research jobs may run;
- daily report can run.

## Scenario E - Data failure

Simulate unavailable/corrupt market data.

Verify:
- system fails closed;
- no invented data is used;
- incident is logged.

## Scenario F - AI failure

Make the AI service unavailable.

Verify:
- deterministic simulator/risk/accounting remain safe;
- no corrupted wallet;
- no unauthorized execution.

## Scenario G - AI malicious output

Return an AI response attempting to:
- execute an order;
- change balance;
- modify DEAD;
- execute shell code.

Verify all attempts are rejected.

## Scenario H - Reproducibility

Run the same experiment twice with:
- same dataset;
- same strategy version;
- same parameters;
- same cost assumptions.

Verify identical deterministic results.

## Scenario I - Research integrity

Verify:
- all experiments are recorded;
- failed experiments remain;
- dataset versions are stored;
- train/test boundaries are preserved;
- paper claims map to experiment outputs.

## Final report

Provide:
- test count;
- passed;
- failed;
- skipped;
- known risks;
- unresolved issues;
- deployment recommendation.

Do not describe the system as profitable merely because simulation tests pass.
