"""
Trading Setup Model

This module defines the output model for the Trader agent.
"""

from pydantic import BaseModel, Field, field_validator, computed_field
from typing import Optional, List
from datetime import datetime

from .enums import TradeDirection
from .base import PriceLevel


class TradingSetup(BaseModel):
    """
    Output model for the Trader agent.
    Contains the complete trading setup with entry, stop loss, and take profit levels.
    """
    direction: TradeDirection = Field(..., description="Trade direction: LONG, SHORT, or NO_TRADE")
    symbol: str = Field(..., description="Financial instrument ticker symbol")
    
    # Price levels
    entry: Optional[PriceLevel] = Field(None, description="Entry price level")
    stop_loss: Optional[PriceLevel] = Field(None, description="Stop loss price level")
    take_profit_targets: List[PriceLevel] = Field(default_factory=list, description="Take profit target levels")
    
    # Setup analysis
    chart_structure: str = Field(default="", description="Chart structure analysis")
    reward_to_risk_ratio: Optional[float] = Field(None, gt=0, description="Expected reward-to-risk ratio")
    setup_quality: Optional[str] = Field(None, description="Assessment of setup quality")
    
    # Justification
    justification: str = Field(..., description="Trading setup justification")
    
    # Metadata
    analyst_recommendation: Optional['AnalystRecommendation'] = Field(None, description="Reference to analyst recommendation")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp of the setup")
    
    @field_validator("stop_loss")
    @classmethod
    def validate_stop_loss(cls, v, info):
        """Ensure stop loss is on the correct side of entry."""
        if v is None or info.data.get("entry") is None:
            return v
        
        direction = info.data.get("direction")
        entry_price = info.data["entry"].price
        stop_price = v.price
        
        if direction == TradeDirection.LONG and stop_price >= entry_price:
            raise ValueError("Stop loss must be below entry price for LONG trades")
        elif direction == TradeDirection.SHORT and stop_price <= entry_price:
            raise ValueError("Stop loss must be above entry price for SHORT trades")
        
        return v
    
    @computed_field
    @property
    def is_actionable(self) -> bool:
        """Check if the trading setup is actionable."""
        return (
            self.direction in [TradeDirection.LONG, TradeDirection.SHORT]
            and self.entry is not None
            and self.stop_loss is not None
            and len(self.take_profit_targets) > 0
        )
    
    @computed_field
    @property
    def risk_per_share(self) -> Optional[float]:
        """Calculate risk per share."""
        if self.entry and self.stop_loss:
            return abs(self.entry.price - self.stop_loss.price)
        return None


# Import after class definition to avoid circular imports
from .analyst import AnalystRecommendation
TradingSetup.model_rebuild()
