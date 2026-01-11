"""
MACD (Moving Average Convergence Divergence) Agent
"""
import pandas as pd
from typing import Dict, Any
from .base_agent import BaseAgent


class MACDAgent(BaseAgent):
    """
    Agent specialized in calculating MACD indicator.
    MACD = 12-day EMA - 26-day EMA
    Signal Line = 9-day EMA of MACD
    """

    def __init__(self, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9):
        super().__init__(name="MACD Agent")
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
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

    def get_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
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

        signal = self.get_latest_signal(df)

        return {
            "latest_macd": round(float(latest['MACD']), 4),
            "latest_signal": round(float(latest['MACD_Signal']), 4),
            "latest_histogram": round(float(latest['MACD_Histogram']), 4),
            "trend": trend,
            "crossover": crossover,
            "trading_signal": signal,
            "parameters": {
                "fast_period": self.fast_period,
                "slow_period": self.slow_period,
                "signal_period": self.signal_period
            }
        }

    def get_latest_signal(self, df: pd.DataFrame) -> str:
        """
        Generate trading signal based on MACD.

        Args:
            df: DataFrame with MACD calculations

        Returns:
            Trading signal: BUY, SELL, or NEUTRAL
        """
        latest = df.iloc[-1]
        previous = df.iloc[-2] if len(df) > 1 else latest

        # Bullish crossover
        if previous['MACD'] <= previous['MACD_Signal'] and latest['MACD'] > latest['MACD_Signal']:
            return "BUY"
        # Bearish crossover
        elif previous['MACD'] >= previous['MACD_Signal'] and latest['MACD'] < latest['MACD_Signal']:
            return "SELL"
        else:
            return "NEUTRAL"
