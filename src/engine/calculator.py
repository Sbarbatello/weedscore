"""
Core calculation engine for the Weedscore metric.
"""

import math
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from src.database.models import Session as DBSession
from src.database.connection import get_session

class WeedScoreCalculator:
    # Class-level defaults for backward compatibility and reference
    T0 = 14.0
    K_SIGMOID = 0.2
    T_THRESHOLD = 3.5
    P_POWER = 2.0
    BASE_WEIGHT = 1.0

    SOLO_MULTIPLIER = 1.5
    SENSITIVITY_K = 1000.0
    HEAT_ACCUMULATION = 10.0
    HEAT_DISSIPATION = 1.0
    SPECIAL_OCCASION_BOOST = 1.5

    def __init__(
        self, 
        db: Optional[Session] = None,
        t0: float = T0,
        k_sigmoid: float = K_SIGMOID,
        t_threshold: float = T_THRESHOLD,
        p_power: float = P_POWER,
        base_weight: float = BASE_WEIGHT,
        solo_multiplier: float = SOLO_MULTIPLIER,
        sensitivity_k: float = SENSITIVITY_K,
        heat_accumulation: float = HEAT_ACCUMULATION,
        heat_dissipation: float = HEAT_DISSIPATION,
        special_occasion_boost: float = SPECIAL_OCCASION_BOOST
    ):
        self.db = db
        self.t0 = t0
        self.k_sigmoid = k_sigmoid
        self.t_threshold = t_threshold
        self.p_power = p_power
        self.base_weight = base_weight
        self.solo_multiplier = solo_multiplier
        self.sensitivity_k = sensitivity_k
        self.heat_accumulation = heat_accumulation
        self.heat_dissipation = heat_dissipation
        self.special_occasion_boost = special_occasion_boost

    def calculate_current_score(self, is_special_occasion: bool = False) -> float:
        """
        Fetches sessions from DB and calculates the current score.
        """
        if not self.db:
            raise ValueError("Database session required for calculate_current_score")
            
        sessions = self.db.query(DBSession).order_by(DBSession.timestamp.asc()).all()
        return self.calculate_score(sessions, datetime.now(timezone.utc), is_special_occasion)

    def calculate_score(self, sessions: List[DBSession], evaluation_time: datetime, is_special_occasion: bool = False) -> float:
        """
        Core mathematical logic isolated from the database.
        """
        if not sessions:
            return 100.0 if not is_special_occasion else 100.0

        # Ensure sessions are sorted chronologically to maintain IAT logic
        sorted_sessions = sorted(sessions, key=lambda x: x.timestamp)

        # 1. Short-Term Recovery (R)
        last_session = sorted_sessions[-1]
        t = (evaluation_time - last_session.timestamp).total_seconds() / (24 * 3600)
        r_t = 100.0 / (1.0 + math.exp(-self.k_sigmoid * (t - self.t0)))

        # 2. Frequency Debt Integration (D)
        debt = 0.0
        current_heat = 0.0
        prev_timestamp: Optional[datetime] = None

        for session in sorted_sessions:
            # Days since this session being evaluated
            days_since_event = (evaluation_time - session.timestamp).total_seconds() / (24 * 3600)
            
            # Calculate IAT for Cluster Intensity (Ci)
            if prev_timestamp is None:
                iat = 365.0 # Cold Start logic
            else:
                iat = (session.timestamp - prev_timestamp).total_seconds() / (24 * 3600)
            
            # Dissipate Heat since last session
            if prev_timestamp is not None:
                days_passed = iat
                current_heat = max(0.0, current_heat - (days_passed * self.heat_dissipation))

            # Ci: Cluster Intensity
            ci = 1.0 + max(0.0, (self.t_threshold - iat) / self.t_threshold) ** self.p_power

            # Hi: Heat Multiplier
            # Based on spec: min(5.0, 1.0 + (current heat at session time / 10))
            hi = min(5.0, 1.0 + (current_heat / 10.0))

            # Si: Solo Multiplier
            si = self.solo_multiplier if session.is_solo else 1.0

            # Li: Annual Decay
            if days_since_event <= 365:
                li = max(0.0, 1.0 - (days_since_event / 365.0))
                session_debt = (self.base_weight * ci * hi * si * li)
                debt += session_debt

            # Accumulate Heat for NEXT session
            current_heat += self.heat_accumulation
            prev_timestamp = session.timestamp

        # 3. Final Integration (W)
        w = r_t / (1.0 + (debt / self.sensitivity_k))
        
        # Occasion Boost
        if is_special_occasion:
            w *= self.special_occasion_boost
            
        return round(min(100.0, w), 2)

if __name__ == "__main__":
    with get_session() as db_session:
        calc = WeedScoreCalculator(db_session)
        score = calc.calculate_current_score()
        print(f"Current Calculated Weedscore: {score}")
