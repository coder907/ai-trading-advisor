"""
Trading Advisor Models

This package contains all Pydantic models for the AI Trading Advisor system.
Models are organized by agent responsibility and functionality.
"""

# Enumerations
from .enums import TradeDirection, ConvictionLevel

# Base models
from .base import TechnicalFactors, FundamentalFactors, PriceLevel

# Agent output models
from .analyst import AnalystRecommendation
from .trader import TradingSetup
from .risk_manager import RiskAllocation

# Workflow models
from .trade_plan import CompleteTradePlan

__all__ = [
    "TradeDirection",
    "ConvictionLevel",
    "TechnicalFactors",
    "FundamentalFactors",
    "PriceLevel",
    "AnalystRecommendation",
    "TradingSetup",
    "RiskAllocation",
    "CompleteTradePlan",
]
