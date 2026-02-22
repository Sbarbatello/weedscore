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
* **Heat Multiplier:** $1 + (\text{current\_heat\_at\_session\_time} / 10)$.

### C. Frequency Debt ($D$)
The total debt is the sum of all sessions in a 365-day rolling window:
$$D = \sum (\text{BaseWeight} \times C_i \times \text{Heat\_Multiplier} \times \text{Solo\_Penalty} \times \text{Annual\_Decay})$$
* **BaseWeight:** 10.0
* **Solo Multiplier:** 1.5x session weight.
* **Annual Decay ($L$):** $1 - (\text{days\_since\_event} / 365)$.

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
* **Ticket 1.1 [ACTIVE]:** initialize the project structure as defined in the proposed structure:
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

