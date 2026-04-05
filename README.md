# Weedscore

A data-driven control system for cannabis (vaporiser) regulation.

## Overview

This project provides a dynamic "deserve" metric ($W$) ranging from 0 to 100 to help maintain a target frequency of cannabis use (defaulting to ~30 sessions per year). It uses a hybrid mathematical model involving:
- **Sigmoid Recovery:** A recency-based refractory period.
- **Frequency Debt:** A rolling 365-day integration of historical sessions.
- **Clustering Penalties:** Non-linear penalties for back-to-back sessions (streaks).
- **Systemic Heat:** An integrator that punishes high volume and duration.

## Tech Stack

- **Environment:** [Pixi](https://pixi.sh/)
- **Database:** Neon (Serverless Postgres) with SQLAlchemy
- **UI:** Streamlit
- **Logic:** Python 3.11 with Pydantic validation

## Project Structure

- `src/`: Main source code
  - `engine/`: Core calculation logic and parameter mapping
  - `database/`: Database models and connection singleton
  - `dashboard/`: Streamlit UI and configuration management
- `tests/`: Unit tests (pytest)
- `scripts/`: Validation and database utility scripts

## Getting Started

1.  **Install Pixi:**
    Follow instructions at [pixi.sh](https://pixi.sh/).

2.  **Install dependencies:**
    ```bash
    pixi install
    ```

3.  **Set up environment variables:**
    Create a `.env` file in the root directory and add your Neon Postgres URL:
    ```bash
    NEON_URL="postgresql://user:password@host/dbname"
    ```

4.  **Initialize the Database:**
    ```bash
    pixi run create_db
    ```

5.  **Run the Dashboard:**
    ```bash
    pixi run dev
    ```

## Development Tasks

- `pixi run dev`: Starts the Streamlit dashboard.
- `pixi run test`: Runs the test suite.
- `pixi run seed`: Injects synthetic scenario data into the DB for testing.
- `pixi run create_db`: Creates the necessary database tables.
- `pixi run test_db`: Verifies the database connection.
- `PYTHONPATH=. pixi run python scripts/verify_scenarios.py`: Runs the mathematical verification suite.
