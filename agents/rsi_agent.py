"""
RSI (Relative Strength Index) Agent
"""
import pandas as pd
from typing import Dict, Any
from .base_agent import BaseAgent


class RSIAgent(BaseAgent):
    """
    Agent specialized in calculating RSI indicator.
    RSI measures the speed and magnitude of price changes.
    """

    def __init__(self, period: int = 14, overbought: int = 70, oversold: int = 30):
        super().__init__(name="RSI Agent")
        self.period = period
        self.overbought = overbought
        self.oversold = oversold

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate RSI using the standard formula.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with RSI column added
        """
        # Calculate price changes
        delta = df['Close'].diff()

        # Separate gains and losses
        gains = delta.where(delta > 0, 0)
        losses = -delta.where(delta < 0, 0)

        # Calculate average gains and losses
        avg_gains = gains.rolling(window=self.period, min_periods=1).mean()
        avg_losses = losses.rolling(window=self.period, min_periods=1).mean()

        # Calculate RS and RSI
        rs = avg_gains / avg_losses
        df['RSI'] = 100 - (100 / (1 + rs))

        return df

    def get_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate summary statistics for RSI.

        Args:
            df: DataFrame with RSI calculations

        Returns:
            Dictionary with RSI summary
        """
        latest = df.iloc[-1]
        rsi_value = float(latest['RSI'])

        # Determine market condition
        if rsi_value >= self.overbought:
            condition = "OVERBOUGHT"
        elif rsi_value <= self.oversold:
            condition = "OVERSOLD"
        else:
            condition = "NEUTRAL"

        # Calculate RSI statistics over the period
        rsi_series = df['RSI'].dropna()

        signal = self.get_latest_signal(df)

        return {
            "latest_rsi": round(rsi_value, 2),
            "condition": condition,
            "overbought_threshold": self.overbought,
            "oversold_threshold": self.oversold,
            "rsi_stats": {
                "mean": round(float(rsi_series.mean()), 2),
                "max": round(float(rsi_series.max()), 2),
                "min": round(float(rsi_series.min()), 2),
                "std": round(float(rsi_series.std()), 2)
            },
            "trading_signal": signal,
            "parameters": {
                "period": self.period,
                "overbought": self.overbought,
                "oversold": self.oversold
            }
        }

    def get_latest_signal(self, df: pd.DataFrame) -> str:
        """
        Generate trading signal based on RSI.

        Args:
            df: DataFrame with RSI calculations

        Returns:
            Trading signal: BUY, SELL, or NEUTRAL
        """
        latest = df.iloc[-1]
        rsi_value = float(latest['RSI'])

        # Check for divergence from oversold/overbought zones
        if len(df) > 1:
            previous = df.iloc[-2]
            prev_rsi = float(previous['RSI'])

            # Moving out of oversold zone (potential buy)
            if prev_rsi <= self.oversold and rsi_value > self.oversold:
                return "BUY"
            # Moving into overbought zone (potential sell)
            elif prev_rsi < self.overbought and rsi_value >= self.overbought:
                return "SELL"

        # Simple threshold-based signals
        if rsi_value <= self.oversold:
            return "BUY"
        elif rsi_value >= self.overbought:
            return "SELL"

        return "NEUTRAL"
