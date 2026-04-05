"""
Dynamic Validation of the Mapping Layer for Weedscore.
Verifies that the formula scales correctly when target frequency (N) changes.
Uses Pydantic UserPreferences for schema enforcement.
"""

from datetime import datetime, timedelta, timezone
from src.engine.calculator import WeedScoreCalculator
from src.database.models import Session as DBSession
from src.engine.mapping import get_calculator_params
from src.engine.models import UserPreferences
from pydantic import ValidationError

def run_strict_sabbatical():
    """N=15: 10 sessions in a week, 90 days ago. Expectation: >90."""
    prefs = UserPreferences(target_frequency=15, patience_factor=0.5, strictness=2.4)
    params = get_calculator_params(prefs)
    now = datetime.now(timezone.utc)
    
    sessions = []
    end_ts = now - timedelta(days=90)
    for i in range(10):
        ts = end_ts - timedelta(hours=i * 18)
        sessions.append(DBSession(timestamp=ts, is_solo=False))
    
    calc = WeedScoreCalculator(**params)
    score = calc.calculate_score(sessions, now)
    return prefs.target_frequency, params['sensitivity_k'], params['heat_dissipation'], score

def run_relaxed_moderator():
    """N=50: 1 session every 8 days. Expectation: ~89 (Fixed by 0.5 Multiplier Rule)."""
    prefs = UserPreferences(target_frequency=50, patience_factor=0.5, strictness=2.4)
    params = get_calculator_params(prefs)
    now = datetime.now(timezone.utc)
    
    sessions = []
    # 1 session every 8 days for a full year
    for i in range(1, 46):
        ts = now - timedelta(days=i * 8)
        sessions.append(DBSession(timestamp=ts, is_solo=False))
    
    calc = WeedScoreCalculator(**params)
    score = calc.calculate_score(sessions, now)
    return prefs.target_frequency, params['sensitivity_k'], params['heat_dissipation'], score

def run_strict_bender():
    """N=30, Strictness=4.0: 4 sessions in 48 hours, evaluated 4 days later. Expectation: Low."""
    prefs = UserPreferences(target_frequency=30, patience_factor=0.5, strictness=4.0)
    params = get_calculator_params(prefs)
    now = datetime.now(timezone.utc)
    
    sessions = []
    last_ts = now - timedelta(days=4)
    for i in range(4):
        ts = last_ts - timedelta(hours=i * 16)
        sessions.append(DBSession(timestamp=ts, is_solo=True))
    
    calc = WeedScoreCalculator(**params)
    score = calc.calculate_score(sessions, now)
    return prefs.target_frequency, params['sensitivity_k'], params['heat_dissipation'], score

def verify_pydantic_enforcement():
    """Verifies that invalid N (e.g. 500) raises a ValidationError."""
    print("\n--- Pydantic Enforcement Check ---")
    try:
        UserPreferences(target_frequency=500)
        print("FAIL: Should have raised ValidationError for N=500")
    except ValidationError as e:
        print(f"SUCCESS: Caught expected ValidationError: {e.errors()[0]['msg']}")

def verify():
    print(f"--- Dynamic Mapping Layer Validation ---")
    print(f"{'Scenario':<20} | {'N':<3} | {'K':<8} | {'Dissip.':<10} | {'Score':<6}")
    print("-" * 65)
    
    # 1. Strict Sabbatical
    n, k, d, score = run_strict_sabbatical()
    print(f"{'Strict Sabbatical':<20} | {n:<3} | {k:<8.1f} | {d:<10.4f} | {score:<6.2f}")
    
    # 2. Relaxed Moderator
    n, k, d, score = run_relaxed_moderator()
    print(f"{'Relaxed Moderator':<20} | {n:<3} | {k:<8.1f} | {d:<10.4f} | {score:<6.2f}")
    
    # 3. Strict Bender
    n, k, d, score = run_strict_bender()
    print(f"{'Strict Bender':<20} | {n:<3} | {k:<8.1f} | {d:<10.4f} | {score:<6.2f}")

    verify_pydantic_enforcement()

if __name__ == "__main__":
    verify()
