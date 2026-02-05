# MerchAI (NOBE)

MerchAI is a Generative Engine Optimization (GEO) and Brand Visibility Tracking platform designed to measure and improve how often a brand is recommended by AI answer engines.

## What we are building
1. Share of Voice Tracking
   - Run a set of queries against answer engines
   - Extract brand and entity mentions from responses
   - Compute visibility metrics over time

2. GEO Service Workflow
   - Entity optimization inputs (knowledge graph and structured data guidance)
   - Content engineering outputs (recommendation oriented content improvements)
   - Paid amplification exploration (Perplexity Sponsored Questions)

## Repo principles
- Zero setup: If it does not work in Docker, it does not exist.
- Steel thread MVP first: End to end working slice before expanding features.
- PR only: No direct pushes to main.

## Quick start
1. Create a local env file
   - Copy `.env.example` to `.env`
2. Build and start the dev container
   - `docker compose up -d --build`
3. Run quality checks
   - `docker compose exec app ruff check .`
   - `docker compose exec app mypy .`
   - `docker compose exec app pytest -q`

## Structure
- `src/` application code
- `tests/` tests
- `.github/workflows/ci.yml` CI checks for lint, typecheck, tests
- `.devcontainer/` dev container config
