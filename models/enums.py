"""
Enumerations for Trading Advisor Models

This module defines common enumerations used across the trading advisor system.
"""

from enum import Enum


class TradeDirection(str, Enum):
    """Enumeration of possible trade directions."""
    LONG = "LONG"
    SHORT = "SHORT"
    NO_TRADE = "NO_TRADE"


class ConvictionLevel(str, Enum):
    """Enumeration of conviction levels for trade recommendations."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    NONE = "NONE" # Used when NO_TRADE
