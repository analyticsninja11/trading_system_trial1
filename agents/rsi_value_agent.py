"""
RSI Value Agent - Calculates RSI on daily timeframe
"""
import pandas as pd
from typing import Dict, Any
from .sub_agent import SubAgent


class RSIValueAgent(SubAgent):
    """
    RSI agent that calculates and returns the actual RSI value on daily timeframe.
    """

    def __init__(self, period: int = 14):
        super().__init__(name="RSI Value Agent")
        self.period = period

    def calculate_rsi(self, df: pd.DataFrame) -> pd.DataFrame:
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

    def process(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Process daily timeframe data and calculate RSI.

        Args:
            df: DataFrame with OHLCV data (daily timeframe)

        Returns:
            Dictionary with RSI value and statistics
        """
        # Calculate RSI
        df = self.calculate_rsi(df)

        # Get RSI values
        rsi_series = df['RSI'].dropna()

        if len(rsi_series) == 0:
            return {
                "rsi_value": None,
                "error": "Unable to calculate RSI"
            }

        # Current RSI value
        current_rsi = float(rsi_series.iloc[-1])

        # Check if RSI is above 90
        is_above_90 = current_rsi > 90

        # Get recent RSI values for trend analysis
        recent_rsi = rsi_series.tail(5).tolist()

        # RSI trend
        if len(rsi_series) >= 2:
            rsi_trend = "Rising" if rsi_series.iloc[-1] > rsi_series.iloc[-2] else "Falling"
        else:
            rsi_trend = "Unknown"

        # Determine RSI zone
        if current_rsi >= 70:
            zone = "Overbought"
        elif current_rsi <= 30:
            zone = "Oversold"
        else:
            zone = "Neutral"

        return {
            "rsi_value": round(current_rsi, 2),
            "is_above_90": is_above_90,
            "rsi_zone": zone,
            "rsi_trend": rsi_trend,
            "recent_rsi_values": [round(float(v), 2) for v in recent_rsi],
            "rsi_stats": {
                "mean": round(float(rsi_series.mean()), 2),
                "max": round(float(rsi_series.max()), 2),
                "min": round(float(rsi_series.min()), 2),
                "std": round(float(rsi_series.std()), 2)
            },
            "parameters": {
                "period": self.period
            }
        }
