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
    # Immutable Constants for default fallbacks
    DEFAULT_T0 = 14.0
    DEFAULT_K_SIGMOID = 0.5
    DEFAULT_T_THRESHOLD = 3.5
    DEFAULT_P_POWER = 2.4
    DEFAULT_BASE_WEIGHT = 1.0
    DEFAULT_SOLO_MULTIPLIER = 1.5
    DEFAULT_SENSITIVITY_K = 5500.0
    DEFAULT_HEAT_ACCUMULATION = 10.0
    DEFAULT_HEAT_DISSIPATION = 1.0
    DEFAULT_HEAT_CAP = 5.0
    DEFAULT_ANNUAL_WINDOW = 365.0
    DEFAULT_SPECIAL_OCCASION_BOOST = 1.5

    def __init__(
        self, 
        db: Optional[Session] = None,
        t0: float = DEFAULT_T0,
        k_sigmoid: float = DEFAULT_K_SIGMOID,
        t_threshold: float = DEFAULT_T_THRESHOLD,
        p_power: float = DEFAULT_P_POWER,
        base_weight: float = DEFAULT_BASE_WEIGHT,
        solo_multiplier: float = DEFAULT_SOLO_MULTIPLIER,
        sensitivity_k: float = DEFAULT_SENSITIVITY_K,
        heat_accumulation: float = DEFAULT_HEAT_ACCUMULATION,
        heat_dissipation: float = DEFAULT_HEAT_DISSIPATION,
        heat_cap: float = DEFAULT_HEAT_CAP,
        annual_window: float = DEFAULT_ANNUAL_WINDOW,
        special_occasion_boost: float = DEFAULT_SPECIAL_OCCASION_BOOST
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
        self.heat_cap = heat_cap
        self.annual_window = annual_window
        self.special_occasion_boost = special_occasion_boost

    def calculate_current_score(self, is_special_occasion: bool = False) -> float:
        """
        Fetches sessions from the rolling year and calculates the current score.
        """
        if not self.db:
            raise ValueError("Database session required for calculate_current_score")
            
        now = datetime.now(timezone.utc)
        # Dynamic window based on self.annual_window
        start_date = now - timedelta(days=self.annual_window)
        
        sessions = self.db.query(DBSession)\
            .filter(DBSession.timestamp >= start_date)\
            .order_by(DBSession.timestamp.asc())\
            .all()
            
        return self.calculate_score(sessions, now, is_special_occasion)

    def calculate_score(self, sessions: List[DBSession], evaluation_time: datetime, is_special_occasion: bool = False) -> float:
        """
        Core mathematical logic isolated from the database.
        Pure Function: relies ONLY on provided input and class instance parameters.
        """
        if not sessions:
            return 100.0

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
            days_since_event = (evaluation_time - session.timestamp).total_seconds() / (24 * 3600)
            
            # Skip if outside the rolling annual window
            if days_since_event > self.annual_window:
                continue

            # IAT calculation for Cluster Intensity (Ci)
            if prev_timestamp is None:
                iat = self.annual_window # Cold Start
            else:
                iat = (session.timestamp - prev_timestamp).total_seconds() / (24 * 3600)
            
            # Dissipate Heat since last event
            if prev_timestamp is not None:
                current_heat = max(0.0, current_heat - (iat * self.heat_dissipation))

            # Ci: Cluster Intensity Factor
            ci = 1.0 + max(0.0, (self.t_threshold - iat) / self.t_threshold) ** self.p_power

            # Hi: Heat Multiplier (Clamped)
            hi = min(self.heat_cap, 1.0 + (current_heat / self.heat_accumulation))

            # Si: Solo Multiplier
            si = self.solo_multiplier if session.is_solo else 1.0

            # Li: Annual Decay Factor (Scaling the session's weight based on age)
            li = max(0.0, 1.0 - (days_since_event / self.annual_window))
            
            # Integrate this session's debt
            session_debt = (self.base_weight * ci * hi * si * li)
            debt += session_debt

            # Accumulate Heat for the next session's calculation
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
