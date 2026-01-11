"""
Supertrend Agent - Calculates Supertrend indicator on daily timeframe
"""
import pandas as pd
import numpy as np
from typing import Dict, Any
from .sub_agent import SubAgent


class SupertrendAgent(SubAgent):
    """
    Supertrend agent that calculates the indicator and returns Green/Red signal.

    Green: Closing price is above Supertrend line (bullish)
    Red: Closing price is below Supertrend line (bearish)
    """

    def __init__(self, atr_length: int = 10, multiplier: float = 3.0):
        super().__init__(name="Supertrend Agent")
        self.atr_length = atr_length
        self.multiplier = multiplier

    def calculate_atr(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Average True Range (ATR).

        Args:
            df: DataFrame with OHLC data

        Returns:
            DataFrame with ATR column added
        """
        # True Range calculation
        df['H-L'] = df['High'] - df['Low']
        df['H-PC'] = abs(df['High'] - df['Close'].shift(1))
        df['L-PC'] = abs(df['Low'] - df['Close'].shift(1))

        df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)

        # ATR is the moving average of True Range
        df['ATR'] = df['TR'].rolling(window=self.atr_length).mean()

        # Clean up intermediate columns
        df.drop(['H-L', 'H-PC', 'L-PC', 'TR'], axis=1, inplace=True)

        return df

    def calculate_supertrend(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Supertrend indicator.

        Args:
            df: DataFrame with OHLC data and ATR

        Returns:
            DataFrame with Supertrend columns added
        """
        # Calculate basic bands
        df['HL_AVG'] = (df['High'] + df['Low']) / 2

        # Upper and Lower bands
        df['Upper_Band'] = df['HL_AVG'] + (self.multiplier * df['ATR'])
        df['Lower_Band'] = df['HL_AVG'] - (self.multiplier * df['ATR'])

        # Initialize Supertrend
        df['Supertrend'] = 0.0
        df['Supertrend_Signal'] = 'Red'

        # Calculate Supertrend
        for i in range(1, len(df)):
            # Adjust bands based on previous values
            if df['Close'].iloc[i - 1] <= df['Upper_Band'].iloc[i - 1]:
                df.loc[df.index[i], 'Upper_Band'] = min(df['Upper_Band'].iloc[i], df['Upper_Band'].iloc[i - 1])

            if df['Close'].iloc[i - 1] >= df['Lower_Band'].iloc[i - 1]:
                df.loc[df.index[i], 'Lower_Band'] = max(df['Lower_Band'].iloc[i], df['Lower_Band'].iloc[i - 1])

            # Determine Supertrend value and signal
            if df['Close'].iloc[i] > df['Upper_Band'].iloc[i - 1]:
                df.loc[df.index[i], 'Supertrend'] = df['Lower_Band'].iloc[i]
                df.loc[df.index[i], 'Supertrend_Signal'] = 'Green'
            elif df['Close'].iloc[i] < df['Lower_Band'].iloc[i - 1]:
                df.loc[df.index[i], 'Supertrend'] = df['Upper_Band'].iloc[i]
                df.loc[df.index[i], 'Supertrend_Signal'] = 'Red'
            else:
                # Continue previous trend
                if df['Supertrend_Signal'].iloc[i - 1] == 'Green':
                    df.loc[df.index[i], 'Supertrend'] = df['Lower_Band'].iloc[i]
                    df.loc[df.index[i], 'Supertrend_Signal'] = 'Green'
                else:
                    df.loc[df.index[i], 'Supertrend'] = df['Upper_Band'].iloc[i]
                    df.loc[df.index[i], 'Supertrend_Signal'] = 'Red'

        return df

    def process(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Process daily timeframe data and calculate Supertrend.

        Args:
            df: DataFrame with OHLCV data (daily timeframe)

        Returns:
            Dictionary with Supertrend signal (Green/Red)
        """
        # Calculate ATR
        df = self.calculate_atr(df)

        # Calculate Supertrend
        df = self.calculate_supertrend(df)

        # Get current signal
        current_signal = df['Supertrend_Signal'].iloc[-1]
        current_supertrend_value = float(df['Supertrend'].iloc[-1])
        current_close = float(df['Close'].iloc[-1])
        current_atr = float(df['ATR'].iloc[-1])

        # Check if signal is Green (bullish)
        is_green = current_signal == 'Green'

        # Get recent signals for trend analysis
        recent_signals = df['Supertrend_Signal'].tail(5).tolist()

        # Count signal changes (volatility indicator)
        signal_changes = sum(1 for i in range(1, len(recent_signals))
                            if recent_signals[i] != recent_signals[i-1])

        # Distance from Supertrend line
        distance = current_close - current_supertrend_value
        distance_percent = (distance / current_close) * 100

        return {
            "supertrend_signal": current_signal,
            "is_green": is_green,
            "current_close": round(current_close, 2),
            "supertrend_value": round(current_supertrend_value, 2),
            "distance_from_supertrend": round(distance, 2),
            "distance_percent": round(distance_percent, 2),
            "current_atr": round(current_atr, 2),
            "recent_signals": recent_signals,
            "signal_changes_last_5": signal_changes,
            "trend_stability": "Stable" if signal_changes <= 1 else "Volatile",
            "parameters": {
                "atr_length": self.atr_length,
                "multiplier": self.multiplier
            }
        }
