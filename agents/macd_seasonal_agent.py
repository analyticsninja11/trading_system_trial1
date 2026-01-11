"""
MACD Seasonal Agent - Identifies market seasons based on MACD histogram
"""
import pandas as pd
import numpy as np
from typing import Dict, Any
from .sub_agent import SubAgent


class MACDSeasonalAgent(SubAgent):
    """
    MACD agent that identifies seasons based on histogram patterns.

    Seasons:
    - Spring: Histogram < 0, two consecutive bars increasing
    - Summer: Histogram > 0, two consecutive bars increasing
    - Autumn: Histogram > 0, two consecutive bars decreasing
    - Winter: Histogram < 0, two consecutive bars decreasing
    """

    def __init__(self, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9):
        super().__init__(name="MACD Seasonal Agent")
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period

    def calculate_macd(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate MACD indicator."""
        # Calculate EMAs
        ema_fast = df['Close'].ewm(span=self.fast_period, adjust=False).mean()
        ema_slow = df['Close'].ewm(span=self.slow_period, adjust=False).mean()

        # MACD line
        df['MACD'] = ema_fast - ema_slow

        # Signal line
        df['MACD_Signal'] = df['MACD'].ewm(span=self.signal_period, adjust=False).mean()

        # Histogram
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']

        return df

    def identify_season(self, histogram_values: pd.Series) -> str:
        """
        Identify the current season based on histogram pattern.

        Args:
            histogram_values: Series of last 3 histogram values

        Returns:
            Season name: Spring, Summer, Autumn, or Winter
        """
        if len(histogram_values) < 3:
            return "Unknown"

        current = histogram_values.iloc[-1]
        prev1 = histogram_values.iloc[-2]
        prev2 = histogram_values.iloc[-3]

        # Check if two consecutive bars are increasing
        increasing = (prev1 > prev2) and (current > prev1)

        # Check if two consecutive bars are decreasing
        decreasing = (prev1 < prev2) and (current < prev1)

        # Determine season
        if current < 0 and increasing:
            return "Spring"
        elif current > 0 and increasing:
            return "Summer"
        elif current > 0 and decreasing:
            return "Autumn"
        elif current < 0 and decreasing:
            return "Winter"
        else:
            return "Neutral"

    def process(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Process daily timeframe data and identify seasons.

        Args:
            df: DataFrame with OHLCV data (daily timeframe)

        Returns:
            Dictionary with seasonal analysis
        """
        # Calculate MACD
        df = self.calculate_macd(df)

        # Get histogram values
        histogram = df['MACD_Histogram'].dropna()

        if len(histogram) < 3:
            return {
                "season": "Unknown",
                "error": "Insufficient data (need at least 3 points)"
            }

        # Identify current season
        current_season = self.identify_season(histogram.tail(3))

        # Get recent histogram values for context
        recent_values = histogram.tail(5).tolist()

        # Calculate season statistics over the entire period
        seasons_list = []
        for i in range(2, len(histogram)):
            season = self.identify_season(histogram.iloc[i-2:i+1])
            seasons_list.append(season)

        # Count seasons
        from collections import Counter
        season_counts = Counter(seasons_list)

        return {
            "current_season": current_season,
            "latest_histogram": round(float(histogram.iloc[-1]), 4),
            "histogram_trend": "Increasing" if histogram.iloc[-1] > histogram.iloc[-2] else "Decreasing",
            "recent_histogram_values": [round(float(v), 4) for v in recent_values],
            "season_distribution": dict(season_counts),
            "is_bullish_season": current_season in ["Spring", "Summer"],
            "parameters": {
                "fast_period": self.fast_period,
                "slow_period": self.slow_period,
                "signal_period": self.signal_period
            }
        }
