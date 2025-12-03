"""
Supporting Models for Trading Analysis

This module contains supporting data models used by the main trading models.
"""

from pydantic import BaseModel, Field
from typing import Optional


class TechnicalFactors(BaseModel):
    """Technical analysis factors supporting the trade recommendation."""
    trend: Optional[str] = Field(None, description="Overall trend assessment (e.g., 'uptrend', 'downtrend', 'sideways')")
    momentum: Optional[str] = Field(None, description="Momentum indicators assessment")
    volume: Optional[str] = Field(None, description="Volume behavior analysis")
    support_resistance: Optional[str] = Field(None, description="Key support and resistance levels")
    chart_patterns: Optional[str] = Field(None, description="Identified chart patterns")
    volatility: Optional[str] = Field(None, description="Volatility assessment")
    breakouts: Optional[str] = Field(None, description="Breakout or breakdown observations")


class FundamentalFactors(BaseModel):
    """Fundamental and macroeconomic factors supporting the recommendation."""
    earnings: Optional[str] = Field(None, description="Earnings-related information")
    macro_data: Optional[str] = Field(None, description="Macroeconomic data points")
    news: Optional[str] = Field(None, description="Notable news or events")
    sector_conditions: Optional[str] = Field(None, description="Sector-level conditions")


class PriceLevel(BaseModel):
    """Represents a price level with justification."""
    price: float = Field(..., gt=0, description="Price level")
    justification: str = Field(..., description="Reasoning for this price level")
