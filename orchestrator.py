"""
Agent Orchestrator - Coordinates multiple technical indicator agents
"""
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime
from agents import MACDCombinedAgent, SMAAgent, RSICombinedAgent, BaseAgent
import concurrent.futures
import os


class AgentOrchestrator:
    """
    Orchestrates the execution of multiple technical indicator agents.
    Manages agent lifecycle, data flow, and result aggregation.
    """

    def __init__(self):
        self.agents: List[BaseAgent] = []
        self.results: Dict[str, Any] = {}
        self.data: pd.DataFrame = None
        self.ticker: str = None
        self.timeframe: str = None

    def initialize_agents(self):
        """
        Initialize all technical indicator agents.
        """
        self.agents = [
            MACDCombinedAgent(),
            SMAAgent(periods=[20, 50]),
            RSICombinedAgent()
        ]
        print(f"Initialized {len(self.agents)} agents")

    def load_data(self, ticker: str, timeframe: str, start_date: str = None, end_date: str = None) -> bool:
        """
        Load price data from CSV file.

        Args:
            ticker: Stock ticker symbol (e.g., 'googl')
            timeframe: Time period (e.g., 'daily', 'monthly')
            start_date: Start date in DD/MM/YYYY format (UK format)
            end_date: End date in DD/MM/YYYY format (UK format)

        Returns:
            True if data loaded successfully, False otherwise
        """
        try:
            # Construct filename
            filename = f"{ticker.lower()}_{timeframe.lower()}.csv"
            filepath = os.path.join("data", filename)

            if not os.path.exists(filepath):
                print(f"Error: File {filepath} not found")
                return False

            # Load CSV
            df = pd.read_csv(filepath)
            df['Date'] = pd.to_datetime(df['Date'])

            # Filter by date range if provided
            if start_date:
                start_dt = datetime.strptime(start_date, "%d/%m/%Y")
                df = df[df['Date'] >= start_dt]

            if end_date:
                end_dt = datetime.strptime(end_date, "%d/%m/%Y")
                df = df[df['Date'] <= end_dt]

            # Sort by date
            df = df.sort_values('Date').reset_index(drop=True)

            self.data = df
            self.ticker = ticker.upper()
            self.timeframe = timeframe.lower()

            print(f"Loaded {len(df)} rows of {self.ticker} {self.timeframe} data")
            print(f"Date range: {df['Date'].min().strftime('%d/%m/%Y')} to {df['Date'].max().strftime('%d/%m/%Y')}")

            return True

        except Exception as e:
            print(f"Error loading data: {e}")
            return False

    def run_agents_sequential(self) -> Dict[str, Any]:
        """
        Run all agents sequentially.

        Returns:
            Dictionary containing results from all agents
        """
        if self.data is None:
            raise ValueError("No data loaded. Call load_data() first.")

        print("\n" + "=" * 60)
        print("STARTING AGENTIC WORKFLOW - SEQUENTIAL EXECUTION")
        print("=" * 60)

        self.results = {
            "ticker": self.ticker,
            "timeframe": self.timeframe,
            "data_points": len(self.data),
            "date_range": {
                "start": self.data['Date'].min().strftime('%d/%m/%Y'),
                "end": self.data['Date'].max().strftime('%d/%m/%Y')
            },
            "agents": {},
            "execution_mode": "sequential"
        }

        for agent in self.agents:
            result = agent.run(self.data)
            self.results["agents"][agent.name] = result

        print("\n" + "=" * 60)
        print("WORKFLOW COMPLETED")
        print("=" * 60)

        return self.results

    def run_agents_parallel(self) -> Dict[str, Any]:
        """
        Run all agents in parallel using ThreadPoolExecutor.

        Returns:
            Dictionary containing results from all agents
        """
        if self.data is None:
            raise ValueError("No data loaded. Call load_data() first.")

        print("\n" + "=" * 60)
        print("STARTING AGENTIC WORKFLOW - PARALLEL EXECUTION")
        print("=" * 60)

        self.results = {
            "ticker": self.ticker,
            "timeframe": self.timeframe,
            "data_points": len(self.data),
            "date_range": {
                "start": self.data['Date'].min().strftime('%d/%m/%Y'),
                "end": self.data['Date'].max().strftime('%d/%m/%Y')
            },
            "agents": {},
            "execution_mode": "parallel"
        }

        # Run agents in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.agents)) as executor:
            # Submit all agent tasks
            future_to_agent = {executor.submit(agent.run, self.data): agent for agent in self.agents}

            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_agent):
                agent = future_to_agent[future]
                try:
                    result = future.result()
                    self.results["agents"][agent.name] = result
                except Exception as e:
                    print(f"Agent {agent.name} generated an exception: {e}")
                    self.results["agents"][agent.name] = {
                        "agent": agent.name,
                        "status": "failed",
                        "error": str(e)
                    }

        print("\n" + "=" * 60)
        print("WORKFLOW COMPLETED")
        print("=" * 60)

        return self.results

    def get_consolidated_signals(self) -> Dict[str, Any]:
        """
        Consolidate signals from all agents into a unified recommendation.

        Returns:
            Dictionary with consolidated trading signals
        """
        if not self.results or "agents" not in self.results:
            return {"error": "No results available. Run agents first."}

        signals = []
        for agent_name, result in self.results["agents"].items():
            if result["status"] == "completed" and result["summary"]:
                signal = result["summary"].get("trading_signal", "NEUTRAL")
                signals.append(signal)

        # Count signals
        buy_count = signals.count("BUY")
        sell_count = signals.count("SELL")
        neutral_count = signals.count("NEUTRAL")

        # Determine overall signal
        total_signals = len(signals)
        if total_signals == 0:
            overall_signal = "NO_DATA"
            confidence = 0
        elif buy_count > sell_count and buy_count >= neutral_count:
            overall_signal = "BUY"
            confidence = round((buy_count / total_signals) * 100, 2)
        elif sell_count > buy_count and sell_count >= neutral_count:
            overall_signal = "SELL"
            confidence = round((sell_count / total_signals) * 100, 2)
        else:
            overall_signal = "NEUTRAL"
            confidence = round((neutral_count / total_signals) * 100, 2)

        return {
            "overall_signal": overall_signal,
            "confidence": confidence,
            "individual_signals": {
                "BUY": buy_count,
                "SELL": sell_count,
                "NEUTRAL": neutral_count
            },
            "total_agents": total_signals
        }

    def print_summary(self):
        """
        Print a formatted summary of all agent results.
        """
        if not self.results:
            print("No results to display")
            return

        print("\n" + "=" * 60)
        print(f"ANALYSIS SUMMARY: {self.results['ticker']} ({self.results['timeframe']})")
        print("=" * 60)
        print(f"Date Range: {self.results['date_range']['start']} to {self.results['date_range']['end']}")
        print(f"Data Points: {self.results['data_points']}")
        print(f"Execution Mode: {self.results['execution_mode']}")
        print("\n" + "-" * 60)

        for agent_name, result in self.results["agents"].items():
            print(f"\n{agent_name.upper()}")
            print("-" * 60)
            print(f"Status: {result['status']}")

            if result['status'] == 'completed' and result['summary']:
                print("\nKey Metrics:")
                for key, value in result['summary'].items():
                    if key != 'parameters' and not isinstance(value, dict):
                        print(f"  {key}: {value}")

                if 'parameters' in result['summary']:
                    print("\nParameters:")
                    for key, value in result['summary']['parameters'].items():
                        print(f"  {key}: {value}")

            elif result['error']:
                print(f"Error: {result['error']}")

        # Print consolidated signals
        print("\n" + "=" * 60)
        print("CONSOLIDATED TRADING SIGNALS")
        print("=" * 60)
        consolidated = self.get_consolidated_signals()
        for key, value in consolidated.items():
            print(f"{key}: {value}")

    def get_combined_dataframe(self) -> pd.DataFrame:
        """
        Get a combined dataframe with all indicator calculations.

        Returns:
            DataFrame with all indicators
        """
        if not self.results or "agents" not in self.results:
            return None

        combined_df = self.data.copy()

        for agent_name, result in self.results["agents"].items():
            if result["status"] == "completed" and result["data"] is not None:
                # Merge indicator columns
                indicator_df = result["data"]
                indicator_cols = [col for col in indicator_df.columns if col not in combined_df.columns]

                for col in indicator_cols:
                    combined_df[col] = indicator_df[col]

        return combined_df
