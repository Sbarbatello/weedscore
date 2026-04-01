"""
Parameter Optimization & Calibration Framework for Weedscore.
Performs Grid Search to find optimal sensitivity (K) and penalty power (P).
"""

import math
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Tuple
from src.engine.calculator import WeedScoreCalculator
from src.database.models import Session as DBSession

# Golden Benchmarks
BENCHMARKS = {
    "Perfect Moderator": 85.0,
    "The Bender": 15.0,
}

def simulate_perfect_moderator(n: int, now: datetime) -> List[DBSession]:
    """Sessions spaced exactly at 365/N intervals. Evaluated t0 + 7 days after last."""
    gap = 365.0 / n
    sessions = []
    # Eval is at 'now'. Last session was t0 + 7 days ago.
    # For optimization, we use t0 = gap. So last session was gap + 7 days ago.
    for i in range(1, n + 1):
        ts = now - timedelta(days=(i * gap) + 7)
        sessions.append(DBSession(timestamp=ts, is_solo=False))
    return sessions

def simulate_the_bender(now: datetime) -> List[DBSession]:
    """5 sessions within 72 hours, evaluated 10 days after the last session."""
    sessions = []
    # Last session 10 days ago
    last_ts = now - timedelta(days=10)
    # 5 sessions within 72 hours (3 days) before that
    for i in range(5):
        ts = last_ts - timedelta(hours=i * (72/4)) # spread 5 sessions across 72h
        sessions.append(DBSession(timestamp=ts, is_solo=True))
    return sessions

def calculate_error(scores: Dict[str, float]) -> float:
    """Total absolute error across benchmarks."""
    error = 0.0
    for name, target in BENCHMARKS.items():
        error += abs(scores[name] - target)
    return error

def optimize():
    now = datetime.now(timezone.utc)
    target_ns = [20, 30, 50]
    
    # Grid Search space
    ks = range(500, 10001, 500)
    ps = [1.0, 2.0, 3.0]
    sigmoid_ks = [0.1, 0.2, 0.3, 0.5]
    
    print(f"--- Weedscore Optimization Report ---")
    print(f"{'N':<5} | {'Opt K':<7} | {'Opt P':<5} | {'Sig k':<5} | {'Min Error':<10}")
    print("-" * 50)

    results = []

    for n in target_ns:
        best_k = 0
        best_p = 0
        best_sig_k = 0
        min_error = float('inf')
        
        # Dynamic parameters for this N
        heat_diss = 10.0 / (365.0 / n)
        t0_val = 365.0 / n
        
        mod_sessions = simulate_perfect_moderator(n, now)
        bender_sessions = simulate_the_bender(now)

        for sig_k in sigmoid_ks:
            for p in ps:
                for k in ks:
                    calc = WeedScoreCalculator(
                        sensitivity_k=k, 
                        p_power=p,
                        heat_dissipation=heat_diss,
                        heat_accumulation=10.0,
                        base_weight=1.0,
                        t0=t0_val,
                        k_sigmoid=sig_k
                    )
                    
                    scores = {
                        "Perfect Moderator": calc.calculate_score(mod_sessions, now),
                        "The Bender": calc.calculate_score(bender_sessions, now),
                    }
                    
                    err = calculate_error(scores)
                    if err < min_error:
                        min_error = err
                        best_k = k
                        best_p = p
                        best_sig_k = sig_k

        print(f"{n:<5} | {best_k:<7} | {best_p:<5.1f} | {best_sig_k:<5.1f} | {min_error:<10.2f}")
        
        # Get final scores for report
        best_calc = WeedScoreCalculator(
            sensitivity_k=best_k, 
            p_power=best_p, 
            heat_dissipation=heat_diss,
            base_weight=1.0,
            t0=t0_val,
            k_sigmoid=best_sig_k
        )
        final_scores = {
            "Perfect Moderator": best_calc.calculate_score(mod_sessions, now),
            "The Bender": best_calc.calculate_score(bender_sessions, now),
        }
        print(f"      -> {final_scores}")
        
        results.append((n, best_k))

    print("\n--- Calibration Insights ---")
    cs = [k/n for n, k in results]
    avg_c = sum(cs) / len(cs)
    print(f"Proposed Linear Formula: K = {round(avg_c)} * N")

if __name__ == "__main__":
    optimize()
