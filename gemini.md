# Weedscore Project Context

## 1. Project Overview
**Purpose:** A data-driven control system for cannabis regulation. 
**Objective:** Maintain a target frequency of ~30 sessions/year via a dynamic "deserve" metric (0-100).

## 2. Current Mission
**Goal:** Stabilize E2E tests and finalize Phase 3.
**Active Task:** Diagnose and fix failures in `tests/e2e/test_dashboard.py`.

## 3. Active Roadmap (Phase 3)
* **Ticket 3.1 [DONE]:** Comprehensive Test Coverage.
    - Updated `tests/test_engine.py` to use `UserPreferences`.
    - Fixed E2E test instability in `tests/e2e/test_dashboard.py`.
    - Corrected $C_i$ engine formula to ensure strictness works intuitively.
* **Ticket 3.2 [IN PROGRESS]:** UX Polish.
    - **Tooltip Refactor:** Update "Recovery Patience" and "Bender Strictness" tooltips to use non-technical language.
    - **UX Refactor:** Move "Is Solo?" toggle near the "Log New Session" button to distinguish it from "Global Lens" toggles.
    - Add Plotly visualizations for historical score trends.

## 4. Critical Reference Links
* **[Engine Spec](docs/specs/engine.md):** Mathematical formulas and calibration.
* **[Dashboard Spec](docs/specs/dashboard.md):** UI/UX requirements and state logic.
* **[Architecture Decisions](docs/DECISIONS.md):** "Why" we built it this way.
* **[Historical Archive](docs/ARCHIVE.md):** Completed tickets and milestones.

## 5. Development Standards
* **Environment:** Pixi (`pixi run ...`).
* **Database:** Neon (Postgres) via SQLAlchemy.
* **Testing:** Pytest + Playwright for E2E.
* **Validation:** All engine changes MUST be verified against `tests/test_engine.py`.
