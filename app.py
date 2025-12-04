"""
AI Trading Advisor - Main Application

This module provides a Gradio web interface for the AI Trading Advisor system.
Users can upload chart screenshots, specify account equity, and provide custom
prompts to receive comprehensive trade recommendations from the multi-agent workflow.
"""

import os
import gradio as gr
import logging
from crew import create_trading_crew
from dotenv import load_dotenv
from models import CompleteTradePlan
from typing import Optional

logging.basicConfig(level=logging.INFO)

# Load environment variables from .env file
load_dotenv()

def _ensure_env_key(key_name: str):
    value = os.getenv(key_name)
    if not value:
        raise ValueError(
            f"{key_name} environment variable is not set.\n"
            f"Please create a .env file in the project root with: {key_name}=<your_value_here>"
        )
    os.environ[key_name] = value

_ensure_env_key("GOOGLE_API_KEY")
_ensure_env_key("SERPER_API_KEY")

class TradingAdvisorApp:
    """Main application class for the AI Trading Advisor Gradio interface."""
    
    def __init__(self):
        """Initialize the Trading Advisor application."""
        self.crew = create_trading_crew()
    
    def analyze_trade(
        self,
        chart_image_path,
        symbol: str,
        account_equity: float,
        user_prompt: Optional[str] = None
    ) -> str:
        """
        Analyze a trading opportunity using the multi-agent workflow.
        
        Args:
            chart_image_path: Uploaded chart screenshot file path
            symbol: Trading symbol (e.g., "ES", "AAPL", "BTCUSD")
            account_equity: Total account equity in dollars
            user_prompt: Optional custom instructions or context
        
        Returns:
            Formatted trade recommendation text
        """
        try:
            # Validate inputs and collect all errors
            validation_errors = []
            
            if not symbol:
                validation_errors.append("Please provide a trading symbol (e.g., ES, AAPL, BTCUSD)")
            
            if chart_image_path is None:
                validation_errors.append("Please upload a chart screenshot")
            elif not chart_image_path.lower().endswith((".png", ".jpg", ".jpeg")):
                validation_errors.append("Unsupported image format. Please upload a PNG or JPG image.")

            if account_equity is None or account_equity <= 0:
                validation_errors.append("Account equity must be provided and greater than 0")
            
            # If there are validation errors, return them all
            if validation_errors:
                error_output = "❌ VALIDATION ERRORS\n"
                error_output += "=" * 60 + "\n"
                for i, error in enumerate(validation_errors, 1):
                    error_output += f"{i}. {error}\n"
                return error_output
            
            # Execute the workflow
            output_text = "🔄 Analyzing chart...\n\n"
            output_text += "=" * 60 + "\n"
            output_text += f"Symbol: {symbol.upper()}\n"
            output_text += f"Account Equity: ${account_equity:,.2f}\n"
            if user_prompt:
                output_text += f"User Prompt: {user_prompt}\n"
            output_text += "=" * 60 + "\n\n"

            result: CompleteTradePlan = self.crew.analyze_chart(
                symbol=symbol.upper(),
                chart_image_path=chart_image_path,
                account_equity=account_equity,
                user_prompt=f"\n\nUser Instructions:\n{user_prompt}" if user_prompt else ""
            )
            
            # Format the output
            output_text += self._format_trade_plan(result)
            
            return output_text
            
        except Exception as e:
            return f"❌ Error during analysis:\n\n{str(e)}\n\nPlease check your inputs and try again."
    
    def _format_trade_plan(self, plan: CompleteTradePlan) -> str:
        """
        Format a CompleteTradePlan into a readable text output.
        
        Args:
            plan: Complete trade plan from the workflow
        
        Returns:
            Formatted trade plan text
        """
        output = []
        
        # Header
        output.append("📊 TRADING ADVISOR ANALYSIS COMPLETE")
        output.append("=" * 60)
        output.append("")
        
        # Workflow Status
        if plan.workflow_status == "NO_TRADE":
            output.append("⛔ NO TRADE RECOMMENDATION")
        elif plan.workflow_status == "ERROR":
            output.append("❌ WORKFLOW ERROR")
        elif plan.is_executable:
            output.append("✅ TRADE RECOMMENDATION (EXECUTABLE)")
        else:
            output.append("⚠️  TRADE RECOMMENDATION (INCOMPLETE)")
        
        output.append("")
        output.append("=" * 60)
        output.append("")
        
        # Financial Analyst Section
        output.append("📈 FINANCIAL ANALYST RECOMMENDATION")
        output.append("-" * 60)
        analyst = plan.analyst_recommendation
        
        output.append(f"Direction: {analyst.direction.value}")
        output.append(f"Conviction: {analyst.conviction.value}")
        output.append("")
        output.append("Analysis:")
        output.append(analyst.justification)
        
        if analyst.key_observations:
            output.append("")
            output.append("Key Observations:")
            for obs in analyst.key_observations:
                output.append(f"  • {obs}")
        
        output.append("")
        output.append("=" * 60)
        output.append("")
        
        # Trader Section (only if actionable)
        if plan.trading_setup.is_actionable:
            output.append("🎯 TRADING SETUP")
            output.append("-" * 60)
            setup = plan.trading_setup
            
            output.append(f"Direction: {setup.direction.value}")
            
            if setup.entry:
                output.append(f"Entry Price: ${setup.entry.price:.2f}")
                output.append(f"  Rationale: {setup.entry.justification}")
            
            if setup.stop_loss:
                output.append(f"Stop Loss: ${setup.stop_loss.price:.2f}")
                output.append(f"  Rationale: {setup.stop_loss.justification}")
            
            if setup.take_profit_targets:
                output.append("Take Profit Targets:")
                for i, tp in enumerate(setup.take_profit_targets, 1):
                    output.append(f"  Target {i}: ${tp.price:.2f}")
                    output.append(f"    Rationale: {tp.justification}")
            
            if setup.reward_to_risk_ratio:
                output.append(f"Reward-to-Risk Ratio: {setup.reward_to_risk_ratio:.2f}:1")
            
            if setup.risk_per_share:
                output.append(f"Risk per Share: ${setup.risk_per_share:.2f}")
            
            output.append("")
            output.append("Setup Justification:")
            output.append(setup.justification)
            
            if setup.chart_structure:
                output.append("")
                output.append("Chart Structure Analysis:")
                output.append(setup.chart_structure)
            
            output.append("")
            output.append("=" * 60)
            output.append("")
        
        # Risk Manager Section
        output.append("💰 RISK MANAGEMENT & POSITION SIZING")
        output.append("-" * 60)
        risk = plan.risk_allocation
        
        if risk.is_actionable:
            output.append(f"Account Equity: ${risk.account_equity:,.2f}")
            output.append(f"Risk Percentage: {risk.risk_percentage:.2f}%")
            output.append(f"Risk Amount: ${risk.risk_amount_dollars:,.2f}")
            
            if risk.position_size_shares:
                output.append(f"Position Size: {risk.position_size_shares:.2f} shares")
            
            if risk.position_value_dollars:
                output.append(f"Position Value: ${risk.position_value_dollars:,.2f}")
            
            if risk.conviction_assessment:
                output.append(f"Conviction Assessment: {risk.conviction_assessment.value}")
            
            if risk.setup_quality_assessment:
                output.append(f"Setup Quality: {risk.setup_quality_assessment}")
            
            # Risk limits check
            if risk.risk_limits_met:
                output.append("")
                output.append("✅ Risk limits met (0.5% - 2.0% of equity)")
            else:
                output.append("")
                output.append("⚠️  WARNING: Risk limits not met!")
        else:
            output.append("NO RISK ALLOCATED (NO TRADE)")
        
        output.append("")
        output.append("Risk Allocation Justification:")
        output.append(risk.justification)
        
        output.append("")
        output.append("=" * 60)
        output.append("")
        
        # Summary
        output.append("📋 EXECUTIVE SUMMARY")
        output.append("-" * 60)
        output.append(plan.summary)
        
        output.append("")
        output.append("=" * 60)
        output.append(f"Generated: {plan.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "\n".join(output)
    
    def launch(self, share: bool = False):
        """
        Launch the Gradio interface.
        
        Args:
            share: Whether to create a public shareable link
        """

        with gr.Blocks(title="AI Trading Advisor") as interface:
            
            gr.Markdown(
                """
                # 📊 AI Trading Advisor
                
                Upload a chart screenshot and receive comprehensive trade recommendations 
                from a multi-agent AI system including technical analysis, trade setup, 
                and risk management guidance.
                
                **Workflow:** Financial Analyst → Trader → Risk Manager
                """
            )
            
            with gr.Row():
                # Left Column - Inputs
                with gr.Column(scale=1):
                    gr.Markdown("### 📥 Inputs")
                    
                    chart_image = gr.Image(
                        label="Chart Screenshot",
                        type="filepath",
                        height=300
                    )
                    
                    symbol_input = gr.Textbox(
                        label="Trading Symbol",
                        placeholder="e.g., ES, BTCUSD, EURUSD",
                        value="ES"
                    )
                    
                    equity_input = gr.Number(
                        label="Account Equity ($)",
                        placeholder="e.g., 100000",
                        value=100000,
                        minimum=1,
                        step=1000
                    )
                    
                    user_prompt = gr.Textbox(
                        label="Custom Instructions (Optional)",
                        placeholder="Add any specific instructions or context for the analysis...",
                        lines=4
                    )
                    
                    analyze_btn = gr.Button(
                        "🚀 Analyze Chart",
                        variant="primary",
                        size="lg"
                    )
                    
                    gr.Markdown(
                        """
                        ---
                        **⚠️ Disclaimer:** This is an AI-powered analysis tool for educational 
                        purposes only. Not financial advice. Always do your own research and 
                        consult with licensed financial professionals before trading.
                        """
                    )
                
                # Right Column - Output
                with gr.Column(scale=1):
                    gr.Markdown("### 📤 Trade Recommendation")
                    
                    output_text = gr.Textbox(
                        label="Analysis Results",
                        lines=30,
                        max_lines=50,
                        show_label=False,
                        interactive=False
                    )

            # Connect the analyze button
            analyze_btn.click(
                fn=self.analyze_trade,
                inputs=[chart_image, symbol_input, equity_input, user_prompt],
                outputs=output_text
            )
            
            # Examples section
            gr.Markdown("### 💡 Example Symbols")
            gr.Markdown(
                """
                - **Indices:** ES, YM, NQ, RTY
                - **Stocks:** AAPL, GOOGL, MSFT, NVDA, TSLA
                - **Crypto:** BTCUSD, ETHUSD, SOLUSD
                - **Forex:** EURUSD, GBPUSD, USDJPY
                - **Metals:** XAUUSD, XAGUSD, XPTUSD
                - **Commodities**: KC, CC, OJ
                """
            )
        
        # Launch the interface
        interface.launch(
            server_name="localhost",
            server_port=7860,
            theme=gr.themes.Ocean(),
            show_error=True
        )


def main():
    """Main entry point for the application."""
    print("🚀 Starting AI Trading Advisor...")
    print("=" * 60)
    print("Initializing multi-agent workflow...")
    print("  - Financial Analyst Agent")
    print("  - Trader Agent")
    print("  - Risk Manager Agent")
    print("=" * 60)
    
    try:
        app = TradingAdvisorApp()
        print("✅ Application initialized successfully!")
        print("\n🌐 Launching Gradio interface...")
        app.launch()
    except Exception as e:
        print(f"\n❌ Error starting application: {str(e)}")
        raise


if __name__ == "__main__":
    main()
