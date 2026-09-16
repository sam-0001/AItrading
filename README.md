# AI Trading Lab

This repository currently implements **Phase 1: Foundation** only. It is a
simulation-only safety foundation; it has no market data, strategy execution,
AI integration, broker connectivity, or real-money capability.

## Run locally

```sh
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
cp .env.example .env
.venv/bin/python -m trading_lab.cli init
.venv/bin/python -m pytest
```

See `docs/` for the requirements map, architecture assessment, phase status,
and system rules.
