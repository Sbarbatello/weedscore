"""
Pydantic models for Weedscore configuration and user preferences.
"""

from pydantic import BaseModel, Field

class UserPreferences(BaseModel):
    """
    Structured data schema for user-level dashboard inputs.
    Ensures mathematical safety and serves as the "Source of Truth" 
    for the mapping layer.
    """
    target_frequency: int = Field(
        default=30, 
        ge=1, 
        le=365, 
        description="Goal sessions per year (N)"
    )
    patience_factor: float = Field(
        default=0.5, 
        ge=0.1, 
        le=1.0, 
        description="Scales the recovery midpoint (t0). 0.5 is the 'Natural Balance' (mid-interval)."
    )
    strictness: float = Field(
        default=2.4, 
        ge=1.0, 
        le=5.0, 
        description="Scales the cluster intensity power (P). Higher = more aggressive penalty."
    )
