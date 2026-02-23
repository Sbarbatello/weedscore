# Weedscore

A data-driven control system for cannabis (vaporiser) regulation.

## Overview

This project aims to maintain a target frequency of ~30 sessions per year by providing a dynamic "deserve" metric ($W$) ranging from 0 to 100.

## Project Structure

- `src/`: Main source code
  - `engine/`: Core calculation logic
  - `database/`: Database models and connection handling
  - `dashboard/`: Streamlit application
- `tests/`: Unit tests
- `scripts/`: One-off scripts

## Getting Started

1.  **Install dependencies:**
    ```bash
    pixi install
    ```
2.  **Set up environment variables:**
    Copy `.env.example` to `.env` and fill in your `NEON_URL`.
3.  **Run the dashboard:**
    ```bash
    pixi run start
    ```
