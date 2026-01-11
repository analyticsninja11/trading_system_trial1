"""
SMA Delta Agent - Calculates delta between 6-month and 12-month SMAs
"""
import pandas as pd
from typing import Dict, Any
from .sub_agent import SubAgent


class SMADeltaAgent(SubAgent):
    """
    SMA agent that calculates 6-month and 12-month SMAs on monthly timeframe
    and returns the delta between them.
    """

    def __init__(self, short_period: int = 6, long_period: int = 12):
        super().__init__(name="SMA Delta Agent")
        self.short_period = short_period
        self.long_period = long_period

    def calculate_sma(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate SMAs for both periods.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with SMA columns added
        """
        df[f'SMA_{self.short_period}'] = df['Close'].rolling(window=self.short_period).mean()
        df[f'SMA_{self.long_period}'] = df['Close'].rolling(window=self.long_period).mean()

        # Calculate delta
        df['SMA_Delta'] = df[f'SMA_{self.short_period}'] - df[f'SMA_{self.long_period}']

        return df

    def process(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Process monthly timeframe data and calculate SMA delta.

        Args:
            df: DataFrame with OHLCV data (monthly timeframe)

        Returns:
            Dictionary with SMA delta and trend analysis
        """
        # Calculate SMAs
        df = self.calculate_sma(df)

        # Get delta values
        delta_series = df['SMA_Delta'].dropna()

        if len(delta_series) < 2:
            return {
                "sma_delta": None,
                "error": f"Insufficient data (need at least {self.long_period} monthly points)"
            }

        # Current delta
        current_delta = float(delta_series.iloc[-1])
        previous_delta = float(delta_series.iloc[-2])

        # Check if delta is rising
        is_rising = current_delta > previous_delta

        # Check if delta is positive or negative
        is_positive = current_delta > 0

        # Determine trend
        if is_positive and is_rising:
            trend = "Positive and Rising"
            is_favorable = True
        elif not is_positive and is_rising:
            trend = "Negative and Rising"
            is_favorable = True
        elif is_positive and not is_rising:
            trend = "Positive and Falling"
            is_favorable = False
        else:
            trend = "Negative and Falling"
            is_favorable = False

        # Get last 2 monthly delta values for verification
        last_2_deltas = delta_series.tail(2).tolist()

        # Check if rising for last 2 monthly points
        is_rising_last_2 = len(last_2_deltas) >= 2 and last_2_deltas[-1] > last_2_deltas[-2]

        # Get current SMA values
        current_sma_short = float(df[f'SMA_{self.short_period}'].iloc[-1])
        current_sma_long = float(df[f'SMA_{self.long_period}'].iloc[-1])

        return {
            "sma_delta": round(current_delta, 2),
            "sma_delta_trend": trend,
            "is_delta_rising": is_rising,
            "is_delta_positive": is_positive,
            "is_favorable_for_buy": is_favorable,
            "is_rising_last_2_months": is_rising_last_2,
            "last_2_monthly_deltas": [round(float(v), 2) for v in last_2_deltas],
            "current_sma_values": {
                f"sma_{self.short_period}": round(current_sma_short, 2),
                f"sma_{self.long_period}": round(current_sma_long, 2)
            },
            "parameters": {
                "short_period_months": self.short_period,
                "long_period_months": self.long_period
            }
        }
