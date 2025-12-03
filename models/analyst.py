"""
Financial Analyst Model

This module defines the output model for the Financial Analyst agent.
"""

from pydantic import BaseModel, Field, field_validator, computed_field
from typing import Optional, List
from datetime import datetime

from .enums import TradeDirection, ConvictionLevel
from .base import TechnicalFactors, FundamentalFactors


class AnalystRecommendation(BaseModel):
    """
    Output model for the Financial Analyst agent.
    Contains the directional recommendation and supporting analysis.
    """
    direction: TradeDirection = Field(..., description="Trade direction: LONG, SHORT, or NO_TRADE")
    conviction: ConvictionLevel = Field(..., description="Conviction level: LOW, MEDIUM, HIGH, or NONE")
    symbol: str = Field(..., description="Financial instrument ticker symbol")
    
    # Analysis components
    technical_factors: TechnicalFactors = Field(default_factory=TechnicalFactors, description="Technical analysis factors")
    fundamental_factors: Optional[FundamentalFactors] = Field(None, description="Fundamental factors (if used)")
    
    # Summary and reasoning
    justification: str = Field(..., description="Concise explanation of the recommendation")
    key_observations: List[str] = Field(default_factory=list, description="Key observations from the analysis")
    
    # Metadata
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp of the analysis")
    
    @field_validator("conviction")
    @classmethod
    def validate_conviction(cls, v, info):
        """Ensure conviction is NONE when direction is NO_TRADE."""
        if info.data.get("direction") == TradeDirection.NO_TRADE and v != ConvictionLevel.NONE:
            return ConvictionLevel.NONE
        return v
    
    @computed_field
    @property
    def is_actionable(self) -> bool:
        """Check if the recommendation is actionable (LONG or SHORT)."""
        return self.direction in [TradeDirection.LONG, TradeDirection.SHORT]
