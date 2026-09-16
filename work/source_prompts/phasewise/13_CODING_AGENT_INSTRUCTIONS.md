# Coding Agent Instructions

You are implementing an autonomous quantitative research and simulated trading laboratory.

## Non-negotiable
- Read all phase files before modifying code.
- Implement only the requested phase.
- Do not silently implement later phases.
- Do not connect real-money broker APIs unless explicitly requested and the relevant phase is active.
- Never bypass the risk engine.
- Never mutate historical trade/experiment records.
- Never reset or resurrect a DEAD experiment.
- Never invent market data.
- Never claim a strategy is profitable without reproducible calculations.
- Write automated tests for every safety-critical rule.

## Development process
1. Inspect the existing repository.
2. Identify current architecture and dependencies.
3. Propose changes before making broad structural changes.
4. Implement the smallest complete version of the active phase.
5. Add tests.
6. Run tests.
7. Check failure cases.
8. Document configuration and assumptions.
9. Report exactly what was implemented and what remains.

## Financial simulation
All P&L must use deterministic accounting.
Include transaction costs and slippage once the relevant engine supports them.
Never allow the AI/LLM to directly alter account balance.

## AI isolation
The AI is an untrusted research component.
It can propose data/strategy objects through a validated interface.
It cannot execute arbitrary Python, SQL, shell commands, or broker actions.

## DEAD state
If total virtual wallet <= ₹0:
- persist DEAD;
- cancel pending simulated orders;
- prevent new trades;
- prevent automatic reset;
- preserve all historical data;
- produce a final report.

Restarting the application must not revive DEAD.

## Quality
Prefer clear modules, typed interfaces, deterministic tests, structured logs, and reproducible experiments over a quick demo.
