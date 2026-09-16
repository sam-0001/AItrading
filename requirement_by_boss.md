# Requirements from Boss

The following requirements and APIs need to be provided by the boss (User) for the complete execution of the AI Trading Lab phases. 
**Note:** If any API or live data feed is not available, the system will use local simulated/mock data so that the work does not stop.

## Phase 4: Historical Data
- [ ] Source for historical OHLCV data for Indian equities.
- [ ] Any preferred data provider API (e.g., Yahoo Finance, Zerodha Kite Connect Historical API, Upstox API).

## Phase 6: AI Research Loop
- [ ] LLM API Key (e.g., OpenAI, Anthropic, or Gemini) to run the AI strategy generation.
- [ ] Access to embedding models if semantic search over documentation is required.

## Phase 8: Daily Reporting
- [ ] SMTP Server details or Email API (e.g., SendGrid, AWS SES) for daily risk and experiment death reports.

## Phase 10: Broker Paper Integration
- [ ] Sandbox/Paper trading API credentials (e.g., Angel One SmartAPI, Zerodha Kite Connect).
- [ ] API secret and keys for the broker.

*Please update this checklist and provide the necessary `.env` variables as the project progresses.*

## Phase 9 - VPS & Database
* **Production PostgreSQL DSN**: Required to migrate from SQLite to Postgres for the continuous VPS environment.
* **VPS Details**: Server access required to deploy using the provided `docker-compose.yml`.

## Phase 10 - Broker API
* **Angel One API Keys**: SmartAPI Client ID, Password, API Key, and TOTP setup required for real-time market data access (simulating in Paper mode right now).
* **Angel One Paper Access**: Need verification of their API capabilities in India for algo-trading to transition the mocked `AngelOnePaperAdapter` to the actual websocket/REST feeds.
