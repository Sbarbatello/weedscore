"""
Mapping Layer for Weedscore.
Translates user preferences into calculator engine parameters.
"""

from typing import Dict, Any
from src.engine.models import UserPreferences

# Calibration constant derived from N=30, K=5500 optimization
# C = 183.3 ensures W ~ 85 for perfect moderators.
C_CONSTANT = 183.3

def get_calculator_params(prefs: UserPreferences) -> Dict[str, Any]:
    """
    Derives engine parameters from validated user preferences.
    """
    # 1. Sensitivity (K) scales linearly with Target Frequency (N)
    sensitivity_k = C_CONSTANT * prefs.target_frequency
    
    # 2. Base Interval (Target gap between sessions)
    base_interval = 365.0 / prefs.target_frequency
    
    # 3. Midpoint (t0): interval scaled by patience_factor
    # (Default 0.5 * interval = mid-point recovery)
    t0 = base_interval * prefs.patience_factor
    
    # 4. Heat Dissipation
    # Natural Balance: Dissipate 10 units (1 session) over the target interval.
    heat_dissipation = 10.0 / base_interval
    
    return {
        "sensitivity_k": sensitivity_k,
        "t0": t0,
        "heat_dissipation": heat_dissipation,
        "p_power": prefs.strictness,
        "k_sigmoid": 0.5,      # Fixed steepness for consistent recovery
        "t_threshold": 3.5,    # Danger Zone window (days)
        "base_weight": 1.0     # Baseline session cost
    }
