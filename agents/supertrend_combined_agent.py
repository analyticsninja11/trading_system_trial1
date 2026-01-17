"""
Combined Supertrend Agent - Trend following indicator with ATR-based bands
Migrated to UnifiedAgent architecture with centralized configuration.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.unified_agent import UnifiedAgent
from config import SupertrendConfig, get_config


class SupertrendCombinedAgent(UnifiedAgent):
    """
    Comprehensive Supertrend Agent that provides:
    1. ATR (Average True Range) calculation
    2. Supertrend indicator with upper/lower bands
    3. Green/Red signal detection (bullish/bearish)
    4. Trend stability analysis
    5. Distance from Supertrend line
    6. Signal change detection
    7. Trading signals based on trend direction

    Signal Logic:
    - Green: Price is above Supertrend line (bullish trend)
    - Red: Price is below Supertrend line (bearish trend)
    """

    def __init__(self, config: SupertrendConfig = None):
        """
        Initialize Combined Supertrend Agent.

        Args:
            config: SupertrendConfig instance (uses default if None)
        """
        super().__init__(name="Supertrend Combined Agent", agent_type="indicator")

        # Use provided config or get default
        if config is None:
            config = get_config().supertrend

        self.config = config
        self.atr_length = config.atr_length
        self.multiplier = config.atr_multiplier

    def get_minimum_rows(self) -> int:
        """Supertrend needs at least atr_length + 1 rows for ATR calculation."""
        return self.atr_length + 2

    def process(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Process data and calculate Supertrend with comprehensive analysis.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            Dictionary with:
                - data: DataFrame with Supertrend columns
                - summary: Comprehensive Supertrend analysis
        """
        # Calculate ATR
        result_df = self._calculate_atr(df)

        # Calculate Supertrend
        result_df = self._calculate_supertrend(result_df)

        # Generate comprehensive summary
        summary = self._generate_comprehensive_summary(result_df)

        return {
            "data": result_df,
            "summary": summary
        }

    def _calculate_atr(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Average True Range (ATR).

        Args:
            df: DataFrame with OHLC data

        Returns:
            DataFrame with ATR column added
        """
        # True Range calculation
        high_low = df['High'] - df['Low']
        high_close_prev = abs(df['High'] - df['Close'].shift(1))
        low_close_prev = abs(df['Low'] - df['Close'].shift(1))

        # True Range is the max of these three
        true_range = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)

        # ATR is the moving average of True Range
        df['ATR'] = true_range.rolling(window=self.atr_length).mean()

        return df

    def _calculate_supertrend(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Supertrend indicator.

        Args:
            df: DataFrame with OHLC data and ATR

        Returns:
            DataFrame with Supertrend columns added
        """
        # Calculate HL average (midpoint)
        hl_avg = (df['High'] + df['Low']) / 2

        # Basic upper and lower bands
        df['Upper_Band'] = hl_avg + (self.multiplier * df['ATR'])
        df['Lower_Band'] = hl_avg - (self.multiplier * df['ATR'])

        # Initialize Supertrend columns
        df['Supertrend'] = 0.0
        df['Supertrend_Signal'] = 'Red'
        df['Supertrend_Direction'] = -1  # -1 for Red/Bearish, 1 for Green/Bullish

        # Calculate Supertrend iteratively
        for i in range(1, len(df)):
            # Skip if ATR is NaN
            if pd.isna(df['ATR'].iloc[i]):
                continue

            # Adjust Upper Band
            if df['Close'].iloc[i - 1] <= df['Upper_Band'].iloc[i - 1]:
                df.loc[df.index[i], 'Upper_Band'] = min(
                    df['Upper_Band'].iloc[i],
                    df['Upper_Band'].iloc[i - 1]
                )

            # Adjust Lower Band
            if df['Close'].iloc[i - 1] >= df['Lower_Band'].iloc[i - 1]:
                df.loc[df.index[i], 'Lower_Band'] = max(
                    df['Lower_Band'].iloc[i],
                    df['Lower_Band'].iloc[i - 1]
                )

            # Determine Supertrend value and signal
            if df['Close'].iloc[i] > df['Upper_Band'].iloc[i - 1]:
                df.loc[df.index[i], 'Supertrend'] = df['Lower_Band'].iloc[i]
                df.loc[df.index[i], 'Supertrend_Signal'] = 'Green'
                df.loc[df.index[i], 'Supertrend_Direction'] = 1
            elif df['Close'].iloc[i] < df['Lower_Band'].iloc[i - 1]:
                df.loc[df.index[i], 'Supertrend'] = df['Upper_Band'].iloc[i]
                df.loc[df.index[i], 'Supertrend_Signal'] = 'Red'
                df.loc[df.index[i], 'Supertrend_Direction'] = -1
            else:
                # Continue previous trend
                if i > 0 and df['Supertrend_Signal'].iloc[i - 1] == 'Green':
                    df.loc[df.index[i], 'Supertrend'] = df['Lower_Band'].iloc[i]
                    df.loc[df.index[i], 'Supertrend_Signal'] = 'Green'
                    df.loc[df.index[i], 'Supertrend_Direction'] = 1
                else:
                    df.loc[df.index[i], 'Supertrend'] = df['Upper_Band'].iloc[i]
                    df.loc[df.index[i], 'Supertrend_Signal'] = 'Red'
                    df.loc[df.index[i], 'Supertrend_Direction'] = -1

        return df

    def _generate_comprehensive_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate comprehensive Supertrend summary.

        Args:
            df: DataFrame with Supertrend calculations

        Returns:
            Dictionary with Supertrend summary
        """
        latest = df.iloc[-1]

        current_signal = latest['Supertrend_Signal']
        current_supertrend = float(latest['Supertrend'])
        current_close = float(latest['Close'])
        current_atr = float(latest['ATR']) if pd.notna(latest['ATR']) else 0.0

        # Is Green (bullish)?
        is_green = current_signal == 'Green'

        # Distance from Supertrend line
        distance = current_close - current_supertrend
        distance_percent = (distance / current_close) * 100 if current_close != 0 else 0

        # Recent signals for trend analysis
        recent_signals = df['Supertrend_Signal'].tail(5).tolist()

        # Count signal changes (volatility indicator)
        signal_changes = sum(
            1 for i in range(1, len(recent_signals))
            if recent_signals[i] != recent_signals[i - 1]
        )

        # Trend stability
        if signal_changes == 0:
            trend_stability = "Very Stable"
        elif signal_changes == 1:
            trend_stability = "Stable"
        elif signal_changes == 2:
            trend_stability = "Moderate"
        else:
            trend_stability = "Volatile"

        # Trend duration - count consecutive same signals
        trend_duration = 1
        for i in range(len(df) - 2, -1, -1):
            if df['Supertrend_Signal'].iloc[i] == current_signal:
                trend_duration += 1
            else:
                break

        # Generate trading signal
        signal = self._generate_signal(is_green, trend_stability, distance_percent)

        # Band values
        upper_band = float(latest['Upper_Band']) if pd.notna(latest['Upper_Band']) else None
        lower_band = float(latest['Lower_Band']) if pd.notna(latest['Lower_Band']) else None

        return {
            "supertrend_signal": current_signal,
            "is_green": is_green,
            "signal": signal,
            "trading_signal": signal,  # For compatibility
            "current_close": round(current_close, 2),
            "supertrend_value": round(current_supertrend, 2),
            "distance_from_supertrend": round(distance, 2),
            "distance_percent": round(distance_percent, 2),
            "current_atr": round(current_atr, 2),
            "upper_band": round(upper_band, 2) if upper_band else None,
            "lower_band": round(lower_band, 2) if lower_band else None,
            "trend_analysis": {
                "stability": trend_stability,
                "duration": trend_duration,
                "signal_changes_last_5": signal_changes,
                "recent_signals": recent_signals
            },
            "parameters": {
                "atr_length": self.atr_length,
                "multiplier": self.multiplier
            }
        }

    def _generate_signal(self, is_green: bool, stability: str, distance_pct: float) -> str:
        """
        Generate trading signal based on Supertrend.

        Args:
            is_green: Whether current signal is Green (bullish)
            stability: Trend stability assessment
            distance_pct: Percentage distance from Supertrend line

        Returns:
            Trading signal: BUY, SELL, or NEUTRAL
        """
        # Green = bullish = BUY, Red = bearish = SELL
        if is_green:
            return "BUY"
        else:
            return "SELL"

    def _generate_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Override base class method to use our custom summary generation.

        Args:
            df: DataFrame with calculated indicators

        Returns:
            Summary dictionary
        """
        return self._generate_comprehensive_summary(df)


# Example usage and testing
if __name__ == "__main__":
    print("=" * 80)
    print("Supertrend Combined Agent - Test")
    print("=" * 80)

    # Create sample data
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')

    # Simulate price data with trend
    base_price = 100
    trend = np.linspace(0, 30, 100)
    noise = np.random.randn(100) * 2
    close_prices = base_price + trend + noise

    # Create OHLCV dataframe
    df = pd.DataFrame({
        'Date': dates,
        'Open': close_prices * (1 + np.random.uniform(-0.005, 0.005, 100)),
        'High': close_prices * (1 + np.abs(np.random.randn(100)) * 0.015),
        'Low': close_prices * (1 - np.abs(np.random.randn(100)) * 0.015),
        'Close': close_prices,
        'Volume': np.random.randint(1000000, 5000000, 100)
    })

    # Ensure High >= Close and Low <= Close
    df['High'] = df[['High', 'Close', 'Open']].max(axis=1)
    df['Low'] = df[['Low', 'Close', 'Open']].min(axis=1)

    # Test with default config
    print("\n### Test 1: Default Configuration ###")
    agent = SupertrendCombinedAgent()
    result = agent.run(df)

    if result.is_successful():
        print(f"\n{'Status:':<30} {result.status.upper()}")
        print(f"{'Agent:':<30} {result.agent_name}")

        summary = result.summary

        print("\n" + "=" * 80)
        print("SUPERTREND ANALYSIS")
        print("=" * 80)
        print(f"{'Signal:':<30} {summary['supertrend_signal']}")
        print(f"{'Is Green (Bullish):':<30} {summary['is_green']}")
        print(f"{'Trading Signal:':<30} {summary['signal']}")
        print(f"{'Current Close:':<30} ${summary['current_close']}")
        print(f"{'Supertrend Value:':<30} ${summary['supertrend_value']}")
        print(f"{'Distance:':<30} ${summary['distance_from_supertrend']} ({summary['distance_percent']}%)")
        print(f"{'ATR:':<30} {summary['current_atr']}")

        print("\n" + "-" * 80)
        print("TREND ANALYSIS")
        print("-" * 80)
        trend = summary['trend_analysis']
        print(f"{'Stability:':<30} {trend['stability']}")
        print(f"{'Trend Duration:':<30} {trend['duration']} periods")
        print(f"{'Signal Changes (last 5):':<30} {trend['signal_changes_last_5']}")
        print(f"{'Recent Signals:':<30} {', '.join(trend['recent_signals'])}")

        print("\n" + "-" * 80)
        print("BANDS")
        print("-" * 80)
        print(f"{'Upper Band:':<30} ${summary['upper_band']}")
        print(f"{'Lower Band:':<30} ${summary['lower_band']}")

    else:
        print(f"\nError: {result.error}")

    # Test with custom config
    print("\n\n### Test 2: Custom Configuration (ATR: 14, Multiplier: 2.0) ###")
    from config import SupertrendConfig
    custom_config = SupertrendConfig(atr_length=14, atr_multiplier=2.0)
    agent_custom = SupertrendCombinedAgent(config=custom_config)
    result_custom = agent_custom.run(df)

    if result_custom.is_successful():
        summary = result_custom.summary
        print(f"{'Signal:':<30} {summary['supertrend_signal']}")
        print(f"{'Trading Signal:':<30} {summary['signal']}")
        print(f"{'Stability:':<30} {summary['trend_analysis']['stability']}")

    print("\n" + "=" * 80)
    print("TEST COMPLETED")
    print("=" * 80)
