# Weedscore Project Context

## 1. Project Overview
**Purpose:** A data-driven control system for cannabis (vaporiser) regulation. 
**Objective:** Maintain a target frequency of ~30 sessions per year by providing a dynamic "deserve" metric ($W$) ranging from 0 to 100.

## 2. Mathematical Specification (Immutable)
Defined in `aux/weedscore_calcs.md`

## 3. Tech Stack
* **Environment:** Pixi (refer to `pixi.toml`).
* **Database:** Neon (Serverless Postgres) using SQLAlchemy for ORM.
* **Frontend:** Streamlit for the dashboard and weight-tuning.
* **Language Standards:** Python 3.11+, Type Hints, PEP 8, and modular design.

## 4. Testing Requirements
* **Framework:** `pytest`.
* **Logic Validation:** Every calculation in the `calculator.py` engine must have a corresponding unit test that validates the score against manual "golden" values.

## 5. Development Roadmap
### Phase 1: Scaffolding
* **Ticket 1.1 [DONE] (2026-02-23):** initialize the project structure as defined in the proposed structure:
weedscore/
├── .env                 # Secret DB credentials (NEON_URL)
├── gemini.md            # The "Source of Truth"
├── pixi.toml            # Environment & Dependency management
├── README.md            # High-level overview
├── src/
│   ├── __init__.py
│   ├── engine/          # Ticket 2.2 logic
│   │   ├── __init__.py
│   │   └── calculator.py
│   ├── database/        # Ticket 2.1 logic
│   │   ├── __init__.py
│   │   ├── models.py
│   │   └── connection.py
│   └── dashboard/       # Ticket 2.3 logic
│       ├── __init__.py
│       └── app.py
├── tests/               # Unit tests (Ticket 2.2)
│   ├── __init__.py
│   └── test_engine.py
└── scripts/             # One-off scripts
    └── seed_db.py       # Data injection script

* **Ticket 1.2 [DONE] (2026-02-28):** Database Initialisation:
Update src/database/models.py: Ensure the is_solo and is_special_occasion columns have default=False in their definitions.

Create scripts/create_tables.py: This script must:

Import Base from models.py and get_engine from connection.py.

Use Base.metadata.create_all(engine) to physically create the sessions table in the Neon database.

Include a try/except block to catch connection errors and print 'Table created successfully!' on success.

Command: Provide the exact pixi command to execute this script.

### Phase 2: Simulation & Engine
* **Ticket 2.1 [DONE] (2026-03-29):** Synthetic Data Seeder (`scripts/seed_db.py`)
    - **Purpose:** Create a reproducible 'sandpit' environment to validate mathematical logic against diverse user behaviours.
    - **Scenarios (Temporal Logic):** 1. **The Moderator:** 4 sessions spaced exactly 14 days apart.
        2. **The Bender:** 4 sessions within a 72-hour window.
        3. **The Sabbatical:** 1 session exactly 45 days ago.
    - **Outcome:** Script supports isolation via `--scenario` and ensures a clean DB state via `TRUNCATE`.

* **Ticket 2.2 [DONE] (2026-03-29):** Logic Engine Implementation (`src/engine/calculator.py`).
    - **Purpose:** Core mathematical engine for Weedscore.
    - **Outcome:** Implemented `WeedScoreCalculator` using the specification from `aux/weedscore_calcs.md`. Includes Heat integration, Cluster Intensity, and Sigmoid Recovery.
    - **Validation:** Added a CLI entry point to verify score calculation against live DB data.

* **Ticket 2.2b [DONE] (2026-03-29):** Validation & Testing (`tests/test_engine.py`)
    - **Purpose:** Empirically verify the mathematical engine against high-signal scenarios.
    - **Seeds Updated:**
        - **The Moderator:** 4 sessions, spaced 12 days apart, most recent 21 days ago.
        - **The Sabbatical:** 1 session 60 days ago.
        - **The Clean Slate:** 0 sessions (ceiling test).
    - **Outcomes:** 
        - Fixed Heat Multiplier formula to $1 + H/10$ as per spec.
        - Tuned `SENSITIVITY_K` to **1000.0** to allow for more nuanced recovery for moderate users.
    - **Tests:**
        - Midpoint Sigmoid Check (R(14)=50).
        - Clean Slate Check (W=100.0).
        - Moderator Sensitivity Evaluation (W > 50.0 after 21 days).

* **Ticket 2.3 [ACTIVE]: Parameter Optimization & Calibration**
    - **Goal:** Find the mapping $N \rightarrow K$ using Grid Search.
    - **Key Fixes:** 1. Implement **Heat Clamping** (Max 5.0x) to prevent calculation stalls.
        2. Link **Heat Dissipation** to $N$ to maintain "Natural Balance."
        3. Use **Stateless Simulation** (in-memory lists) to avoid DB pollution during loops.
    - **Search Space:** $K \in [500, 10000]$, $P \in [1.0, 3.0]$.

* **Ticket 2.3 [DONE] (2026-03-29):** Parameter Optimization & Calibration
    - **Purpose:** Find the mathematical "sweet spot" for different target frequencies (N).
    - **Outcome:** Refactored `calculator.py` to be fully injectable. Built `scripts/optimize_params.py` for grid search.
    - **Calibration Findings:**
        - **K_SIGMOID:** Lowered to **0.2** for a smoother, more realistic recovery curve.
        - **T_THRESHOLD:** Reduced to **3.5 days** to prevent debt explosion in moderate users.
        - **K Equation:** Recommended $K \approx 500 \times N$ to keep scores normalized across goals.
        - **Heat Cap:** Implemented a $5.0x$ cap on the heat multiplier to prevent total score lockout.

## Last Status (2026-03-29)
- Completed Ticket 2.3.
- Refined the mathematical engine defaults based on grid search over 20, 30, and 50 sessions/year scenarios.
- Verified that the "Perfect Moderator" scenario now recovers to ~85.0 after a recovery window.
- Next Step: Ticket 2.4 (Streamlit Dashboard Implementation).

-----------------------------------
-----------------------------------

Things I've learned in this project:

  Summary of Best Practices for working with DBs:
   1. Tables: Keep them as Classes in models.py.
   2. Logic: Use the Session (the db object in our code) to read/write. It handles the "Commit" and "Close" for you.
   3. Complex SQL: If it's too hard for SQLAlchemy (like a 50-line recursive CTE), just use db.execute(text("YOUR RAW SQL")). SQLAlchemy
      doesn't stop you from using raw SQL; it just makes the easy stuff even easier.
