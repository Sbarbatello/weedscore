# Weedscore

## Commands
- `pixi run dev` - Start Streamlit dashboard (http://localhost:8501)
- `pixi run test` - Run unit tests (PYTHONPATH=. pytest tests/)
- `pixi run e2e` - Run E2E tests (requires dev server running)
- `pixi run seed` - Seed synthetic scenario data
- `pixi run create_db` - Create database tables
- `pixi run test_db` - Test database connection
- `PYTHONPATH=. pixi run python scripts/verify_scenarios.py` - Run mathematical verification

## Architecture
- `src/engine/` - Calculation logic and parameter mapping
- `src/database/` - SQLAlchemy models and connection singleton
- `src/dashboard/` - Streamlit UI
- `tests/` - Unit tests
- `tests/e2e/` - Playwright E2E tests
- `scripts/` - Database utilities
- `aux/weedscore_calcs.md` - Source of truth for math formulas
- `aux/dashboard.md` - Source of truth for Streamlit UI/UX

## Critical Setup
- Requires `.env` with `NEON_URL` (copy from `.env.example`)
- `PYTHONPATH=.` is required for all Python commands (not set in shell)
- `PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python` required for streamlit dev
- Database tests require live Postgres connection (Neon)

## Strict Coding Standards
- **Tables = Classes:** Define all DB tables as classes in `src/database/models.py`
- **Use Session:** Use the SQLAlchemy Session object for read/write. It handles commits/closures.
- **Complex SQL:** Use `db.execute(text("RAW SQL"))` for queries difficult to express in ORM.

## Testing Standards
- Every calculator formula must have a corresponding unit test validating against golden values
- Use CSV files in `tests/data/` for isolated calculation validation
- E2E tests require dev server running at localhost:8501

## Communication
- Act as a Senior Data Engineer peer
- Use British English