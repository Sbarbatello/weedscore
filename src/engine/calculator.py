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
    # Constants from aux/weedscore_calcs.md
    T0 = 14.0       # Midpoint of sigmoid
    K_SIGMOID = 0.5 # Sigmoid steepness
    T_THRESHOLD = 7.0 # Cluster window (days)
    P_POWER = 2.0   # Cluster power
    BASE_WEIGHT = 10.0
    SOLO_MULTIPLIER = 1.5
    SENSITIVITY_K = 1000.0
    HEAT_ACCUMULATION = 10.0
    HEAT_DISSIPATION = 1.0 # per day

    def __init__(self, db: Optional[Session] = None):
        self.db = db

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

        # 1. Short-Term Recovery (R)
        last_session = sessions[-1]
        t = (evaluation_time - last_session.timestamp).total_seconds() / (24 * 3600)
        r_t = 100.0 / (1.0 + math.exp(-self.K_SIGMOID * (t - self.T0)))

        # 2. Frequency Debt Integration (D)
        debt = 0.0
        current_heat = 0.0
        prev_timestamp: Optional[datetime] = None

        for session in sessions:
            # Calculate IAT for Cluster Intensity (Ci)
            if prev_timestamp is None:
                iat = 365.0 # Cold Start logic
            else:
                iat = (session.timestamp - prev_timestamp).total_seconds() / (24 * 3600)
            
            # Dissipate Heat since last session
            if prev_timestamp is not None:
                days_passed = iat
                current_heat = max(0.0, current_heat - (days_passed * self.HEAT_DISSIPATION))

            # Ci: Cluster Intensity
            ci = 1.0 + max(0.0, (self.T_THRESHOLD - iat) / self.T_THRESHOLD) ** self.P_POWER

            # Hi: Heat Multiplier
            # Based on spec: 1 + (current heat at session time / 10)
            hi = 1.0 + (current_heat / 10.0)

            # Si: Solo Multiplier
            si = self.SOLO_MULTIPLIER if session.is_solo else 1.0

            # Li: Annual Decay (only if session is within last 365 days)
            days_since_event = (evaluation_time - session.timestamp).total_seconds() / (24 * 3600)
            if days_since_event <= 365:
                li = max(0.0, 1.0 - (days_since_event / 365.0))
                session_debt = (self.BASE_WEIGHT * ci * hi * si * li)
                debt += session_debt

            # Accumulate Heat for NEXT session
            current_heat += self.HEAT_ACCUMULATION
            prev_timestamp = session.timestamp

        # 3. Final Integration (W)
        w = r_t / (1.0 + (debt / self.SENSITIVITY_K))
        
        # Occasion Boost
        if is_special_occasion:
            w *= 1.5
            
        return round(min(100.0, w), 2)

if __name__ == "__main__":
    with get_session() as db_session:
        calc = WeedScoreCalculator(db_session)
        score = calc.calculate_current_score()
        print(f"Current Calculated Weedscore: {score}")
