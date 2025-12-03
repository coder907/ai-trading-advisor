"""
Trading Advisor Crew

This module defines the CrewAI workflow for the AI Trading Advisor system.
It loads agent and task configurations from YAML files and orchestrates
the three-agent workflow: Financial Analyst → Trader → Risk Manager.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List

from crewai import Agent, Task, Crew, Process, LLM

from models import (
    AnalystRecommendation,
    TradingSetup,
    RiskAllocation,
    CompleteTradePlan,
    TradeDirection,
    ConvictionLevel,
)
from tools import search_internet, fetch_account_info, scrape_website, analyze_chart, analyze_chart

class TradingAdvisorCrew:
    """
    Orchestrates the AI Trading Advisor workflow with three specialized agents:
    1. Financial Analyst - Analyzes charts and provides directional recommendations
    2. Trader - Creates precise trading setups with entry, stop loss, and targets
    3. Risk Manager - Determines position sizing and risk allocation
    """
    
    def __init__(self, config_dir: str = "config"):
        """
        Initialize the Trading Advisor Crew.
        
        Args:
            config_dir: Directory containing agent and task YAML configurations
        """
        self.config_dir = Path(config_dir)
        self.agents_config = self._load_agents_config()
        self.tasks_config = self._load_tasks_config()

        # Initialize agents
        self.financial_analyst = self._create_agent("financial_analyst_agent")
        self.trader = self._create_agent("trader_agent")
        self.risk_manager = self._create_agent("risk_manager_agent")
        
    def _load_yaml_file(self, filepath: Path) -> Dict[str, Any]:
        """Load and parse a YAML configuration file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise RuntimeError(f"Error loading YAML file {filepath}: {str(e)}")
    
    def _load_agents_config(self) -> Dict[str, Dict[str, Any]]:
        """Load all agent configurations from YAML files."""
        agents_dir = self.config_dir / "agents"
        configs = {}
        
        for yaml_file in agents_dir.glob("*.yaml"):
            config = self._load_yaml_file(yaml_file)
            configs.update(config)
        
        return configs
    
    def _load_tasks_config(self) -> Dict[str, Dict[str, Any]]:
        """Load all task configurations from YAML files."""
        tasks_dir = self.config_dir / "tasks"
        configs = {}
        
        for yaml_file in tasks_dir.glob("*.yaml"):
            config = self._load_yaml_file(yaml_file)
            configs.update(config)
        
        return configs
    
    def _get_llm(self) -> LLM:
        """
        Get the LLM.
        
        Returns:
            LLM instance configured for the model
        """

        return LLM(
            model="gemini/gemini-2.0-flash",
            temperature=0.3,
            top_p=0.9,
            api_key=os.getenv("GOOGLE_API_KEY")
        )

    def _get_tools_for_agent(self, agent_config: Dict[str, Any], llm) -> List:
        """
        Get the appropriate tools for an agent based on configuration.
        
        Args:
            agent_config: Agent configuration dictionary
        
        Returns:
            List of tool instances
        """
        tools = []
        tool_names = agent_config.get("tools", [])
        
        tool_mapping = {
            "analyze_chart": analyze_chart,
            "search_internet": search_internet,
            "scrape_website": scrape_website,
            "fetch_account_info": fetch_account_info,
        }
        
        for tool_name in tool_names:
            if tool_name in tool_mapping:
                tools.append(tool_mapping[tool_name])
        
        return tools
    
    def _create_agent(self, agent_name: str) -> Agent:
        """
        Create an agent from YAML configuration.
        
        Args:
            agent_name: Name of the agent in the configuration
        
        Returns:
            Configured Agent instance
        """
        if agent_name not in self.agents_config:
            raise ValueError(f"Agent configuration not found: {agent_name}")
        
        config = self.agents_config[agent_name]
        llm = self._get_llm()
        tools = self._get_tools_for_agent(config, llm)
        
        agent = Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            llm=llm,
            tools=tools,
            max_iter=config.get("max_iterations", 3),
            verbose=True,
            allow_delegation=False
        )
        
        return agent
    
    def _create_task(
        self,
        task_name: str,
        agent: Agent,
        context: Optional[List[Task]] = None,
        inputs: Optional[Dict[str, Any]] = None
    ) -> Task:
        """
        Create a task from YAML configuration.
        
        Args:
            task_name: Name of the task in the configuration
            agent: Agent to assign the task to
            context: Optional list of previous tasks for context
            inputs: Optional input variables for the task
        
        Returns:
            Configured Task instance
        """
        if task_name not in self.tasks_config:
            raise ValueError(f"Task configuration not found: {task_name}")
        
        config = self.tasks_config[task_name]
        
        # Build task description with inputs if provided
        description = config["description"]
        if inputs:
            description = description.format(**inputs)
        
        task = Task(
            description=description,
            expected_output=config["expected_output"],
            agent=agent,
            context=context or []
        )
        
        return task
    
    def analyze_chart(
        self,
        symbol: str,
        chart_image_path: str,
        account_equity: float,
        user_prompt: Optional[str] = None
    ) -> CompleteTradePlan:
        """
        Execute the complete trading advisor workflow.
        
        Args:
            symbol: Trading symbol (e.g., "ES", "AAPL", "BTCUSD")
            chart_image_path: Path to chart image for analysis
            user_prompt: Optional additional context or instructions
        
        Returns:
            CompleteTradePlan with all agent outputs and executability status
        """
        try:
            inputs = {
                "symbol": symbol,
                "chart_image_path": chart_image_path,
                "account_equity": account_equity,
                "user_prompt": user_prompt or ""
            }

            # Task 1: Financial Analyst analyzes the chart
            analyst_task = self._create_task(
                "financial_analyst_task",
                self.financial_analyst,
                inputs=inputs
            )
            
            # Task 2: Trader creates trading setup based on analyst recommendation
            trader_task = self._create_task(
                "trader_task",
                self.trader,
                context=[analyst_task],
                inputs=inputs
            )
            
            # Task 3: Risk Manager determines position sizing
            risk_manager_task = self._create_task(
                "risk_manager_task",
                self.risk_manager,
                context=[analyst_task, trader_task],
                inputs=inputs
            )
            
            # Create and execute the crew
            crew = Crew(
                agents=[self.financial_analyst, self.trader, self.risk_manager],
                tasks=[analyst_task, trader_task, risk_manager_task],
                process=Process.sequential,
                verbose=True
            )

            crew.kickoff(inputs=inputs)
            
            # Parse the results and create structured output
            # TODO: Have agents return structured JSON/Pydantic models directly
            complete_plan = self._parse_results_to_plan(
                symbol=symbol,
                account_equity=account_equity,
                analyst_result=analyst_task.output,
                trader_result=trader_task.output,
                risk_manager_result=risk_manager_task.output
            )
            
            return complete_plan
            
        except Exception as e:
            return CompleteTradePlan(
                symbol=symbol,
                analyst_recommendation=AnalystRecommendation(
                    direction=TradeDirection.NO_TRADE,
                    conviction=ConvictionLevel.NONE,
                    symbol=symbol,
                    justification=f"Workflow error: {str(e)}"
                ),
                trading_setup=TradingSetup(
                    direction=TradeDirection.NO_TRADE,
                    symbol=symbol,
                    justification="No trade due to workflow error"
                ),
                risk_allocation=RiskAllocation(
                    direction=TradeDirection.NO_TRADE,
                    symbol=symbol,
                    account_equity=account_equity,
                    justification="No risk allocated due to workflow error"
                ),
                workflow_status="ERROR"
            )
    
    def _parse_results_to_plan(
        self,
        symbol: str,
        account_equity: float,
        analyst_result: Any,
        trader_result: Any,
        risk_manager_result: Any
    ) -> CompleteTradePlan:
        """
        Parse agent outputs into a structured CompleteTradePlan.
        
        Args:
            symbol: Trading symbol
            analyst_result: Financial analyst task output
            trader_result: Trader task output
            risk_manager_result: Risk manager task output
        
        Returns:
            Structured CompleteTradePlan object
        """
        # 
        
        try:
            # Parse analyst recommendation
            analyst_text = str(analyst_result.raw if hasattr(analyst_result, 'raw') else analyst_result)
            direction = self._extract_direction(analyst_text)
            conviction = self._extract_conviction(analyst_text)
            
            analyst_recommendation = AnalystRecommendation(
                direction=direction,
                conviction=conviction,
                symbol=symbol,
                justification=analyst_text[:500]  # Truncate for summary
            )
            
            # Parse trading setup
            trader_text = str(trader_result.raw if hasattr(trader_result, 'raw') else trader_result)
            trading_setup = TradingSetup(
                direction=direction,
                symbol=symbol,
                justification=trader_text[:500],
                analyst_recommendation=analyst_recommendation
            )
            
            # Parse risk allocation
            risk_text = str(risk_manager_result.raw if hasattr(risk_manager_result, 'raw') else risk_manager_result)
            risk_allocation = RiskAllocation(
                direction=direction,
                symbol=symbol,
                account_equity=account_equity,
                justification=risk_text[:500],
                trading_setup=trading_setup
            )
            
            # Determine workflow status
            if direction == TradeDirection.NO_TRADE:
                status = "NO_TRADE"
            else:
                status = "COMPLETE"
            
            return CompleteTradePlan(
                symbol=symbol,
                analyst_recommendation=analyst_recommendation,
                trading_setup=trading_setup,
                risk_allocation=risk_allocation,
                workflow_status=status
            )
            
        except Exception as e:
            raise RuntimeError(f"Error parsing agent results: {str(e)}")
    
    def _extract_direction(self, text: str) -> TradeDirection:
        """Extract trade direction from agent output text."""
        text_upper = text.upper()
        if "NO TRADE" in text_upper or "NO_TRADE" in text_upper:
            return TradeDirection.NO_TRADE
        elif "LONG" in text_upper:
            return TradeDirection.LONG
        elif "SHORT" in text_upper:
            return TradeDirection.SHORT
        else:
            return TradeDirection.NO_TRADE
    
    def _extract_conviction(self, text: str) -> ConvictionLevel:
        """Extract conviction level from agent output text."""
        text_upper = text.upper()
        if "HIGH CONVICTION" in text_upper:
            return ConvictionLevel.HIGH
        elif "MEDIUM CONVICTION" in text_upper:
            return ConvictionLevel.MEDIUM
        elif "LOW CONVICTION" in text_upper:
            return ConvictionLevel.LOW
        else:
            return ConvictionLevel.NONE


# Convenience function to create and use the crew
def create_trading_crew(config_dir: str = "config") -> TradingAdvisorCrew:
    """
    Factory function to create a TradingAdvisorCrew instance.
    
    Args:
        config_dir: Directory containing agent and task YAML configurations
    
    Returns:
        Configured TradingAdvisorCrew instance
    """
    return TradingAdvisorCrew(config_dir=config_dir)
