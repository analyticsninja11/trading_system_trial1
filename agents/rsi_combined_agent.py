"""
Combined RSI Agent - Integrates standard RSI analysis with advanced features
Combines functionality from RSIAgent and RSIValueAgent into a single unified agent.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.unified_agent import UnifiedAgent
from config import RSIConfig, get_config


class RSICombinedAgent(UnifiedAgent):
    """
    Comprehensive RSI Agent that provides:
    1. Standard RSI calculation (Relative Strength Index)
    2. Overbought/Oversold zone detection (configurable thresholds)
    3. Extreme levels detection (above 90, below 10)
    4. Trend analysis (Rising/Falling)
    5. Trading signals based on zone transitions
    6. Statistical analysis
    7. Works across all timeframes (daily, weekly, monthly)

    This agent combines the best of both RSIAgent and RSIValueAgent.
    """

    def __init__(self, config: RSIConfig = None):
        """
        Initialize Combined RSI Agent.

        Args:
            config: RSIConfig instance (uses default if None)
        """
        super().__init__(name="RSI Combined Agent", agent_type="indicator")

        # Use provided config or get default
        if config is None:
            config = get_config().rsi

        self.config = config
        self.period = config.period
        self.overbought = config.overbought_threshold
        self.oversold = config.oversold_threshold
        self.extreme_overbought = config.extreme_overbought
        self.extreme_oversold = config.extreme_oversold

    def get_minimum_rows(self) -> int:
        """RSI needs at least period + 1 rows."""
        return self.period + 1

    def process(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Process data and calculate RSI with comprehensive analysis.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            Dictionary with:
                - data: DataFrame with RSI column
                - summary: Comprehensive RSI analysis
        """
        # Calculate RSI
        result_df = self._calculate_rsi(df)

        # Generate comprehensive summary
        summary = self._generate_comprehensive_summary(result_df)

        return {
            "data": result_df,
            "summary": summary
        }

    def _calculate_rsi(self, df: pd.DataFrame) -> pd.DataFrame:
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

    def _generate_comprehensive_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate comprehensive RSI summary with all features.

        Args:
            df: DataFrame with RSI calculations

        Returns:
            Dictionary with RSI summary
        """
        rsi_series = df['RSI'].dropna()

        if len(rsi_series) == 0:
            return {
                "error": "Unable to calculate RSI - no valid data",
                "signal": "NEUTRAL"
            }

        latest = df.iloc[-1]
        rsi_value = float(latest['RSI'])

        # Zone detection
        zone = self._determine_zone(rsi_value)

        # Extreme levels detection
        is_above_extreme_overbought = rsi_value > self.extreme_overbought
        is_below_extreme_oversold = rsi_value < self.extreme_oversold
        is_above_90 = rsi_value > 90  # Special check for orchestrator compatibility

        # Trend analysis
        trend_info = self._analyze_trend(rsi_series)

        # Trading signal
        signal = self._generate_signal(df, rsi_value, zone)

        # Statistical analysis
        stats = self._calculate_statistics(rsi_series)

        # Recent values for context
        recent_values = rsi_series.tail(5).tolist()

        return {
            "latest_rsi": round(rsi_value, 2),
            "rsi_value": round(rsi_value, 2),  # For compatibility with RSIValueAgent
            "zone": zone,
            "condition": zone.upper(),  # For compatibility with RSIAgent
            "signal": signal,
            "trading_signal": signal,  # For compatibility
            "trend_analysis": trend_info,
            "extreme_levels": {
                "is_above_extreme_overbought": is_above_extreme_overbought,
                "is_below_extreme_oversold": is_below_extreme_oversold,
                "is_above_90": is_above_90,  # For orchestrator compatibility
                "extreme_overbought_threshold": self.extreme_overbought,
                "extreme_oversold_threshold": self.extreme_oversold
            },
            "recent_rsi_values": [round(float(v), 2) for v in recent_values],
            "rsi_stats": stats,
            "rsi_zone": zone,  # For compatibility
            "rsi_trend": trend_info["direction"],  # For compatibility
            "parameters": {
                "period": self.period,
                "overbought_threshold": self.overbought,
                "oversold_threshold": self.oversold,
                "extreme_overbought": self.extreme_overbought,
                "extreme_oversold": self.extreme_oversold
            }
        }

    def _determine_zone(self, rsi_value: float) -> str:
        """
        Determine the RSI zone.

        Args:
            rsi_value: Current RSI value

        Returns:
            Zone name: Extreme Overbought, Overbought, Neutral, Oversold, Extreme Oversold
        """
        if rsi_value > self.extreme_overbought:
            return "Extreme Overbought"
        elif rsi_value >= self.overbought:
            return "Overbought"
        elif rsi_value < self.extreme_oversold:
            return "Extreme Oversold"
        elif rsi_value <= self.oversold:
            return "Oversold"
        else:
            return "Neutral"

    def _analyze_trend(self, rsi_series: pd.Series) -> Dict[str, Any]:
        """
        Analyze RSI trend.

        Args:
            rsi_series: Series of RSI values

        Returns:
            Dictionary with trend analysis
        """
        if len(rsi_series) < 2:
            return {
                "direction": "Unknown",
                "strength": "Unknown",
                "momentum": 0.0
            }

        # Current vs previous
        current = rsi_series.iloc[-1]
        previous = rsi_series.iloc[-2]
        direction = "Rising" if current > previous else "Falling"

        # Calculate momentum (change over last 3 periods)
        if len(rsi_series) >= 3:
            momentum = float(current - rsi_series.iloc[-3])
        else:
            momentum = float(current - previous)

        # Determine strength
        if abs(momentum) > 10:
            strength = "Strong"
        elif abs(momentum) > 5:
            strength = "Moderate"
        else:
            strength = "Weak"

        # Check for divergence potential (simplified)
        consecutive_increases = 0
        consecutive_decreases = 0

        if len(rsi_series) >= 5:
            for i in range(len(rsi_series) - 4, len(rsi_series)):
                if i > 0 and rsi_series.iloc[i] > rsi_series.iloc[i-1]:
                    consecutive_increases += 1
                elif i > 0 and rsi_series.iloc[i] < rsi_series.iloc[i-1]:
                    consecutive_decreases += 1

        return {
            "direction": direction,
            "strength": strength,
            "momentum": round(momentum, 2),
            "consecutive_moves": max(consecutive_increases, consecutive_decreases),
            "is_trending": max(consecutive_increases, consecutive_decreases) >= 3
        }

    def _generate_signal(self, df: pd.DataFrame, rsi_value: float, zone: str) -> str:
        """
        Generate trading signal based on RSI.

        Args:
            df: DataFrame with RSI calculations
            rsi_value: Current RSI value
            zone: Current RSI zone

        Returns:
            Trading signal: BUY, SELL, or NEUTRAL
        """
        if len(df) < 2:
            # Simple threshold-based signals
            if "Oversold" in zone:
                return "BUY"
            elif "Overbought" in zone:
                return "SELL"
            return "NEUTRAL"

        previous = df.iloc[-2]
        prev_rsi = float(previous['RSI'])

        # Signal based on zone transitions (more reliable than simple thresholds)

        # Moving out of oversold zone (bullish signal)
        if prev_rsi <= self.oversold and rsi_value > self.oversold:
            return "BUY"

        # Moving into extreme oversold (strong buy signal)
        if rsi_value < self.extreme_oversold:
            return "BUY"

        # Moving into overbought zone (bearish signal)
        if prev_rsi < self.overbought and rsi_value >= self.overbought:
            return "SELL"

        # In extreme overbought (strong sell signal)
        if rsi_value > self.extreme_overbought:
            return "SELL"

        # Additional signals based on current zone
        if "Extreme Oversold" in zone:
            return "BUY"
        elif "Extreme Overbought" in zone:
            return "SELL"
        elif "Oversold" in zone:
            return "BUY"
        elif "Overbought" in zone:
            return "SELL"

        return "NEUTRAL"

    def _calculate_statistics(self, rsi_series: pd.Series) -> Dict[str, float]:
        """
        Calculate statistical measures for RSI.

        Args:
            rsi_series: Series of RSI values

        Returns:
            Dictionary with statistics
        """
        return {
            "mean": round(float(rsi_series.mean()), 2),
            "max": round(float(rsi_series.max()), 2),
            "min": round(float(rsi_series.min()), 2),
            "std": round(float(rsi_series.std()), 2),
            "median": round(float(rsi_series.median()), 2)
        }

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
    print("RSI Combined Agent - Test")
    print("=" * 80)

    # Create sample data
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    np.random.seed(42)

    # Simulate price data with trend and volatility
    base_price = 100
    trend = np.linspace(0, 20, 100)
    noise = np.random.randn(100) * 3
    close_prices = base_price + trend + noise

    # Add some extreme movements to test overbought/oversold
    close_prices[30:35] += 15  # Overbought condition
    close_prices[60:65] -= 15  # Oversold condition

    # Create OHLCV dataframe
    df = pd.DataFrame({
        'Date': dates,
        'Open': close_prices * 0.99,
        'High': close_prices * 1.01,
        'Low': close_prices * 0.98,
        'Close': close_prices,
        'Volume': np.random.randint(1000000, 5000000, 100)
    })

    # Test with default config
    print("\n### Test 1: Default Configuration ###")
    agent = RSICombinedAgent()
    result = agent.run(df)

    if result.is_successful():
        print(f"\n{'Status:':<30} {result.status.upper()}")
        print(f"{'Agent:':<30} {result.agent_name}")

        summary = result.summary

        print("\n" + "=" * 80)
        print("RSI ANALYSIS")
        print("=" * 80)
        print(f"{'Current RSI:':<30} {summary['latest_rsi']}")
        print(f"{'Zone:':<30} {summary['zone']}")
        print(f"{'Trading Signal:':<30} {summary['signal']}")

        print("\n" + "-" * 80)
        print("TREND ANALYSIS")
        print("-" * 80)
        trend = summary['trend_analysis']
        print(f"{'Direction:':<30} {trend['direction']}")
        print(f"{'Strength:':<30} {trend['strength']}")
        print(f"{'Momentum:':<30} {trend['momentum']}")
        print(f"{'Is Trending:':<30} {trend['is_trending']}")

        print("\n" + "-" * 80)
        print("EXTREME LEVELS")
        print("-" * 80)
        extreme = summary['extreme_levels']
        print(f"{'Above 90 (Extreme):':<30} {extreme['is_above_90']}")
        print(f"{'Above {:.0f} (Extreme OB):' :<30} {extreme['is_above_extreme_overbought']}".format(extreme['extreme_overbought_threshold']))
        print(f"{'Below {:.0f} (Extreme OS):' :<30} {extreme['is_below_extreme_oversold']}".format(extreme['extreme_oversold_threshold']))

        print("\n" + "-" * 80)
        print("STATISTICS")
        print("-" * 80)
        stats = summary['rsi_stats']
        for key, value in stats.items():
            print(f"{key.capitalize():<30} {value}")

        print("\n" + "-" * 80)
        print("RECENT RSI VALUES")
        print("-" * 80)
        for i, val in enumerate(summary['recent_rsi_values'], 1):
            print(f"  {i}. {val}")

    else:
        print(f"\nError: {result.error}")

    # Test with custom config
    print("\n\n### Test 2: Custom Configuration (Crypto-style: 80/20) ###")
    from config import RSIConfig
    custom_config = RSIConfig()
    custom_config.period = 14
    custom_config.overbought_threshold = 80.0
    custom_config.oversold_threshold = 20.0
    custom_config.extreme_overbought = 95.0
    custom_config.extreme_oversold = 5.0

    agent_custom = RSICombinedAgent(config=custom_config)
    result_custom = agent_custom.run(df)

    if result_custom.is_successful():
        summary = result_custom.summary
        print(f"{'RSI:':<30} {summary['latest_rsi']}")
        print(f"{'Zone:':<30} {summary['zone']}")
        print(f"{'Signal:':<30} {summary['signal']}")
        print(f"{'Thresholds:':<30} OB={custom_config.overbought_threshold}, OS={custom_config.oversold_threshold}")

    print("\n" + "=" * 80)
    print("TEST COMPLETED")
    print("=" * 80)
