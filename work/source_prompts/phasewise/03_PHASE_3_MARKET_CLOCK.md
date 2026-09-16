# Phase 3 - Indian Market Clock

## Goal
Make the system understand Indian trading sessions automatically.

## Requirements
- Exchange calendar abstraction
- Weekends
- Exchange holidays
- Session open/close times
- Pre-market handling where relevant
- Market-closing state
- Timezone-safe timestamps
- Server clock validation

Do not rely on a single hard-coded time comparison.

## Architecture
`MarketCalendar` answers whether the market is:
- closed
- pre-market
- open
- closing
- holiday/weekend

## Safety
If market-session information is unavailable or inconsistent, enter a safe non-trading state.

## Tests
Include normal trading days, weekends, holidays, timezone boundaries, and restart during each state.
