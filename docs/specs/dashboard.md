# Weedscore Dashboard UI/UX Specification

## Design Philosophy
* **Mobile-First:** Single-column layout, easily tappable.
* **State Management:** Use `st.session_state` for navigation (`current_page`). 
* **Widget Synchronization:** Use identical `st.session_state` keys (e.g., `key="is_solo"`) for toggles across screens.
* **DRY Configuration:** UI input bounds MUST be read dynamically from the Pydantic `UserPreferences` model schema.

## Screen 1: The Main Dashboard
* **Score Display:** Large central visual with **RAG Coloring** (0-50 Red, 50-75 Amber, 75-100 Green).
* **Live Toggles:** `Special Occasion?` and `Is Solo?`. Toggling immediately updates the score.
* **CTA:** "Log New Session" button.

## Screen 2: Record Session
* **Live Preview:** Metric showing `Current Score -> Projected New Score`.
* **Action:** "CONFIRM" button writes to DB and returns to Main.

## Screen 3: Settings
* **Inputs:** `Target Frequency (N)`, `Recovery Patience`, `Bender Strictness`.
* **Validation:** Wrap updates in Pydantic validation; errors displayed via `st.error()`.
