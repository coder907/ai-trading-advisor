"""
Risk Allocation Model

This module defines the output model for the Risk Manager agent.
"""

from pydantic import BaseModel, Field, field_validator, computed_field
from typing import Optional
from datetime import datetime

from .enums import TradeDirection, ConvictionLevel


class RiskAllocation(BaseModel):
    """
    Output model for the Risk Manager agent.
    Contains the risk allocation and position sizing information.
    """
    direction: TradeDirection = Field(..., description="Trade direction: LONG, SHORT, or NO_TRADE")
    symbol: str = Field(..., description="Financial instrument ticker symbol")
    
    # Risk parameters
    account_equity: float = Field(..., gt=0, description="Total account equity in dollars")
    risk_percentage: Optional[float] = Field(None, ge=0.5, le=2.0, description="Risk percentage (0.5% - 2.0%)")
    risk_amount_dollars: Optional[float] = Field(None, gt=0, description="Dollar risk allocation")
    
    # Position sizing
    position_size_shares: Optional[float] = Field(None, gt=0, description="Calculated position size in shares")
    position_value_dollars: Optional[float] = Field(None, gt=0, description="Total position value in dollars")
    
    # Justification
    justification: str = Field(..., description="Risk allocation reasoning")
    conviction_assessment: Optional[ConvictionLevel] = Field(None, description="Assessed conviction level")
    setup_quality_assessment: Optional[str] = Field(None, description="Assessment of setup quality")
    
    # Metadata
    trading_setup: Optional['TradingSetup'] = Field(None, description="Reference to trading setup")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp of the allocation")
    
    @field_validator("risk_percentage")
    @classmethod
    def validate_risk_percentage(cls, v, info):
        """Ensure risk percentage is None for NO_TRADE."""
        direction = info.data.get("direction")
        if direction == TradeDirection.NO_TRADE and v is not None:
            return None
        return v
    
    @computed_field
    @property
    def is_actionable(self) -> bool:
        """Check if the risk allocation is actionable."""
        return (
            self.direction in [TradeDirection.LONG, TradeDirection.SHORT]
            and self.risk_amount_dollars is not None
            and self.risk_percentage is not None
        )
    
    @computed_field
    @property
    def risk_limits_met(self) -> bool:
        """Verify risk percentage is within allowed limits."""
        if self.risk_percentage is None:
            return True # NO_TRADE case
        return 0.5 <= self.risk_percentage <= 2.0


# Import after class definition to avoid circular imports
from .trader import TradingSetup
RiskAllocation.model_rebuild()
