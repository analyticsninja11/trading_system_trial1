"""
Combined SMA Agent - Simple Moving Average analysis with crossover patterns
Migrated to UnifiedAgent architecture with centralized configuration.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.unified_agent import UnifiedAgent
from config import SMAConfig, get_config


class SMACombinedAgent(UnifiedAgent):
    """
    Comprehensive SMA Agent that provides:
    1. Simple Moving Average calculation for multiple periods
    2. Price position relative to SMAs (above/below)
    3. Golden Cross / Death Cross detection
    4. SMA trend analysis
    5. Trading signals based on crossovers and price position
    6. Works across all timeframes (daily, weekly, monthly)

    Default periods: Short (20) and Long (50) - configurable via SMAConfig.

    Crossover Patterns:
    - Golden Cross: Short SMA crosses above Long SMA (bullish)
    - Death Cross: Short SMA crosses below Long SMA (bearish)
    """

    def __init__(self, config: SMAConfig = None, periods: List[int] = None):
        """
        Initialize Combined SMA Agent.

        Args:
            config: SMAConfig instance (uses default if None)
            periods: Optional list of custom periods (overrides config)
        """
        super().__init__(name="SMA Combined Agent", agent_type="indicator")

        # Use provided config or get default
        if config is None:
            config = get_config().sma

        self.config = config

        # Allow custom periods list or use config defaults
        if periods is not None:
            self.periods = sorted(periods)
        else:
            self.periods = sorted([config.short_period, config.long_period])

        self.short_period = self.periods[0]
        self.long_period = self.periods[-1]

    def get_minimum_rows(self) -> int:
        """SMA needs at least long_period rows for meaningful analysis."""
        return self.long_period + 1

    def process(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Process data and calculate SMAs with comprehensive analysis.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            Dictionary with:
                - data: DataFrame with SMA columns
                - summary: Comprehensive SMA analysis
        """
        # Calculate SMAs
        result_df = self._calculate_smas(df)

        # Generate comprehensive summary
        summary = self._generate_comprehensive_summary(result_df)

        return {
            "data": result_df,
            "summary": summary
        }

    def _calculate_smas(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate SMAs for all specified periods.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with SMA columns added
        """
        for period in self.periods:
            df[f'SMA_{period}'] = df['Close'].rolling(window=period).mean()

        return df

    def _generate_comprehensive_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate comprehensive SMA summary with all features.

        Args:
            df: DataFrame with SMA calculations

        Returns:
            Dictionary with SMA summary
        """
        latest = df.iloc[-1]
        previous = df.iloc[-2] if len(df) > 1 else latest

        latest_price = float(latest['Close'])

        # SMA values
        sma_values = {}
        for period in self.periods:
            sma_col = f'SMA_{period}'
            if pd.notna(latest[sma_col]):
                sma_values[sma_col] = round(float(latest[sma_col]), 2)
            else:
                sma_values[sma_col] = None

        # Price position relative to each SMA
        price_position = {}
        above_count = 0
        below_count = 0

        for period in self.periods:
            sma_col = f'SMA_{period}'
            if sma_values[sma_col] is not None:
                if latest_price > sma_values[sma_col]:
                    price_position[sma_col] = "ABOVE"
                    above_count += 1
                else:
                    price_position[sma_col] = "BELOW"
                    below_count += 1
            else:
                price_position[sma_col] = "N/A"

        # Crossover detection (using short and long periods)
        crossover = self._detect_crossover(df)

        # SMA trend analysis
        trend_analysis = self._analyze_sma_trend(df)

        # Generate trading signal
        signal = self._generate_signal(crossover, above_count, below_count)

        # Price distance from SMAs
        price_distances = self._calculate_price_distances(latest_price, sma_values)

        # SMA alignment analysis
        alignment = self._analyze_alignment(sma_values)

        return {
            "latest_price": round(latest_price, 2),
            "sma_values": sma_values,
            "price_position": price_position,
            "crossover": crossover,
            "cross_pattern": crossover.get("pattern"),  # For backward compatibility
            "signal": signal,
            "trading_signal": signal,  # For backward compatibility
            "trend_analysis": trend_analysis,
            "price_distances": price_distances,
            "alignment": alignment,
            "bullish_factors": above_count,
            "bearish_factors": below_count,
            "parameters": {
                "periods": self.periods,
                "short_period": self.short_period,
                "long_period": self.long_period
            }
        }

    def _detect_crossover(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Detect Golden Cross or Death Cross patterns.

        Args:
            df: DataFrame with SMA calculations

        Returns:
            Dictionary with crossover information
        """
        if len(df) < 2:
            return {
                "detected": False,
                "pattern": None,
                "description": "Insufficient data for crossover detection"
            }

        short_col = f'SMA_{self.short_period}'
        long_col = f'SMA_{self.long_period}'

        latest = df.iloc[-1]
        previous = df.iloc[-2]

        # Check if both SMAs have valid values
        if pd.isna(latest[short_col]) or pd.isna(latest[long_col]):
            return {
                "detected": False,
                "pattern": None,
                "description": "Insufficient data for SMA calculation"
            }

        if pd.isna(previous[short_col]) or pd.isna(previous[long_col]):
            return {
                "detected": False,
                "pattern": None,
                "description": "Insufficient historical data for crossover detection"
            }

        curr_short = float(latest[short_col])
        curr_long = float(latest[long_col])
        prev_short = float(previous[short_col])
        prev_long = float(previous[long_col])

        # Golden Cross: Short SMA crosses above Long SMA
        if prev_short <= prev_long and curr_short > curr_long:
            return {
                "detected": True,
                "pattern": "GOLDEN_CROSS",
                "description": "Golden Cross (Bullish) - Short SMA crossed above Long SMA",
                "is_bullish": True
            }

        # Death Cross: Short SMA crosses below Long SMA
        if prev_short >= prev_long and curr_short < curr_long:
            return {
                "detected": True,
                "pattern": "DEATH_CROSS",
                "description": "Death Cross (Bearish) - Short SMA crossed below Long SMA",
                "is_bullish": False
            }

        # No crossover, but determine current state
        if curr_short > curr_long:
            return {
                "detected": False,
                "pattern": None,
                "description": "Bullish alignment - Short SMA above Long SMA",
                "current_state": "BULLISH"
            }
        else:
            return {
                "detected": False,
                "pattern": None,
                "description": "Bearish alignment - Short SMA below Long SMA",
                "current_state": "BEARISH"
            }

    def _analyze_sma_trend(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze SMA trends over recent periods.

        Args:
            df: DataFrame with SMA calculations

        Returns:
            Dictionary with trend analysis for each SMA
        """
        trend_info = {}

        for period in self.periods:
            sma_col = f'SMA_{period}'
            sma_series = df[sma_col].dropna()

            if len(sma_series) < 3:
                trend_info[sma_col] = {
                    "direction": "Unknown",
                    "slope": 0.0
                }
                continue

            # Calculate slope (simple approach: compare current to 3 periods ago)
            current = float(sma_series.iloc[-1])
            previous = float(sma_series.iloc[-3]) if len(sma_series) >= 3 else float(sma_series.iloc[0])
            slope = current - previous

            # Determine direction
            if slope > 0:
                direction = "Rising"
            elif slope < 0:
                direction = "Falling"
            else:
                direction = "Flat"

            trend_info[sma_col] = {
                "direction": direction,
                "slope": round(slope, 4),
                "current_value": round(current, 2)
            }

        # Overall trend assessment
        rising_count = sum(1 for t in trend_info.values() if t.get("direction") == "Rising")
        falling_count = sum(1 for t in trend_info.values() if t.get("direction") == "Falling")

        if rising_count == len(self.periods):
            overall = "STRONGLY_BULLISH"
        elif rising_count > falling_count:
            overall = "BULLISH"
        elif falling_count == len(self.periods):
            overall = "STRONGLY_BEARISH"
        elif falling_count > rising_count:
            overall = "BEARISH"
        else:
            overall = "NEUTRAL"

        trend_info["overall"] = overall

        return trend_info

    def _generate_signal(self, crossover: Dict[str, Any], above_count: int, below_count: int) -> str:
        """
        Generate trading signal based on crossover and price position.

        Args:
            crossover: Crossover detection result
            above_count: Number of SMAs price is above
            below_count: Number of SMAs price is below

        Returns:
            Trading signal: BUY, SELL, or NEUTRAL
        """
        # Crossover signals take priority
        if crossover.get("detected"):
            if crossover.get("pattern") == "GOLDEN_CROSS":
                return "BUY"
            elif crossover.get("pattern") == "DEATH_CROSS":
                return "SELL"

        # Price position-based signals
        total_smas = above_count + below_count
        if total_smas > 0:
            # Price above all SMAs = bullish
            if above_count == total_smas:
                return "BUY"
            # Price below all SMAs = bearish
            elif below_count == total_smas:
                return "SELL"

        return "NEUTRAL"

    def _calculate_price_distances(self, price: float, sma_values: Dict[str, float]) -> Dict[str, Dict[str, float]]:
        """
        Calculate price distance from each SMA.

        Args:
            price: Current price
            sma_values: Dictionary of SMA values

        Returns:
            Dictionary with distance information for each SMA
        """
        distances = {}

        for sma_name, sma_value in sma_values.items():
            if sma_value is not None:
                absolute_distance = round(price - sma_value, 2)
                percentage_distance = round((price - sma_value) / sma_value * 100, 2)
                distances[sma_name] = {
                    "absolute": absolute_distance,
                    "percentage": percentage_distance
                }
            else:
                distances[sma_name] = {
                    "absolute": None,
                    "percentage": None
                }

        return distances

    def _analyze_alignment(self, sma_values: Dict[str, float]) -> Dict[str, Any]:
        """
        Analyze SMA alignment (bullish when shorter SMAs above longer SMAs).

        Args:
            sma_values: Dictionary of SMA values

        Returns:
            Dictionary with alignment analysis
        """
        valid_smas = [(k, v) for k, v in sma_values.items() if v is not None]

        if len(valid_smas) < 2:
            return {
                "status": "Unknown",
                "description": "Insufficient SMAs for alignment analysis"
            }

        # Extract period from SMA name and sort
        smas_sorted = sorted(valid_smas, key=lambda x: int(x[0].split('_')[1]))

        # Check if SMAs are in bullish order (shorter above longer)
        is_bullish_order = all(
            smas_sorted[i][1] > smas_sorted[i + 1][1]
            for i in range(len(smas_sorted) - 1)
        )

        # Check if SMAs are in bearish order (shorter below longer)
        is_bearish_order = all(
            smas_sorted[i][1] < smas_sorted[i + 1][1]
            for i in range(len(smas_sorted) - 1)
        )

        if is_bullish_order:
            return {
                "status": "BULLISH",
                "description": "Perfect bullish alignment - shorter SMAs above longer SMAs",
                "is_aligned": True
            }
        elif is_bearish_order:
            return {
                "status": "BEARISH",
                "description": "Perfect bearish alignment - shorter SMAs below longer SMAs",
                "is_aligned": True
            }
        else:
            return {
                "status": "MIXED",
                "description": "Mixed alignment - SMAs not in perfect order",
                "is_aligned": False
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
    print("SMA Combined Agent - Test")
    print("=" * 80)

    # Create sample data
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    np.random.seed(42)

    # Simulate price data with trend
    base_price = 100
    trend = np.linspace(0, 30, 100)
    noise = np.random.randn(100) * 2
    close_prices = base_price + trend + noise

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
    print("\n### Test 1: Default Configuration (20/50 SMA) ###")
    agent = SMACombinedAgent()
    result = agent.run(df)

    if result.is_successful():
        print(f"\n{'Status:':<30} {result.status.upper()}")
        print(f"{'Agent:':<30} {result.agent_name}")

        summary = result.summary

        print("\n" + "=" * 80)
        print("PRICE AND SMA VALUES")
        print("=" * 80)
        print(f"{'Latest Price:':<30} {summary['latest_price']}")
        for sma_name, value in summary['sma_values'].items():
            print(f"{sma_name + ':':<30} {value}")

        print("\n" + "-" * 80)
        print("PRICE POSITION")
        print("-" * 80)
        for sma_name, position in summary['price_position'].items():
            print(f"{sma_name + ':':<30} {position}")

        print("\n" + "-" * 80)
        print("CROSSOVER ANALYSIS")
        print("-" * 80)
        crossover = summary['crossover']
        print(f"{'Detected:':<30} {crossover['detected']}")
        print(f"{'Pattern:':<30} {crossover.get('pattern', 'None')}")
        print(f"{'Description:':<30} {crossover['description']}")

        print("\n" + "-" * 80)
        print("TRADING SIGNAL")
        print("-" * 80)
        print(f"{'Signal:':<30} {summary['signal']}")
        print(f"{'Bullish Factors:':<30} {summary['bullish_factors']}")
        print(f"{'Bearish Factors:':<30} {summary['bearish_factors']}")

        print("\n" + "-" * 80)
        print("SMA TREND ANALYSIS")
        print("-" * 80)
        trend = summary['trend_analysis']
        print(f"{'Overall Trend:':<30} {trend['overall']}")
        for sma_name, info in trend.items():
            if sma_name != 'overall' and isinstance(info, dict):
                print(f"{sma_name + ':':<30} {info['direction']} (slope: {info['slope']})")

        print("\n" + "-" * 80)
        print("SMA ALIGNMENT")
        print("-" * 80)
        alignment = summary['alignment']
        print(f"{'Status:':<30} {alignment['status']}")
        print(f"{'Description:':<30} {alignment['description']}")

        print("\n" + "-" * 80)
        print("PRICE DISTANCES FROM SMAs")
        print("-" * 80)
        for sma_name, dist in summary['price_distances'].items():
            if dist['absolute'] is not None:
                print(f"{sma_name + ':':<30} {dist['absolute']} ({dist['percentage']}%)")

    else:
        print(f"\nError: {result.error}")

    # Test with custom periods
    print("\n\n### Test 2: Custom Periods (10/20/50/200) ###")
    agent_custom = SMACombinedAgent(periods=[10, 20, 50, 200])

    # Need more data for 200 SMA
    dates_long = pd.date_range(start='2022-01-01', periods=250, freq='D')
    trend_long = np.linspace(0, 50, 250)
    noise_long = np.random.randn(250) * 2
    close_prices_long = base_price + trend_long + noise_long

    df_long = pd.DataFrame({
        'Date': dates_long,
        'Open': close_prices_long * 0.99,
        'High': close_prices_long * 1.01,
        'Low': close_prices_long * 0.98,
        'Close': close_prices_long,
        'Volume': np.random.randint(1000000, 5000000, 250)
    })

    result_custom = agent_custom.run(df_long)

    if result_custom.is_successful():
        summary = result_custom.summary
        print(f"{'Price:':<30} {summary['latest_price']}")
        print(f"{'Signal:':<30} {summary['signal']}")
        print(f"{'Periods Used:':<30} {summary['parameters']['periods']}")
        print(f"{'SMA Alignment:':<30} {summary['alignment']['status']}")
        print(f"{'Overall Trend:':<30} {summary['trend_analysis']['overall']}")
    else:
        print(f"Error: {result_custom.error}")

    print("\n" + "=" * 80)
    print("TEST COMPLETED")
    print("=" * 80)
