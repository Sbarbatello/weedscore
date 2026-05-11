import pytest
import math
from datetime import datetime, timedelta, timezone
from src.database.connection import get_session
from src.database.models import Session as DBSession
from src.engine.calculator import WeedScoreCalculator
from src.engine.mapping import get_calculator_params
from src.engine.models import UserPreferences
from sqlalchemy import text

@pytest.fixture(scope="module")
def db():
    """Provides a database session for testing."""
    with get_session() as session:
        yield session

def clean_db(db):
    """Utility to clear the sessions table."""
    db.execute(text("TRUNCATE TABLE sessions RESTART IDENTITY CASCADE;"))
    db.commit()

def test_recovery_at_midpoint(db):
    """
    Test R(t) at exactly the recovery midpoint (t0).
    The score should be approximately 50 (adjusted for debt).
    """
    clean_db(db)
    now = datetime.now(timezone.utc)
    
    # User intent: Target 30 sessions, standard patience
    prefs = UserPreferences(target_frequency=30, patience_factor=0.5)
    params = get_calculator_params(prefs)
    t0 = params['t0']
    
    # Add one session exactly t0 days ago
    db.add(DBSession(
        timestamp=now - timedelta(days=t0),
        is_solo=False,
        is_special_occasion=False
    ))
    db.commit()
    
    calc = WeedScoreCalculator(db=db, **params)
    score = calc.calculate_current_score()
    
    # At t0, R(t) is 50.0. 
    # Final score W = 50 / (1 + Debt/K)
    # Since Debt > 0, W must be < 50.0.
    assert score < 50.0
    assert score > 45.0 # High sensitivity K makes debt impact small for 1 session

def test_clean_slate(db):
    """Test that 'The Clean Slate' (no sessions) returns 100.0."""
    clean_db(db)
    # Verify even with high target frequency, clean slate is 100
    prefs = UserPreferences(target_frequency=100)
    params = get_calculator_params(prefs)
    calc = WeedScoreCalculator(db=db, **params)
    score = calc.calculate_current_score()
    assert score == 100.0

def test_bender_strictness_impact(db):
    """
    Verify that increasing 'Strictness' (P) results in a lower score for clustered sessions.
    """
    now = datetime.now(timezone.utc)
    
    def get_score_for_strictness(strictness_val):
        clean_db(db)
        # 3 sessions in 2 days (A Bender)
        # But evaluation is 14 days later so score is in recovery (near 50)
        # This makes the Debt impact much more visible
        eval_time = now + timedelta(days=14)
        for hours in [0, 12, 24]:
            db.add(DBSession(
                timestamp=now - timedelta(hours=hours),
                is_solo=False,
                is_special_occasion=False
            ))
        db.commit()
        
        prefs = UserPreferences(target_frequency=30, strictness=strictness_val)
        params = get_calculator_params(prefs)
        calc = WeedScoreCalculator(db=db, **params)
        return calc.calculate_score(db.query(DBSession).all(), eval_time)

    score_low_strict = get_score_for_strictness(1.0)
    score_high_strict = get_score_for_strictness(5.0)
    
    assert score_high_strict < score_low_strict

def test_moderator_scenario(db):
    """
    Run a 'Moderator' scenario and ensure it results in a healthy score.
    """
    clean_db(db)
    now = datetime.now(timezone.utc)
    
    # 4 sessions, spaced 12 days apart, most recent 21 days ago
    for days in [21, 33, 45, 57]:
        db.add(DBSession(
            timestamp=now - timedelta(days=days),
            is_solo=False,
            is_special_occasion=False,
            score_at_time=0.0,
            notes="Scenario: The Moderator"
        ))
    db.commit()
    
    prefs = UserPreferences(target_frequency=30)
    params = get_calculator_params(prefs)
    calc = WeedScoreCalculator(db=db, **params)
    score = calc.calculate_current_score()
    
    assert score > 50.0
