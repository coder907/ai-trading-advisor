"""
Complete Trade Plan Model

This module defines the comprehensive trade plan combining all agent outputs.
"""

from pydantic import BaseModel, Field, computed_field
from typing import Literal
from datetime import datetime

from .analyst import AnalystRecommendation
from .trader import TradingSetup
from .risk_manager import RiskAllocation


class CompleteTradePlan(BaseModel):
    """
    Comprehensive trade plan combining all agent outputs.
    This is the final output of the entire workflow.
    """
    symbol: str = Field(..., description="Financial instrument ticker symbol")
    
    # Component outputs
    analyst_recommendation: AnalystRecommendation = Field(..., description="Financial analyst recommendation")
    trading_setup: TradingSetup = Field(..., description="Trading setup from trader agent")
    risk_allocation: RiskAllocation = Field(..., description="Risk allocation from risk manager")
    
    # Workflow metadata
    workflow_status: Literal["COMPLETE", "NO_TRADE", "ERROR"] = Field(..., description="Overall workflow status")
    created_at: datetime = Field(default_factory=datetime.now, description="Workflow completion timestamp")
    
    @computed_field
    @property
    def is_executable(self) -> bool:
        """Check if the complete trade plan is ready for execution."""
        return (
            self.workflow_status == "COMPLETE"
            and self.analyst_recommendation.is_actionable
            and self.trading_setup.is_actionable
            and self.risk_allocation.is_actionable
            and self.risk_allocation.risk_limits_met
        )
    
    @computed_field
    @property
    def summary(self) -> str:
        """Generate a human-readable summary of the trade plan."""
        if self.workflow_status == "NO_TRADE":
            return f"NO TRADE recommendation for {self.symbol}. Reason: {self.analyst_recommendation.justification}"
        
        if not self.is_executable:
            return f"Trade plan for {self.symbol} is incomplete or has validation errors."
        
        direction = self.trading_setup.direction.value
        entry = self.trading_setup.entry.price if self.trading_setup.entry else "N/A"
        stop = self.trading_setup.stop_loss.price if self.trading_setup.stop_loss else "N/A"
        risk = self.risk_allocation.risk_amount_dollars
        risk_pct = self.risk_allocation.risk_percentage
        
        return (
            f"{direction} {self.symbol} @ ${entry}\n"
            f"Stop Loss: ${stop}\n"
            f"Risk: ${risk:,.2f} ({risk_pct}% of equity)\n"
            f"Conviction: {self.analyst_recommendation.conviction.value}"
        )
