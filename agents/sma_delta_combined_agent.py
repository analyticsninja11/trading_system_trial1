"""
Combined SMA Delta Agent - Monthly SMA delta analysis for trend detection
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
from config import SMADeltaConfig, get_config


class SMADeltaCombinedAgent(UnifiedAgent):
    """
    Comprehensive SMA Delta Agent that provides:
    1. Short-term and long-term SMA calculation (typically 6 and 12 months)
    2. Delta (difference) between short and long SMAs
    3. Delta trend analysis (rising/falling)
    4. Favorable/unfavorable assessment for trading
    5. Historical delta analysis
    6. Trading signals based on delta direction

    Best used with monthly timeframe data.

    Signal Logic:
    - Delta Rising: Short SMA gaining on Long SMA (bullish momentum)
    - Delta Falling: Short SMA losing to Long SMA (bearish momentum)
    - Positive Delta: Short SMA > Long SMA (bullish)
    - Negative Delta: Short SMA < Long SMA (bearish)
    """

    def __init__(self, config: SMADeltaConfig = None):
        """
        Initialize Combined SMA Delta Agent.

        Args:
            config: SMADeltaConfig instance (uses default if None)
        """
        super().__init__(name="SMA Delta Combined Agent", agent_type="indicator")

        # Use provided config or get default
        if config is None:
            config = get_config().sma_delta

        self.config = config
        self.short_period = config.short_lookback_months
        self.long_period = config.long_lookback_months

    def get_minimum_rows(self) -> int:
        """SMA Delta needs at least long_period + 1 rows."""
        return self.long_period + 1

    def process(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Process data and calculate SMA Delta with comprehensive analysis.

        Args:
            df: DataFrame with OHLCV data (preferably monthly timeframe)

        Returns:
            Dictionary with:
                - data: DataFrame with SMA and Delta columns
                - summary: Comprehensive SMA Delta analysis
        """
        # Calculate SMAs and Delta
        result_df = self._calculate_sma_delta(df)

        # Generate comprehensive summary
        summary = self._generate_comprehensive_summary(result_df)

        return {
            "data": result_df,
            "summary": summary
        }

    def _calculate_sma_delta(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate SMAs and their delta.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with SMA and Delta columns added
        """
        # Calculate short and long SMAs
        df[f'SMA_{self.short_period}'] = df['Close'].rolling(window=self.short_period).mean()
        df[f'SMA_{self.long_period}'] = df['Close'].rolling(window=self.long_period).mean()

        # Calculate delta (short - long)
        df['SMA_Delta'] = df[f'SMA_{self.short_period}'] - df[f'SMA_{self.long_period}']

        # Calculate delta change (current - previous)
        df['SMA_Delta_Change'] = df['SMA_Delta'].diff()

        # Calculate percentage delta relative to long SMA
        df['SMA_Delta_Percent'] = (df['SMA_Delta'] / df[f'SMA_{self.long_period}']) * 100

        return df

    def _generate_comprehensive_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate comprehensive SMA Delta summary.

        Args:
            df: DataFrame with SMA Delta calculations

        Returns:
            Dictionary with SMA Delta summary
        """
        # Get delta series (excluding NaN)
        delta_series = df['SMA_Delta'].dropna()

        if len(delta_series) < 2:
            return {
                "error": f"Insufficient data (need at least {self.long_period + 1} data points)",
                "signal": "NEUTRAL",
                "sma_delta": None
            }

        latest = df.iloc[-1]
        previous = df.iloc[-2]

        # Current values
        current_delta = float(latest['SMA_Delta'])
        previous_delta = float(previous['SMA_Delta'])
        current_close = float(latest['Close'])

        # SMA values
        short_sma = float(latest[f'SMA_{self.short_period}'])
        long_sma = float(latest[f'SMA_{self.long_period}'])

        # Delta analysis
        is_rising = current_delta > previous_delta
        is_positive = current_delta > 0

        # Delta percent
        delta_percent = float(latest['SMA_Delta_Percent']) if pd.notna(latest['SMA_Delta_Percent']) else 0

        # Determine trend description
        if is_positive and is_rising:
            trend = "Positive and Rising"
            trend_strength = "STRONGLY_BULLISH"
        elif not is_positive and is_rising:
            trend = "Negative but Rising"
            trend_strength = "BULLISH"
        elif is_positive and not is_rising:
            trend = "Positive but Falling"
            trend_strength = "BEARISH"
        else:
            trend = "Negative and Falling"
            trend_strength = "STRONGLY_BEARISH"

        # Is favorable for buy?
        is_favorable = is_rising

        # Get last N delta values for analysis
        last_deltas = delta_series.tail(5).tolist()
        last_2_deltas = delta_series.tail(2).tolist()

        # Check if rising for last 2 periods
        is_rising_last_2 = len(last_2_deltas) >= 2 and last_2_deltas[-1] > last_2_deltas[-2]

        # Count consecutive rising/falling periods
        consecutive_direction = 1
        direction = "rising" if is_rising else "falling"
        for i in range(len(delta_series) - 2, -1, -1):
            if i > 0:
                curr = delta_series.iloc[i]
                prev = delta_series.iloc[i - 1]
                if (direction == "rising" and curr > prev) or (direction == "falling" and curr < prev):
                    consecutive_direction += 1
                else:
                    break

        # Delta momentum (rate of change)
        if len(delta_series) >= 3:
            delta_momentum = float(delta_series.iloc[-1] - delta_series.iloc[-3])
        else:
            delta_momentum = float(current_delta - previous_delta)

        # Generate trading signal
        signal = self._generate_signal(is_rising, is_positive, trend_strength)

        # Statistics
        delta_stats = {
            "mean": round(float(delta_series.mean()), 2),
            "max": round(float(delta_series.max()), 2),
            "min": round(float(delta_series.min()), 2),
            "std": round(float(delta_series.std()), 2) if len(delta_series) > 1 else 0
        }

        return {
            "sma_delta": round(current_delta, 2),
            "sma_delta_percent": round(delta_percent, 2),
            "sma_delta_trend": trend,
            "trend_strength": trend_strength,
            "is_delta_rising": is_rising,
            "is_delta_positive": is_positive,
            "is_favorable_for_buy": is_favorable,
            "is_rising_last_2_periods": is_rising_last_2,
            "signal": signal,
            "trading_signal": signal,  # For compatibility
            "current_values": {
                "close": round(current_close, 2),
                f"sma_{self.short_period}": round(short_sma, 2),
                f"sma_{self.long_period}": round(long_sma, 2)
            },
            "trend_analysis": {
                "direction": "Rising" if is_rising else "Falling",
                "consecutive_periods": consecutive_direction,
                "momentum": round(delta_momentum, 2),
                "last_deltas": [round(float(v), 2) for v in last_deltas]
            },
            "delta_stats": delta_stats,
            "parameters": {
                "short_period": self.short_period,
                "long_period": self.long_period
            }
        }

    def _generate_signal(self, is_rising: bool, is_positive: bool, trend_strength: str) -> str:
        """
        Generate trading signal based on SMA Delta.

        Args:
            is_rising: Whether delta is rising
            is_positive: Whether delta is positive
            trend_strength: Overall trend strength assessment

        Returns:
            Trading signal: BUY, SELL, or NEUTRAL
        """
        # Rising delta is favorable for buying
        if is_rising:
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
    print("SMA Delta Combined Agent - Test")
    print("=" * 80)

    # Create sample monthly data
    np.random.seed(42)
    dates = pd.date_range(start='2021-01-01', periods=24, freq='ME')  # 24 months

    # Simulate price data with trend
    base_price = 100
    trend = np.linspace(0, 40, 24)
    noise = np.random.randn(24) * 3
    close_prices = base_price + trend + noise

    # Create OHLCV dataframe
    df = pd.DataFrame({
        'Date': dates,
        'Open': close_prices * 0.99,
        'High': close_prices * 1.02,
        'Low': close_prices * 0.98,
        'Close': close_prices,
        'Volume': np.random.randint(1000000, 5000000, 24)
    })

    # Test with default config (6/12 months)
    print("\n### Test 1: Default Configuration (6/12 months) ###")
    agent = SMADeltaCombinedAgent()
    result = agent.run(df)

    if result.is_successful():
        print(f"\n{'Status:':<35} {result.status.upper()}")
        print(f"{'Agent:':<35} {result.agent_name}")

        summary = result.summary

        print("\n" + "=" * 80)
        print("SMA DELTA ANALYSIS")
        print("=" * 80)
        print(f"{'SMA Delta:':<35} {summary['sma_delta']}")
        print(f"{'Delta Percent:':<35} {summary['sma_delta_percent']}%")
        print(f"{'Delta Trend:':<35} {summary['sma_delta_trend']}")
        print(f"{'Trend Strength:':<35} {summary['trend_strength']}")
        print(f"{'Trading Signal:':<35} {summary['signal']}")

        print("\n" + "-" * 80)
        print("DELTA STATUS")
        print("-" * 80)
        print(f"{'Is Rising:':<35} {summary['is_delta_rising']}")
        print(f"{'Is Positive:':<35} {summary['is_delta_positive']}")
        print(f"{'Favorable for Buy:':<35} {summary['is_favorable_for_buy']}")
        print(f"{'Rising Last 2 Periods:':<35} {summary['is_rising_last_2_periods']}")

        print("\n" + "-" * 80)
        print("CURRENT VALUES")
        print("-" * 80)
        for key, value in summary['current_values'].items():
            print(f"{key + ':':<35} ${value}")

        print("\n" + "-" * 80)
        print("TREND ANALYSIS")
        print("-" * 80)
        trend = summary['trend_analysis']
        print(f"{'Direction:':<35} {trend['direction']}")
        print(f"{'Consecutive Periods:':<35} {trend['consecutive_periods']}")
        print(f"{'Momentum:':<35} {trend['momentum']}")
        print(f"{'Recent Deltas:':<35} {trend['last_deltas']}")

        print("\n" + "-" * 80)
        print("DELTA STATISTICS")
        print("-" * 80)
        for key, value in summary['delta_stats'].items():
            print(f"{key.capitalize() + ':':<35} {value}")

    else:
        print(f"\nError: {result.error}")

    # Test with custom config
    print("\n\n### Test 2: Custom Configuration (3/6 months) ###")
    from config import SMADeltaConfig
    custom_config = SMADeltaConfig(short_lookback_months=3, long_lookback_months=6)
    agent_custom = SMADeltaCombinedAgent(config=custom_config)
    result_custom = agent_custom.run(df)

    if result_custom.is_successful():
        summary = result_custom.summary
        print(f"{'SMA Delta:':<35} {summary['sma_delta']}")
        print(f"{'Trend:':<35} {summary['sma_delta_trend']}")
        print(f"{'Signal:':<35} {summary['signal']}")

    print("\n" + "=" * 80)
    print("TEST COMPLETED")
    print("=" * 80)
