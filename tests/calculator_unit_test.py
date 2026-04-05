"""
Isolated unit test for WeedScoreCalculator mathematical logic.
Loads scenarios from CSV files and validates the score.
"""

import csv
import argparse
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from src.engine.calculator import WeedScoreCalculator
from src.engine.mapping import get_calculator_params
from src.engine.models import UserPreferences
from src.database.models import Session as DBSession

def load_sessions_from_csv(file_path: str) -> List[DBSession]:
    """
    Reads a CSV file and returns a list of DBSession objects.
    """
    sessions = []
    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sessions.append(DBSession(
                timestamp=datetime.fromisoformat(row['timestamp']),
                is_solo=row['is_solo'].lower() == 'true',
                is_special_occasion=row['is_special_occasion'].lower() == 'true',
                score_at_time=float(row['score_at_time']),
                notes=row['notes']
            ))
    return sessions

def run_test(
    csv_path: str, 
    evaluation_time: Optional[str] = None, 
    days_since_last: Optional[float] = None,
    target_frequency: int = 30
) -> None:
    """
    Runs the calculation for a given CSV dataset.
    """
    sessions = load_sessions_from_csv(csv_path)
    if not sessions:
        print("Error: No sessions found in CSV.")
        return
        
    last_session_ts = sessions[-1].timestamp
    
    # Priority: 1. days_since_last, 2. evaluation_time, 3. default (12d)
    if days_since_last is not None:
        eval_dt = last_session_ts + timedelta(days=days_since_last)
    elif evaluation_time == "now":
        eval_dt = datetime.now(timezone.utc)
    elif evaluation_time:
        eval_dt = datetime.fromisoformat(evaluation_time)
    else:
        # Default to exactly 12 days after the last session in the CSV
        eval_dt = last_session_ts + timedelta(days=12)

    # Use specified or default target frequency
    prefs = UserPreferences(target_frequency=target_frequency)
    params = get_calculator_params(prefs)
    
    calc = WeedScoreCalculator(db=None, **params) # No DB needed for isolated logic
    score = calc.calculate_score(sessions, eval_dt)
    
    # Calculate days since last session for reporting
    diff_days = (eval_dt - last_session_ts).total_seconds() / (24 * 3600)
    
    print(f"--- Unit Test Report ---")
    print(f"Dataset: {csv_path}")
    print(f"Target Frequency (N): {target_frequency}")
    print(f"Last Session Time: {last_session_ts}")
    print(f"Evaluation Time: {eval_dt}")
    print(f"Time Since Last Session: {diff_days:.2f} days")
    print(f"Total Sessions: {len(sessions)}")
    print(f"Calculated Score: {score}")
    print(f"------------------------")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Isolated unit test for Weedscore Calculator.")
    parser.add_argument("--csv", type=str, required=True, help="Path to the CSV dataset.")
    parser.add_argument("--eval_time", type=str, help="ISO timestamp for evaluation (optional).")
    parser.add_argument("--days_since_last", type=float, help="Days since the last recorded session (optional).")
    parser.add_argument("--n", type=int, default=30, help="Target frequency (default: 30).")
    
    args = parser.parse_args()
    run_test(args.csv, args.eval_time, args.days_since_last, args.n)
