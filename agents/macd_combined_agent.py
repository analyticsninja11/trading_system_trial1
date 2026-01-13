"""
Combined MACD Agent - Integrates standard MACD analysis with seasonal patterns
Combines functionality from MACDAgent and MACDSeasonalAgent into a single unified agent.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from collections import Counter
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.unified_agent import UnifiedAgent
from config import MACDConfig, get_config


class MACDCombinedAgent(UnifiedAgent):
    """
    Comprehensive MACD Agent that provides:
    1. Standard MACD indicator calculation (line, signal, histogram)
    2. Trading signals based on crossovers
    3. Seasonal pattern identification (Spring, Summer, Autumn, Winter)
    4. Market phase analysis

    This agent combines the best of both MACDAgent and MACDSeasonalAgent.

    Seasons:
    - Spring: Histogram < 0, two consecutive bars increasing (accumulation)
    - Summer: Histogram > 0, two consecutive bars increasing (bullish trend)
    - Autumn: Histogram > 0, two consecutive bars decreasing (distribution)
    - Winter: Histogram < 0, two consecutive bars decreasing (bearish trend)
    """

    def __init__(self, config: MACDConfig = None):
        """
        Initialize Combined MACD Agent.

        Args:
            config: MACDConfig instance (uses default if None)
        """
        super().__init__(name="MACD Combined Agent", agent_type="indicator")

        # Use provided config or get default
        if config is None:
            config = get_config().macd

        self.config = config
        self.fast_period = config.fast_period
        self.slow_period = config.slow_period
        self.signal_period = config.signal_period

    def get_minimum_rows(self) -> int:
        """MACD needs at least slow_period + signal_period rows."""
        return self.slow_period + self.signal_period

    def process(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Process data and calculate MACD with seasonal analysis.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            Dictionary with:
                - data: DataFrame with MACD columns
                - summary: Comprehensive summary including standard and seasonal analysis
        """
        # Calculate MACD indicators
        result_df = self._calculate_macd(df)

        # Generate standard MACD summary
        standard_summary = self._generate_standard_summary(result_df)

        # Generate seasonal analysis
        seasonal_summary = self._generate_seasonal_summary(result_df)

        # Combine summaries
        combined_summary = {
            **standard_summary,
            "seasonal_analysis": seasonal_summary,
            "recommendation": self._generate_recommendation(standard_summary, seasonal_summary)
        }

        return {
            "data": result_df,
            "summary": combined_summary
        }

    def _calculate_macd(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate MACD, Signal Line, and Histogram.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with MACD columns added
        """
        # Calculate EMAs
        ema_fast = df['Close'].ewm(span=self.fast_period, adjust=False).mean()
        ema_slow = df['Close'].ewm(span=self.slow_period, adjust=False).mean()

        # Calculate MACD line
        df['MACD'] = ema_fast - ema_slow

        # Calculate Signal line
        df['MACD_Signal'] = df['MACD'].ewm(span=self.signal_period, adjust=False).mean()

        # Calculate Histogram
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']

        return df

    def _generate_standard_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate standard MACD summary statistics.

        Args:
            df: DataFrame with MACD calculations

        Returns:
            Dictionary with MACD summary
        """
        latest = df.iloc[-1]
        previous = df.iloc[-2] if len(df) > 1 else latest

        # Determine trend
        if latest['MACD'] > latest['MACD_Signal']:
            trend = "BULLISH"
        else:
            trend = "BEARISH"

        # Check for crossover
        crossover = None
        if previous['MACD'] <= previous['MACD_Signal'] and latest['MACD'] > latest['MACD_Signal']:
            crossover = "BULLISH_CROSSOVER"
        elif previous['MACD'] >= previous['MACD_Signal'] and latest['MACD'] < latest['MACD_Signal']:
            crossover = "BEARISH_CROSSOVER"

        # Generate trading signal
        if crossover == "BULLISH_CROSSOVER":
            signal = "BUY"
        elif crossover == "BEARISH_CROSSOVER":
            signal = "SELL"
        else:
            signal = "NEUTRAL"

        return {
            "latest_macd": round(float(latest['MACD']), 4),
            "latest_signal": round(float(latest['MACD_Signal']), 4),
            "latest_histogram": round(float(latest['MACD_Histogram']), 4),
            "trend": trend,
            "crossover": crossover,
            "signal": signal,
            "parameters": {
                "fast_period": self.fast_period,
                "slow_period": self.slow_period,
                "signal_period": self.signal_period
            }
        }

    def _generate_seasonal_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate seasonal pattern analysis.

        Args:
            df: DataFrame with MACD calculations

        Returns:
            Dictionary with seasonal analysis
        """
        histogram = df['MACD_Histogram'].dropna()

        if len(histogram) < 3:
            return {
                "current_season": "Unknown",
                "is_bullish_season": False,
                "error": "Insufficient data for seasonal analysis (need at least 3 points)"
            }

        # Identify current season
        current_season = self._identify_season(histogram.tail(3))

        # Get recent histogram values for context
        recent_values = histogram.tail(5).tolist()

        # Calculate season statistics over the entire period
        seasons_list = []
        for i in range(2, len(histogram)):
            season = self._identify_season(histogram.iloc[i-2:i+1])
            seasons_list.append(season)

        # Count seasons
        season_counts = Counter(seasons_list)

        # Determine histogram trend
        histogram_trend = "Increasing" if histogram.iloc[-1] > histogram.iloc[-2] else "Decreasing"

        # Check if we're in a bullish season
        is_bullish_season = current_season in ["Spring", "Summer"]

        # Calculate histogram momentum (rate of change)
        if len(histogram) >= 3:
            hist_momentum = round(float(histogram.iloc[-1] - histogram.iloc[-3]), 4)
        else:
            hist_momentum = 0

        return {
            "current_season": current_season,
            "is_bullish_season": is_bullish_season,
            "histogram_trend": histogram_trend,
            "histogram_momentum": hist_momentum,
            "recent_histogram_values": [round(float(v), 4) for v in recent_values],
            "season_distribution": dict(season_counts),
            "season_interpretation": self._interpret_season(current_season)
        }

    def _identify_season(self, histogram_values: pd.Series) -> str:
        """
        Identify the current season based on histogram pattern.

        Args:
            histogram_values: Series of last 3 histogram values

        Returns:
            Season name: Spring, Summer, Autumn, Winter, or Neutral
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

    def _interpret_season(self, season: str) -> str:
        """
        Provide human-readable interpretation of the season.

        Args:
            season: Season name

        Returns:
            Interpretation string
        """
        interpretations = {
            "Spring": "Accumulation phase - potential reversal from bearish to bullish",
            "Summer": "Strong bullish trend - momentum increasing",
            "Autumn": "Distribution phase - potential reversal from bullish to bearish",
            "Winter": "Strong bearish trend - momentum decreasing",
            "Neutral": "Transitional phase - no clear directional momentum",
            "Unknown": "Insufficient data for seasonal analysis"
        }
        return interpretations.get(season, "Unknown season")

    def _generate_recommendation(self, standard: Dict[str, Any], seasonal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive trading recommendation combining both analyses.

        Args:
            standard: Standard MACD analysis
            seasonal: Seasonal analysis

        Returns:
            Dictionary with recommendation
        """
        signal = standard['signal']
        season = seasonal['current_season']
        is_bullish_season = seasonal['is_bullish_season']
        trend = standard['trend']

        # Initialize recommendation components
        strength = "MODERATE"
        confidence = "MEDIUM"
        action = signal
        reasoning = []

        # Analyze confluence between signal and season
        if signal == "BUY" and is_bullish_season:
            strength = "STRONG"
            confidence = "HIGH"
            reasoning.append(f"Buy signal aligns with bullish season ({season})")
        elif signal == "BUY" and not is_bullish_season:
            strength = "WEAK"
            confidence = "LOW"
            reasoning.append(f"Buy signal conflicts with bearish season ({season})")
        elif signal == "SELL" and not is_bullish_season:
            strength = "STRONG"
            confidence = "HIGH"
            reasoning.append(f"Sell signal aligns with bearish season ({season})")
        elif signal == "SELL" and is_bullish_season:
            strength = "WEAK"
            confidence = "LOW"
            reasoning.append(f"Sell signal conflicts with bullish season ({season})")
        else:  # NEUTRAL
            reasoning.append("No clear trading signal at this time")
            if season == "Spring":
                reasoning.append("Consider preparing for potential bullish move")
            elif season == "Autumn":
                reasoning.append("Consider preparing for potential bearish move")

        # Add crossover information if available
        if standard['crossover']:
            reasoning.append(f"Recent {standard['crossover'].replace('_', ' ').lower()}")

        # Add trend information
        reasoning.append(f"Overall trend: {trend}")

        return {
            "action": action,
            "strength": strength,
            "confidence": confidence,
            "reasoning": reasoning,
            "confluence": signal == "BUY" and is_bullish_season or signal == "SELL" and not is_bullish_season
        }

    def _generate_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Override base class method to use our custom summary generation.

        Args:
            df: DataFrame with calculated indicators

        Returns:
            Summary dictionary
        """
        standard = self._generate_standard_summary(df)
        seasonal = self._generate_seasonal_summary(df)
        return {
            **standard,
            "seasonal_analysis": seasonal,
            "recommendation": self._generate_recommendation(standard, seasonal)
        }


# Example usage and testing
if __name__ == "__main__":
    print("=" * 80)
    print("MACD Combined Agent - Test")
    print("=" * 80)

    # Create sample data
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    np.random.seed(42)

    # Simulate price data with trend
    base_price = 100
    trend = np.linspace(0, 20, 100)
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

    # Initialize and run agent
    agent = MACDCombinedAgent()
    result = agent.run(df)

    if result.is_successful():
        print(f"\n{'Status:':<25} {result.status.upper()}")
        print(f"{'Agent:':<25} {result.agent_name}")

        summary = result.summary

        print("\n" + "=" * 80)
        print("STANDARD MACD ANALYSIS")
        print("=" * 80)
        print(f"{'MACD Line:':<25} {summary['latest_macd']}")
        print(f"{'Signal Line:':<25} {summary['latest_signal']}")
        print(f"{'Histogram:':<25} {summary['latest_histogram']}")
        print(f"{'Trend:':<25} {summary['trend']}")
        print(f"{'Crossover:':<25} {summary.get('crossover', 'None')}")
        print(f"{'Trading Signal:':<25} {summary['signal']}")

        print("\n" + "=" * 80)
        print("SEASONAL ANALYSIS")
        print("=" * 80)
        seasonal = summary['seasonal_analysis']
        print(f"{'Current Season:':<25} {seasonal['current_season']}")
        print(f"{'Interpretation:':<25} {seasonal['season_interpretation']}")
        print(f"{'Bullish Season:':<25} {seasonal['is_bullish_season']}")
        print(f"{'Histogram Trend:':<25} {seasonal['histogram_trend']}")
        print(f"{'Histogram Momentum:':<25} {seasonal['histogram_momentum']}")

        print("\n" + "=" * 80)
        print("RECOMMENDATION")
        print("=" * 80)
        rec = summary['recommendation']
        print(f"{'Action:':<25} {rec['action']}")
        print(f"{'Strength:':<25} {rec['strength']}")
        print(f"{'Confidence:':<25} {rec['confidence']}")
        print(f"{'Signal-Season Confluence:':<25} {rec['confluence']}")
        print(f"\n{'Reasoning:'}")
        for reason in rec['reasoning']:
            print(f"  • {reason}")

        print("\n" + "=" * 80)
        print("DATA PREVIEW (Last 5 rows)")
        print("=" * 80)
        display_cols = ['Close', 'MACD', 'MACD_Signal', 'MACD_Histogram']
        print(result.data[display_cols].tail(5).to_string())

    else:
        print(f"\nError: {result.error}")
