"""
MACD (Moving Average Convergence Divergence) Agent - Refactored
Uses unified agent interface and centralized configuration.
"""
import pandas as pd
from typing import Dict, Any
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.unified_agent import UnifiedAgent
from config import MACDConfig, get_config


class MACDAgent(UnifiedAgent):
    """
    Agent specialized in calculating MACD indicator.
    MACD = fast EMA - slow EMA
    Signal Line = signal_period EMA of MACD
    Histogram = MACD - Signal Line

    This refactored version uses:
    - UnifiedAgent base class for consistent interface
    - Centralized configuration for parameters
    - Custom exceptions for error handling
    """

    def __init__(self, config: MACDConfig = None):
        """
        Initialize MACD Agent.

        Args:
            config: MACDConfig instance (uses default if None)
        """
        super().__init__(name="MACD Agent", agent_type="indicator")

        # Use provided config or get default
        if config is None:
            config = get_config().macd

        self.config = config
        self.fast_period = config.fast_period
        self.slow_period = config.slow_period
        self.signal_period = config.signal_period

    def get_minimum_rows(self) -> int:
        """MACD needs at least slow_period + signal_period rows."""
        return self.slow_period + self.signal_period

    def process(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Process data and calculate MACD indicator.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            Dictionary with:
                - data: DataFrame with MACD columns
                - summary: Summary statistics
                - signal: Trading signal
        """
        # Calculate MACD
        result_df = self._calculate_macd(df)

        # Generate summary
        summary = self._generate_summary_from_df(result_df)

        # Extract signal
        signal = self._get_signal_from_summary(summary)

        # Add signal to summary for easy retrieval
        summary["signal"] = signal

        return {
            "data": result_df,
            "summary": summary
        }

    def _calculate_macd(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate MACD, Signal Line, and Histogram.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with MACD columns added
        """
        # Calculate EMAs
        ema_fast = df['Close'].ewm(span=self.fast_period, adjust=False).mean()
        ema_slow = df['Close'].ewm(span=self.slow_period, adjust=False).mean()

        # Calculate MACD line
        df['MACD'] = ema_fast - ema_slow

        # Calculate Signal line
        df['MACD_Signal'] = df['MACD'].ewm(span=self.signal_period, adjust=False).mean()

        # Calculate Histogram
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']

        return df

    def _generate_summary_from_df(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate summary statistics for MACD.

        Args:
            df: DataFrame with MACD calculations

        Returns:
            Dictionary with MACD summary
        """
        latest = df.iloc[-1]
        previous = df.iloc[-2] if len(df) > 1 else latest

        # Determine trend
        if latest['MACD'] > latest['MACD_Signal']:
            trend = "BULLISH"
        else:
            trend = "BEARISH"

        # Check for crossover
        crossover = None
        if previous['MACD'] <= previous['MACD_Signal'] and latest['MACD'] > latest['MACD_Signal']:
            crossover = "BULLISH_CROSSOVER"
        elif previous['MACD'] >= previous['MACD_Signal'] and latest['MACD'] < latest['MACD_Signal']:
            crossover = "BEARISH_CROSSOVER"

        return {
            "latest_macd": round(float(latest['MACD']), 4),
            "latest_signal": round(float(latest['MACD_Signal']), 4),
            "latest_histogram": round(float(latest['MACD_Histogram']), 4),
            "trend": trend,
            "crossover": crossover,
            "parameters": {
                "fast_period": self.fast_period,
                "slow_period": self.slow_period,
                "signal_period": self.signal_period
            }
        }

    def _get_signal_from_summary(self, summary: Dict[str, Any]) -> str:
        """
        Generate trading signal based on MACD summary.

        Args:
            summary: Summary dictionary with crossover information

        Returns:
            Trading signal: "BUY", "SELL", or "NEUTRAL"
        """
        crossover = summary.get("crossover")

        if crossover == "BULLISH_CROSSOVER":
            return "BUY"
        elif crossover == "BEARISH_CROSSOVER":
            return "SELL"
        else:
            return "NEUTRAL"

    def _generate_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Override base class method to use our custom summary generation.

        Args:
            df: DataFrame with calculated indicators

        Returns:
            Summary dictionary
        """
        return self._generate_summary_from_df(df)
