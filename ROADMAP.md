# Weedscore Roadmap

## Last Status (2026-04-01)
- **Phase 2 COMPLETE** - Simulation & Engine
- Streamlit Dashboard fully functional with session logging and live previews
- Parameter optimization baked into mapping layer (C=183.3, k_sigmoid=0.5)
- System follows "NAI standard" pipeline: User Input → Pydantic Schema → Mapping Layer → Calculator

## Current Focus
- **Ticket 3.1: Test Coverage** (NEXT)

---

## Development Roadmap

### Phase 1: Scaffolding [DONE]
- Ticket 1.1 [DONE] - Project structure initialized
- Ticket 1.2 [DONE] - Database initialization with defaults

### Phase 2: Simulation & Engine [DONE]
- Ticket 2.1 [DONE] - Synthetic data seeder
- Ticket 2.2 [DONE] - Logic engine implementation
- Ticket 2.2b [DONE] - Validation & testing
- Ticket 2.3 [DONE] - Parameter optimization & calibration
- Ticket 2.4 [DONE] - Streamlit dashboard implementation

### Phase 3: Stabilization & Polish [IN PROGRESS]
- **Ticket 3.1 [TODO]:** Comprehensive Test Coverage
  - Goal: Update tests to use UserPreferences and cover new mapping logic
- **Ticket 3.2 [TODO]:** UX Polish
  - Goal: Add Plotly visualizations for historical score trends

---

## Completed Features
- Sigmoid recovery curve with configurable midpoint and steepness
- Heat accumulation model with dissipation tied to target frequency
- Cluster intensity penalties for back-to-back sessions
- Annual rolling decay (365-day window)
- Solo and special occasion multipliers
- Pydantic validation for user preferences
- RAG-coloured score display (0-50 Red, 50-75 Amber, 75-100 Green)
- Live projected score preview on session logging
- Stateless parameter mapping layer (N → K calibration)