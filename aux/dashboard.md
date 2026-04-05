# Weedscore Dashboard UI/UX Specification (Ticket 2.4)

## Design Philosophy
* **Mobile-First:** Single-column layout, easily tappable.
* **State Management:** Use `st.session_state` for navigation (`current_page`). 
* **Widget Synchronization:** Use identical `st.session_state` keys (e.g., `key="is_solo"`, `key="is_special_occasion"`) for toggles that appear on multiple screens to ensure they remain perfectly synced without extra logic.
* **DRY Configuration:** UI input bounds (min/max values) MUST be read dynamically from the Pydantic `UserPreferences` model schema. Do not hardcode ranges in the UI.

## Screen 1: The Main Dashboard (Default)
* **Header:** Title with a "⚙️" icon button (top right) to access Settings.
* **The Score Display:** A large, central, stable visual element (e.g., styled `st.metric` or Plotly Donut).
    * **RAG Coloring:** 0-50 (Red), 50-75 (Amber), 75-100 (Green).
* **Live Toggles:** Positioned directly under the score.
    * Checkbox/Toggle: `Special Occasion?` (key="is_special_occasion")
    * Checkbox/Toggle: `Is Solo?` (key="is_solo")
    * *Note: Toggling these must immediately update the displayed score.*
* **Call to Action:** A prominent button below the toggles: **"Log New Session"** -> routes to Screen 2.

## Screen 2: Record Session
* **Header:** "Record Session" with a "🏠 Home" button.
* **Live Preview:** A dynamic metric: `Current Score -> Projected New Score`.
    * *Implementation Note:* Calculate the Projected Score by passing the DB sessions + a temporary, uncommitted `DBSession(timestamp=now, is_solo=st.session_state.is_solo)` to the calculator.
* **Live Toggles:** Exact same toggles and layout as Screen 1, using the identical session state keys to maintain visual continuity for the user.
* **Action:** "CONFIRM" button.
    * **Flow:** On click -> Write to DB -> Show `st.success("Session recorded successfully!")` -> Wait 1 second -> Return to Main Dashboard.

## Screen 3: Settings
* **Header:** "Configuration" with a "🏠 Home" button.
* **Inputs:** Read the `default`, `ge` (min), and `le` (max) values directly from `UserPreferences.model_fields` to populate these UI elements.
    * Number Input: `Target Frequency (N)`
    * Slider: `Recovery Patience`
    * Slider: `Bender Strictness`
* **Validation & Action:** "Update Settings" button.
    * **Flow:** Wrap the update in a `try...except ValidationError`. If validation fails, display an `st.error()` warning on screen. If successful, overwrite `config/preferences.json`, show a success message, and return to Screen 1.