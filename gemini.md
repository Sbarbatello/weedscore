# Weedscore Project Context

## 1. Project Overview
**Purpose:** A data-driven control system for cannabis (vaporiser) regulation. 
**Objective:** Maintain a target frequency of ~30 sessions per year by providing a dynamic "deserve" metric ($W$) ranging from 0 to 100.

## 2. Mathematical Specification (Immutable)
The following formulas are the "source of truth." Do not deviate from these logic implementations:

### A. Short-Term Recovery ($R$)
$$R(t) = \frac{100}{1 + e^{-0.5(t - 14)}}$$
* **$t$**: Days since last session.
* **$t_0 = 14$**: Midpoint of recovery.
* **$k = 0.5$**: Growth steepness.

### B. Clustering & Heat Logic
* **Cluster Intensity ($C_i$):** $1 + \max(0, \frac{7 - IAT}{7})^2$ (where $IAT$ is days since previous session).
* **Heat Pool ($H$):** Each session adds $+10$ units. Dissipates at $-1$ unit per day.
* **Heat Multiplier:** $1 + (\text{current heat at session time} / 10)$

### C. Frequency Debt ($D$)
The total debt is the sum of all sessions in a 365-day rolling window:
$$D = \sum (\text{BaseWeight} \times C_i \times \text{HeatMultiplier} \times \text{SoloMultiplier} \times \text{AnnualDecay})$$
* **BaseWeight:** 10.0
* **Solo Multiplier:** 1.5x session weight.
* **Annual Decay ($L$):** $1 - (\text{days since event} / 365)$

### D. Final Metric ($W$)
$$W = \text{round}\left(\frac{R(t)}{1 + D}, 2\right)$$
* **Occasion Boost:** If toggled, $W = W \times 1.5$ (capped at 100).

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

## Current Status (2026-02-28)
- Completed Ticket 1.2.
- Updated `src/database/models.py` with `default=False`.
- Created `scripts/create_tables.py`.
- Next Step: Verify table creation in Neon and start Ticket 1.3 (Data Ingestion).

-----------------------------------
-----------------------------------

Things I've learned in this project:

  Summary of Best Practices for working with DBs:
   1. Tables: Keep them as Classes in models.py.
   2. Logic: Use the Session (the db object in our code) to read/write. It handles the "Commit" and "Close" for you.
   3. Complex SQL: If it's too hard for SQLAlchemy (like a 50-line recursive CTE), just use db.execute(text("YOUR RAW SQL")). SQLAlchemy
      doesn't stop you from using raw SQL; it just makes the easy stuff even easier.
