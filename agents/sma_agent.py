"""
SMA (Simple Moving Average) Agent
"""
import pandas as pd
from typing import Dict, Any, List
from .base_agent import BaseAgent


class SMAAgent(BaseAgent):
    """
    Agent specialized in calculating Simple Moving Averages.
    Supports multiple periods (default: 20 and 50).
    """

    def __init__(self, periods: List[int] = None):
        super().__init__(name="SMA Agent")
        self.periods = periods if periods is not None else [20, 50]

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate SMAs for specified periods.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with SMA columns added
        """
        for period in self.periods:
            df[f'SMA_{period}'] = df['Close'].rolling(window=period).mean()

        return df

    def get_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate summary statistics for SMAs.

        Args:
            df: DataFrame with SMA calculations

        Returns:
            Dictionary with SMA summary
        """
        latest = df.iloc[-1]
        summary = {
            "latest_price": round(float(latest['Close']), 2),
            "sma_values": {},
            "price_position": {},
            "trading_signal": self.get_latest_signal(df),
            "parameters": {
                "periods": self.periods
            }
        }

        # Add SMA values and price positions
        for period in self.periods:
            sma_col = f'SMA_{period}'
            sma_value = float(latest[sma_col])
            summary["sma_values"][f"SMA_{period}"] = round(sma_value, 2)

            # Determine if price is above or below SMA
            if latest['Close'] > sma_value:
                summary["price_position"][f"SMA_{period}"] = "ABOVE"
            else:
                summary["price_position"][f"SMA_{period}"] = "BELOW"

        # Check for golden cross or death cross (if we have both 20 and 50 period SMAs)
        if 20 in self.periods and 50 in self.periods:
            sma_20 = float(latest['SMA_20'])
            sma_50 = float(latest['SMA_50'])

            if len(df) > 1:
                prev_sma_20 = float(df.iloc[-2]['SMA_20'])
                prev_sma_50 = float(df.iloc[-2]['SMA_50'])

                if prev_sma_20 <= prev_sma_50 and sma_20 > sma_50:
                    summary["cross_pattern"] = "GOLDEN_CROSS (Bullish)"
                elif prev_sma_20 >= prev_sma_50 and sma_20 < sma_50:
                    summary["cross_pattern"] = "DEATH_CROSS (Bearish)"
                else:
                    summary["cross_pattern"] = None
            else:
                summary["cross_pattern"] = None

        return summary

    def get_latest_signal(self, df: pd.DataFrame) -> str:
        """
        Generate trading signal based on SMA.

        Args:
            df: DataFrame with SMA calculations

        Returns:
            Trading signal: BUY, SELL, or NEUTRAL
        """
        latest = df.iloc[-1]

        # If we have both SMAs, check for golden/death cross
        if 20 in self.periods and 50 in self.periods and len(df) > 1:
            sma_20 = float(latest['SMA_20'])
            sma_50 = float(latest['SMA_50'])
            prev_sma_20 = float(df.iloc[-2]['SMA_20'])
            prev_sma_50 = float(df.iloc[-2]['SMA_50'])

            # Golden cross
            if prev_sma_20 <= prev_sma_50 and sma_20 > sma_50:
                return "BUY"
            # Death cross
            elif prev_sma_20 >= prev_sma_50 and sma_20 < sma_50:
                return "SELL"

        # Otherwise, check if price is above all SMAs (bullish) or below all (bearish)
        above_count = 0
        below_count = 0

        for period in self.periods:
            sma_col = f'SMA_{period}'
            if pd.notna(latest[sma_col]):
                if latest['Close'] > latest[sma_col]:
                    above_count += 1
                else:
                    below_count += 1

        if above_count == len(self.periods):
            return "BUY"
        elif below_count == len(self.periods):
            return "SELL"

        return "NEUTRAL"
