# Architectural Decisions & Lessons Learned

## Database Best Practices
1. **Models as Truth:** Keep tables defined as Classes in `models.py`.
2. **Session Lifecycle:** Use SQLAlchemy Sessions to handle Commit/Close automatically.
3. **Raw SQL escape hatch:** Use `db.execute(text(...))` for complex queries that SQLAlchemy struggles with.

## Engine & Mapping
1. **Singleton Engine:** Implemented in `connection.py` for efficient connection pooling.
2. **Heat Clamping:** Clamped at 5.0x to prevent "Debt Explosion" and calculation stalls.
3. **Heat Dissipation:** Linked to Target Frequency ($N$) to maintain "Natural Balance."
4. **Stateless Simulation:** Use in-memory lists for "Projected Score" to avoid DB pollution.

## Dashboard UI
1. **State Sync:** Using shared `st.session_state` keys (e.g., `key="is_solo"`) is the most reliable way to sync toggles across Streamlit "pages" without manual callback spaghetti.
2. **Pydantic Boundaries:** Using Pydantic metadata (`ge`, `le`) to drive UI `min_value`/`max_value` ensures the UI can't send invalid data to the engine.
