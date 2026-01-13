"""
Base Orchestrator Agent - Coordinates sub-agents and generates BUY signals
Compatible with Google's Agent Development Kit (ADK)
"""
import pandas as pd
from typing import Dict, Any, List
import concurrent.futures
from .macd_combined_agent import MACDCombinedAgent
from .rsi_combined_agent import RSICombinedAgent
from .sma_delta_agent import SMADeltaAgent
from .supertrend_agent import SupertrendAgent


class OrchestratorAgent:
    """
    Base Agent that orchestrates multiple sub-agents and generates BUY signals.

    BUY Signal Logic (2 out of 4 conditions must be met):
    1. MACD Season is either Spring or Summer
    2. RSI is not above 90
    3. SMA delta is either negative and rising or positive and rising for last 2 monthly points
    4. Supertrend indicator is Green
    """

    def __init__(self):
        self.name = "Base Orchestrator Agent"
        self.status = "initialized"

        # Initialize sub-agents
        self.macd_agent = MACDCombinedAgent()
        self.rsi_agent = RSICombinedAgent()
        self.sma_agent = SMADeltaAgent(short_period=6, long_period=12)
        self.supertrend_agent = SupertrendAgent(atr_length=10, multiplier=3.0)

        self.sub_agents = [
            self.macd_agent,
            self.rsi_agent,
            self.sma_agent,
            self.supertrend_agent
        ]

    def run_sub_agents_parallel(self, daily_df: pd.DataFrame, monthly_df: pd.DataFrame = None) -> Dict[str, Any]:
        """
        Run all sub-agents in parallel.

        Args:
            daily_df: DataFrame with daily OHLCV data
            monthly_df: DataFrame with monthly OHLCV data (optional, can be derived)

        Returns:
            Dictionary with results from all sub-agents
        """
        print(f"\n[{self.name}] Starting parallel execution of sub-agents...")

        # If monthly data not provided, resample from daily
        if monthly_df is None:
            monthly_df = self._resample_to_monthly(daily_df)

        results = {}

        # Run agents in parallel using ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            # Submit tasks
            futures = {
                executor.submit(self.macd_agent.run, daily_df): "MACD",
                executor.submit(self.rsi_agent.run, daily_df): "RSI",
                executor.submit(self.sma_agent.run, monthly_df): "SMA",
                executor.submit(self.supertrend_agent.run, daily_df): "Supertrend"
            }

            # Collect results
            for future in concurrent.futures.as_completed(futures):
                agent_type = futures[future]
                try:
                    result = future.result()
                    # Handle AgentResult objects (from UnifiedAgent-based agents like MACDCombinedAgent)
                    if hasattr(result, 'to_dict'):
                        results[agent_type] = result.to_dict()
                    else:
                        results[agent_type] = result
                except Exception as e:
                    print(f"[{self.name}] Error in {agent_type} agent: {e}")
                    results[agent_type] = {
                        "agent": agent_type,
                        "status": "failed",
                        "output": None,
                        "error": str(e)
                    }

        print(f"[{self.name}] All sub-agents completed")
        return results

    def run_sub_agents_sequential(self, daily_df: pd.DataFrame, monthly_df: pd.DataFrame = None) -> Dict[str, Any]:
        """
        Run all sub-agents sequentially.

        Args:
            daily_df: DataFrame with daily OHLCV data
            monthly_df: DataFrame with monthly OHLCV data (optional, can be derived)

        Returns:
            Dictionary with results from all sub-agents
        """
        print(f"\n[{self.name}] Starting sequential execution of sub-agents...")

        # If monthly data not provided, resample from daily
        if monthly_df is None:
            monthly_df = self._resample_to_monthly(daily_df)

        results = {}

        # MACD on daily
        macd_result = self.macd_agent.run(daily_df)
        results["MACD"] = macd_result.to_dict() if hasattr(macd_result, 'to_dict') else macd_result

        # RSI on daily
        rsi_result = self.rsi_agent.run(daily_df)
        results["RSI"] = rsi_result.to_dict() if hasattr(rsi_result, 'to_dict') else rsi_result

        # SMA on monthly
        sma_result = self.sma_agent.run(monthly_df)
        results["SMA"] = sma_result.to_dict() if hasattr(sma_result, 'to_dict') else sma_result

        # Supertrend on daily
        supertrend_result = self.supertrend_agent.run(daily_df)
        results["Supertrend"] = supertrend_result.to_dict() if hasattr(supertrend_result, 'to_dict') else supertrend_result

        print(f"[{self.name}] All sub-agents completed")
        return results

    def evaluate_buy_signal(self, sub_agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate BUY signal based on 2-of-4 condition logic.

        Args:
            sub_agent_results: Results from all sub-agents

        Returns:
            Dictionary with BUY signal evaluation
        """
        print(f"\n[{self.name}] Evaluating BUY signal...")

        conditions = {
            "condition_1_macd_season": False,
            "condition_2_rsi_check": False,
            "condition_3_sma_delta": False,
            "condition_4_supertrend": False
        }

        condition_details = {}

        # Condition 1: MACD Season is Spring or Summer
        if sub_agent_results["MACD"]["status"] == "completed":
            # Combined agent returns summary with seasonal_analysis
            macd_result = sub_agent_results["MACD"]
            if "summary" in macd_result and "seasonal_analysis" in macd_result["summary"]:
                seasonal = macd_result["summary"]["seasonal_analysis"]
                season = seasonal.get("current_season", "Unknown")
                is_bullish = seasonal.get("is_bullish_season", False)
            else:
                # Fallback for old format
                macd_output = macd_result.get("output", {})
                season = macd_output.get("current_season", "Unknown")
                is_bullish = macd_output.get("is_bullish_season", False)

            conditions["condition_1_macd_season"] = season in ["Spring", "Summer"]
            condition_details["macd"] = {
                "season": season,
                "is_bullish": is_bullish,
                "condition_met": conditions["condition_1_macd_season"]
            }

        # Condition 2: RSI is not above 90
        if sub_agent_results["RSI"]["status"] == "completed":
            # Combined agent returns summary with extreme_levels
            rsi_result = sub_agent_results["RSI"]
            if "summary" in rsi_result:
                rsi_summary = rsi_result["summary"]
                rsi_value = rsi_summary.get("rsi_value", 0)
                # Check extreme_levels or direct is_above_90 field
                if "extreme_levels" in rsi_summary:
                    is_above_90 = rsi_summary["extreme_levels"].get("is_above_90", True)
                else:
                    is_above_90 = rsi_summary.get("is_above_90", True)
            else:
                # Fallback for old format
                rsi_output = rsi_result.get("output", {})
                rsi_value = rsi_output.get("rsi_value", 0)
                is_above_90 = rsi_output.get("is_above_90", True)

            conditions["condition_2_rsi_check"] = not is_above_90
            condition_details["rsi"] = {
                "rsi_value": rsi_value,
                "is_above_90": is_above_90,
                "condition_met": conditions["condition_2_rsi_check"]
            }

        # Condition 3: SMA delta is negative and rising OR positive and rising
        if sub_agent_results["SMA"]["status"] == "completed":
            sma_output = sub_agent_results["SMA"]["output"]
            is_favorable = sma_output.get("is_favorable_for_buy", False)
            conditions["condition_3_sma_delta"] = is_favorable
            condition_details["sma"] = {
                "delta": sma_output.get("sma_delta", 0),
                "trend": sma_output.get("sma_delta_trend", "Unknown"),
                "is_rising_last_2_months": sma_output.get("is_rising_last_2_months", False),
                "condition_met": conditions["condition_3_sma_delta"]
            }

        # Condition 4: Supertrend is Green
        if sub_agent_results["Supertrend"]["status"] == "completed":
            supertrend_output = sub_agent_results["Supertrend"]["output"]
            is_green = supertrend_output.get("is_green", False)
            conditions["condition_4_supertrend"] = is_green
            condition_details["supertrend"] = {
                "signal": supertrend_output.get("supertrend_signal", "Red"),
                "is_green": is_green,
                "condition_met": conditions["condition_4_supertrend"]
            }

        # Count conditions met
        conditions_met = sum(conditions.values())

        # BUY signal if 2 or more conditions are met
        buy_signal = conditions_met >= 2

        print(f"[{self.name}] Conditions met: {conditions_met}/4")
        print(f"[{self.name}] BUY Signal: {'YES' if buy_signal else 'NO'}")

        return {
            "buy_signal": buy_signal,
            "conditions_met": conditions_met,
            "conditions_required": 2,
            "individual_conditions": conditions,
            "condition_details": condition_details,
            "recommendation": "BUY" if buy_signal else "HOLD/WAIT"
        }

    def run(self, daily_df: pd.DataFrame, monthly_df: pd.DataFrame = None,
            mode: str = "parallel") -> Dict[str, Any]:
        """
        Execute the orchestrator agent workflow.

        Args:
            daily_df: DataFrame with daily OHLCV data
            monthly_df: DataFrame with monthly OHLCV data (optional)
            mode: Execution mode - "parallel" or "sequential"

        Returns:
            Dictionary with complete analysis and BUY signal
        """
        self.status = "running"

        # Run sub-agents
        if mode == "parallel":
            sub_agent_results = self.run_sub_agents_parallel(daily_df, monthly_df)
        else:
            sub_agent_results = self.run_sub_agents_sequential(daily_df, monthly_df)

        # Evaluate BUY signal
        buy_evaluation = self.evaluate_buy_signal(sub_agent_results)

        self.status = "completed"

        return {
            "orchestrator": self.name,
            "status": self.status,
            "execution_mode": mode,
            "sub_agent_results": sub_agent_results,
            "buy_signal_evaluation": buy_evaluation
        }

    def _resample_to_monthly(self, daily_df: pd.DataFrame) -> pd.DataFrame:
        """
        Resample daily data to monthly.

        Args:
            daily_df: DataFrame with daily OHLCV data

        Returns:
            DataFrame with monthly OHLCV data
        """
        # Ensure Date is datetime and set as index
        df = daily_df.copy()
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)

        # Resample to monthly
        monthly = pd.DataFrame()
        monthly['Open'] = df['Open'].resample('MS').first()
        monthly['High'] = df['High'].resample('MS').max()
        monthly['Low'] = df['Low'].resample('MS').min()
        monthly['Close'] = df['Close'].resample('MS').last()
        monthly['Volume'] = df['Volume'].resample('MS').sum()

        monthly.reset_index(inplace=True)

        return monthly

    def print_summary(self, results: Dict[str, Any]):
        """
        Print a formatted summary of orchestrator results.

        Args:
            results: Results dictionary from run()
        """
        print("\n" + "=" * 80)
        print(f"ORCHESTRATOR SUMMARY: {self.name}")
        print("=" * 80)

        # BUY Signal
        buy_eval = results["buy_signal_evaluation"]
        print(f"\n🎯 BUY SIGNAL: {buy_eval['recommendation']}")
        print(f"   Conditions Met: {buy_eval['conditions_met']}/{buy_eval['conditions_required']} required")

        # Individual conditions
        print("\n📊 Condition Breakdown:")
        for i, (cond_key, cond_value) in enumerate(buy_eval["individual_conditions"].items(), 1):
            status = "✅" if cond_value else "❌"
            cond_name = cond_key.replace("condition_", "").replace("_", " ").title()
            print(f"   {status} Condition {i}: {cond_name}")

        # Sub-agent details
        print("\n🤖 Sub-Agent Results:")
        for agent_name, agent_result in results["sub_agent_results"].items():
            print(f"\n   {agent_name} Agent:")
            if agent_result["status"] == "completed" and agent_result["output"]:
                output = agent_result["output"]
                for key, value in list(output.items())[:5]:  # Show first 5 items
                    if not isinstance(value, dict) and not isinstance(value, list):
                        print(f"      {key}: {value}")
            else:
                print(f"      Status: {agent_result['status']}")
                if agent_result.get("error"):
                    print(f"      Error: {agent_result['error']}")

        print("\n" + "=" * 80)
