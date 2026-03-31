import pytest
import math
from datetime import datetime, timedelta, timezone
from src.database.connection import get_session
from src.database.models import Session as DBSession
from src.engine.calculator import WeedScoreCalculator
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
    Test R(t) at exactly 14 days (t0) to ensure it returns 50.0.
    Since we don't have direct access to R(t) from the calculator easily,
    we seed a session exactly 14 days ago and check if the debt-free score is ~50.
    """
    clean_db(db)
    now = datetime.now(timezone.utc)
    t0 = WeedScoreCalculator.T0
    
    # Add one session exactly t0 days ago
    db.add(DBSession(
        timestamp=now - timedelta(days=t0),
        is_solo=False,
        is_special_occasion=False,
        score_at_time=0.0,
        notes="Test t0"
    ))
    db.commit()
    
    calc = WeedScoreCalculator(db)
    score = calc.calculate_current_score()
    
    # R(14) should be 50.0. 
    # Debt D for one session 14 days ago:
    # Ci = 1.0 (IAT = 365 default)
    # Hi = 1.0 (Heat = 0 initial)
    # Si = 1.0 (is_solo = False)
    # Li = max(0, 1 - 14/365) = 0.9616
    # D = 10 * 1 * 1 * 1 * 0.9616 = 9.616
    # W = 50 / (1 + 9.616/150) = 50 / 1.0641 = 46.98
    
    # Wait, the instruction says "Test R(t) at exactly 14 days (t0) to ensure it returns 50.0".
    # This might mean checking if r_t itself is 50 inside the calculator, but W will be suppressed by debt.
    # Let's adjust the test to calculate what W SHOULD be based on R=50.
    
    expected_r = 50.0
    debt = 10.0 * 1.0 * 1.0 * 1.0 * (1 - t0/365.0)
    expected_w = round(expected_r / (1.0 + (debt / calc.SENSITIVITY_K)), 2)
    
    assert score == expected_w

def test_clean_slate(db):
    """Test that 'The Clean Slate' (no sessions) returns 100.0."""
    clean_db(db)
    calc = WeedScoreCalculator(db)
    score = calc.calculate_current_score()
    assert score == 100.0

def test_moderator_scenario(db):
    """
    Run the 'Moderator' scenario and print the result.
    If it is below 50.0, suggest a new value for SENSITIVITY_K in the logs.
    """
    # Manual seed using the current db session to avoid session conflicts/deadlocks
    clean_db(db)
    now = datetime.now(timezone.utc)
    # Most recent 21 days ago, others spaced 12 days before that
    for days in [21, 33, 45, 57]:
        db.add(DBSession(
            timestamp=now - timedelta(days=days),
            is_solo=False,
            is_special_occasion=False,
            score_at_time=0.0,
            notes="Scenario: The Moderator"
        ))
    db.commit()
    
    calc = WeedScoreCalculator(db)
    score = calc.calculate_current_score()
    
    print(f"\n[Validation] Moderator Score: {score}")
    if score < 50.0:
        print(f"[Warning] Score is {score}, which is below the target threshold of 50.0 for a 'Moderator'.")
        print(f"[Advice] Suggest increasing SENSITIVITY_K (current: {calc.SENSITIVITY_K}) to relax the suppression.")
    else:
        print(f"[Success] Moderator Score {score} is above 50.0.")
    
    assert score > 0
