# Phase 1 Prompt - Foundation

Implement Phase 1 only.

## Goal

Create the production-quality foundation for the AI Trading Research Lab without implementing AI strategy generation, broker integration, or real trading.

## Before coding

Inspect the entire repository.

Determine:
- language/framework;
- current folder structure;
- existing database setup;
- existing tests;
- configuration system;
- logging;
- deployment setup.

Do not make assumptions about the existing project.

## Build

Create/establish:
- clean project structure;
- environment/configuration management;
- typed domain models;
- database models/migrations;
- structured logging;
- system-state machine;
- wallet/account domain model;
- immutable event/audit model;
- strategy and experiment identifiers;
- test infrastructure.

## Required states

Support:
`INITIALIZING`
`PRE_MARKET`
`MARKET_OPEN`
`MARKET_CLOSING`
`MARKET_CLOSED`
`RESEARCH`
`DEAD`
`ERROR_SAFE`

`DEAD` is terminal.

## Wallet

Create a virtual wallet:
- starting balance: ₹1,000;
- initial maximum deployment: ₹500.

Do not implement real-money funds.

## Security boundaries

The future AI must be treated as an untrusted component.

Design interfaces so that AI code cannot:
- execute arbitrary SQL;
- execute shell commands;
- directly mutate wallet balance;
- change historical records;
- bypass risk controls.

## Tests

Write tests proving:
- initial wallet = ₹1,000;
- initial deployment limit = ₹500;
- invalid state transitions fail;
- DEAD is terminal;
- DEAD persists through restart simulation;
- historical records are append-only;
- wallet mutations happen through the accounting service only.

## Do not build yet

Do not implement:
- Groww API;
- real orders;
- AI strategy generation;
- autonomous learning;
- live market data;
- dynamic capital promotion;
- email reports.

## Completion report

Return:
- architecture created;
- files changed;
- tests added;
- test results;
- known limitations;
- exact command to run Phase 1 locally.
