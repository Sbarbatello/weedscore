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
    Test R(t) at exactly t0 to ensure it returns 50.0.
    """
    clean_db(db)
    now = datetime.now(timezone.utc)
    
    # Use default preferences
    prefs = UserPreferences(target_frequency=30, patience_factor=0.5)
    params = get_calculator_params(prefs)
    t0 = params['t0']
    
    # Add one session exactly t0 days ago
    db.add(DBSession(
        timestamp=now - timedelta(days=t0),
        is_solo=False,
        is_special_occasion=False,
        score_at_time=0.0,
        notes="Test t0"
    ))
    db.commit()
    
    calc = WeedScoreCalculator(db=db, **params)
    score = calc.calculate_current_score()
    
    # R(t0) should be 50.0. 
    # Debt D for one session t0 days ago:
    # Ci = 1.0 (IAT = Cold Start)
    # Hi = 1.0 (Heat = 0 initial)
    # Si = 1.0 (is_solo = False)
    # Li = max(0, 1 - t0/365.0)
    # D = BaseWeight * Ci * Hi * Si * Li = 1.0 * 1.0 * 1.0 * 1.0 * (1 - t0/365.0)
    
    expected_r = 50.0
    debt = 1.0 * (1 - t0/365.0)
    expected_w = round(expected_r / (1.0 + (debt / params['sensitivity_k'])), 2)
    
    assert score == expected_w

def test_clean_slate(db):
    """Test that 'The Clean Slate' (no sessions) returns 100.0."""
    clean_db(db)
    prefs = UserPreferences()
    params = get_calculator_params(prefs)
    calc = WeedScoreCalculator(db=db, **params)
    score = calc.calculate_current_score()
    assert score == 100.0

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
