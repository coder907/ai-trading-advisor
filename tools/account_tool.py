"""
Account Information Tool

This tool retrieves account equity information for risk management calculations.
"""

from crewai.tools import tool
import logging

logging.basicConfig(level=logging.INFO)

@tool("Account Info Tool")
def fetch_account_info(account_equity: float) -> str:
    """
    Retrieve current account equity information for risk management calculations.
    This tool returns the total account equity value needed to calculate
    position sizing and risk allocation (0.5% - 2.0% of equity).
    
    Args:
        account_id: Optional account identifier. If not provided, uses the
                   default trading account.
    
    Returns:
        A string containing account equity information in a structured format.
    """
    try:
        logging.info("Account Info Tool: Fetching account information")

        # Mocked account info retrieval
        account_info = {
            "total_equity": account_equity,
            "currency": "USD",
            "risk_limits": {
                "min_risk_pct": 0.5,
                "max_risk_pct": 2.0,
                "min_risk_dollars": account_equity * 0.005,
                "max_risk_dollars": account_equity * 0.02
            }
        }
        
        result = f"""
Account Information:
-------------------
Total Equity: ${account_info['total_equity']:,.2f} {account_info['currency']}

Risk Allocation Limits:
- Minimum Risk (0.5%): ${account_info['risk_limits']['min_risk_dollars']:,.2f}
- Maximum Risk (2.0%): ${account_info['risk_limits']['max_risk_dollars']:,.2f}

Note: Risk per trade must be between 0.5% and 2.0% of total equity.
"""
        
        return result.strip()
    
    except Exception as e:
        return f"Error fetching account information: {str(e)}. Using default values may be necessary."
