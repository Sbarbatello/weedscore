"""
Streamlit dashboard for visualizing and recording Weedscore sessions.
"""

import streamlit as st
import time
from datetime import datetime, timezone, timedelta
from typing import List, Optional

from src.database.connection import get_session
from src.database.models import Session as DBSession
from src.engine.calculator import WeedScoreCalculator
from src.engine.mapping import get_calculator_params
from src.engine.models import UserPreferences
from src.dashboard.config_manager import load_preferences, save_preferences
from pydantic import ValidationError

# --- Page Configuration ---
st.set_page_config(
    page_title="Weedscore",
    page_icon="🌿",
    layout="centered"
)

# --- Session State Initialization ---
if "current_page" not in st.session_state:
    st.session_state.current_page = "Main"

if "is_solo" not in st.session_state:
    st.session_state.is_solo = False

if "is_special_occasion" not in st.session_state:
    st.session_state.is_special_occasion = False

# --- Helper Functions ---
def get_current_score(prefs: UserPreferences) -> float:
    """Calculates the current weedscore from DB."""
    params = get_calculator_params(prefs)
    with get_session() as db:
        calc = WeedScoreCalculator(db=db, **params)
        return calc.calculate_current_score(is_special_occasion=st.session_state.is_special_occasion)

def get_projected_score(prefs: UserPreferences) -> float:
    """Calculates what the score WOULD be if a session was logged NOW."""
    params = get_calculator_params(prefs)
    now = datetime.now(timezone.utc)
    
    with get_session() as db:
        # Fetch actual sessions from the annual window
        start_date = now - timedelta(days=params.get("annual_window", 365.0))
        historical_sessions = db.query(DBSession)\
            .filter(DBSession.timestamp >= start_date)\
            .order_by(DBSession.timestamp.asc())\
            .all()
        
        # Add a temporary, uncommitted session for "now"
        temp_session = DBSession(
            timestamp=now,
            is_solo=st.session_state.is_solo,
            is_special_occasion=st.session_state.is_special_occasion
        )
        simulated_sessions = historical_sessions + [temp_session]
        
        calc = WeedScoreCalculator(**params)
        return calc.calculate_score(
            simulated_sessions, 
            now, 
            is_special_occasion=st.session_state.is_special_occasion
        )

def navigate_to(page: str):
    st.session_state.current_page = page
    st.rerun()

# --- Shared UI Elements ---
def render_live_toggles():
    """Renders the Is Solo and Special Occasion toggles (Synced)."""
    col1, col2 = st.columns(2)
    with col1:
        st.toggle("Is Solo?", key="is_solo")
    with col2:
        st.toggle("Special Occasion?", key="is_special_occasion")

# --- Screens ---

def show_main_screen():
    prefs = load_preferences()
    
    # Header
    col1, col2 = st.columns([0.9, 0.1])
    with col1:
        st.title("Weedscore")
    with col2:
        if st.button("⚙️", help="Settings"):
            navigate_to("Settings")
    
    # Score Display
    score = get_current_score(prefs)
    
    # RAG Color logic
    color = "red" if score < 50 else "orange" if score < 75 else "green"
    
    st.markdown(
        f"""
        <div style="text-align: center; padding: 20px; border-radius: 10px; background-color: rgba(0,0,0,0.05);">
            <h1 style="font-size: 80px; color: {color}; margin: 0;">{score}</h1>
            <p style="color: gray;">Current Deserve Metric</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.divider()
    
    # Toggles
    render_live_toggles()
    
    st.divider()
    
    # Call to Action
    if st.button("🌿 Log New Session", use_container_width=True, type="primary"):
        navigate_to("Record")

def show_record_screen():
    prefs = load_preferences()
    
    # Header
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        st.title("Record Session")
    with col2:
        if st.button("🏠", help="Home"):
            navigate_to("Main")
            
    # Live Preview Metric
    current_score = get_current_score(prefs)
    projected_score = get_projected_score(prefs)
    delta = round(projected_score - current_score, 2)
    
    st.metric(
        label="Projected Score (if logged now)",
        value=f"{projected_score}",
        delta=f"{delta} (New Debt)",
        delta_color="inverse"
    )
    
    st.divider()
    
    # Toggles (Continuity)
    render_live_toggles()
    
    notes = st.text_area("Notes (Optional)", placeholder="What are you smoking? How are you feeling?")
    
    st.divider()
    
    if st.button("✅ CONFIRM SESSION", use_container_width=True, type="primary"):
        with get_session() as db:
            new_session = DBSession(
                timestamp=datetime.now(timezone.utc),
                is_solo=st.session_state.is_solo,
                is_special_occasion=st.session_state.is_special_occasion,
                score_at_time=projected_score,
                notes=notes
            )
            db.add(new_session)
            db.commit()
            
        st.success("Session recorded successfully!")
        time.sleep(1)
        navigate_to("Main")

def show_settings_screen():
    # Header
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        st.title("Configuration")
    with col2:
        if st.button("🏠", help="Home"):
            navigate_to("Main")
            
    prefs = load_preferences()
    
    # DRY introspection of Pydantic fields
    # Fields: target_frequency, patience_factor, strictness
    fields = UserPreferences.model_fields
    
    st.subheader("Personalized Tuning")

    def get_constraint(field, constraint_type):
        """Helper to extract ge/le from Pydantic v2 metadata."""
        for meta in field.metadata:
            if hasattr(meta, constraint_type):
                return getattr(meta, constraint_type)
        return None
    
    # Target Frequency (N)
    n_field = fields['target_frequency']
    n_ge = get_constraint(n_field, 'ge')
    n_le = get_constraint(n_field, 'le')
    n_val = st.number_input(
        "Target Frequency (Sessions/Year)",
        min_value=int(n_ge) if n_ge is not None else 1,
        max_value=int(n_le) if n_le is not None else 365,
        value=prefs.target_frequency,
        step=1
    )
    
    # Patience Factor
    p_field = fields['patience_factor']
    p_ge = get_constraint(p_field, 'ge')
    p_le = get_constraint(p_field, 'le')
    p_val = st.slider(
        "Recovery Patience",
        min_value=float(p_ge) if p_ge is not None else 0.1,
        max_value=float(p_le) if p_le is not None else 1.0,
        value=prefs.patience_factor,
        step=0.05,
        help="Scales t0. 0.5 means recovery midpoint is halfway through your target interval."
    )
    
    # Strictness (P)
    s_field = fields['strictness']
    s_ge = get_constraint(s_field, 'ge')
    s_le = get_constraint(s_field, 'le')
    s_val = st.slider(
        "Bender Strictness",
        min_value=float(s_ge) if s_ge is not None else 1.0,
        max_value=float(s_le) if s_le is not None else 5.0,
        value=prefs.strictness,
        step=0.1,
        help="Scales the clustering penalty (P power)."
    )
    
    if st.button("💾 Save Settings", use_container_width=True):
        try:
            new_prefs = UserPreferences(
                target_frequency=n_val,
                patience_factor=p_val,
                strictness=s_val
            )
            save_preferences(new_prefs)
            st.success("Settings updated!")
            time.sleep(0.5)
            navigate_to("Main")
        except ValidationError as e:
            st.error(f"Validation Error: {e}")

# --- Routing ---
if st.session_state.current_page == "Main":
    show_main_screen()
elif st.session_state.current_page == "Record":
    show_record_screen()
elif st.session_state.current_page == "Settings":
    show_settings_screen()
