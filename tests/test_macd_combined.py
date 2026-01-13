"""
Test Combined MACD Agent with real NXT data
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.macd_combined_agent import MACDCombinedAgent
from scripts.import_price_data import import_ticker_data
import pandas as pd


def test_with_nxt_data():
    """Test Combined MACD Agent with NXT Daily data"""
    print("=" * 80)
    print("Testing MACD Combined Agent with NXT Data")
    print("=" * 80)

    # Import NXT data
    print("\nImporting NXT data...")
    nxt_data = import_ticker_data('NXT', data_dir='data')

    if 'daily' not in nxt_data:
        print("Error: Daily data not found")
        return

    # Get daily data
    df = nxt_data['daily']
    print(f"Loaded {len(df)} rows of daily data")

    # Convert to format expected by agent (capital letters)
    df_agent = pd.DataFrame({
        'Open': df['open'],
        'High': df['high'],
        'Low': df['low'],
        'Close': df['close']
    })

    # Initialize agent
    agent = MACDCombinedAgent()

    # Run agent
    print("\nRunning MACD Combined Agent...")
    result = agent.run(df_agent)

    # Display results
    if result.is_successful():
        print(f"\n{'Status:':<30} {result.status.upper()} ✓")
        print(f"{'Agent:':<30} {result.agent_name}")

        summary = result.summary

        print("\n" + "=" * 80)
        print("STANDARD MACD ANALYSIS")
        print("=" * 80)
        print(f"{'MACD Line:':<30} {summary['latest_macd']}")
        print(f"{'Signal Line:':<30} {summary['latest_signal']}")
        print(f"{'Histogram:':<30} {summary['latest_histogram']}")
        print(f"{'Trend:':<30} {summary['trend']}")
        print(f"{'Crossover:':<30} {summary.get('crossover', 'None')}")
        print(f"{'Trading Signal:':<30} {summary['signal']}")

        print("\n" + "=" * 80)
        print("SEASONAL ANALYSIS")
        print("=" * 80)
        seasonal = summary['seasonal_analysis']
        print(f"{'Current Season:':<30} {seasonal['current_season']}")
        print(f"{'Interpretation:':<30}")
        print(f"  {seasonal['season_interpretation']}")
        print(f"{'Bullish Season:':<30} {'Yes' if seasonal['is_bullish_season'] else 'No'}")
        print(f"{'Histogram Trend:':<30} {seasonal['histogram_trend']}")
        print(f"{'Histogram Momentum:':<30} {seasonal['histogram_momentum']}")
        print(f"\n{'Recent Histogram Values:':<30}")
        for i, val in enumerate(seasonal['recent_histogram_values'], 1):
            print(f"  {i}. {val}")

        print(f"\n{'Season Distribution (historical):'}")
        for season, count in seasonal['season_distribution'].items():
            percentage = (count / len(result.data)) * 100
            print(f"  {season:<15} {count:>5} ({percentage:.1f}%)")

        print("\n" + "=" * 80)
        print("RECOMMENDATION")
        print("=" * 80)
        rec = summary['recommendation']
        print(f"{'Action:':<30} {rec['action']}")
        print(f"{'Strength:':<30} {rec['strength']}")
        print(f"{'Confidence:':<30} {rec['confidence']}")
        print(f"{'Signal-Season Confluence:':<30} {'Yes ✓' if rec['confluence'] else 'No ✗'}")
        print(f"\n{'Reasoning:'}")
        for reason in rec['reasoning']:
            print(f"  • {reason}")

        print("\n" + "=" * 80)
        print("LATEST PRICE DATA (Last 5 days)")
        print("=" * 80)
        display_cols = ['Close', 'MACD', 'MACD_Signal', 'MACD_Histogram']
        print(result.data[display_cols].tail(5).to_string())

        print("\n" + "=" * 80)
        print("TEST PASSED ✓")
        print("=" * 80)

    else:
        print(f"\n❌ Error: {result.error}")
        print("TEST FAILED")


def test_all_timeframes():
    """Test with all three timeframes"""
    print("\n\n" + "=" * 80)
    print("Testing with All Timeframes (Daily, Weekly, Monthly)")
    print("=" * 80)

    # Import all NXT data
    nxt_data = import_ticker_data('NXT', data_dir='data')

    agent = MACDCombinedAgent()

    for timeframe, df in nxt_data.items():
        print(f"\n{'='*80}")
        print(f"{timeframe.upper()} TIMEFRAME")
        print(f"{'='*80}")

        # Convert to agent format
        df_agent = pd.DataFrame({
            'Open': df['open'],
            'High': df['high'],
            'Low': df['low'],
            'Close': df['close']
        })

        result = agent.run(df_agent)

        if result.is_successful():
            summary = result.summary
            seasonal = summary['seasonal_analysis']
            rec = summary['recommendation']

            print(f"{'Signal:':<25} {summary['signal']}")
            print(f"{'Trend:':<25} {summary['trend']}")
            print(f"{'Season:':<25} {seasonal['current_season']}")
            print(f"{'Recommendation:':<25} {rec['action']} ({rec['strength']}, {rec['confidence']})")
            print(f"{'Confluence:':<25} {'Yes ✓' if rec['confluence'] else 'No ✗'}")
        else:
            print(f"Error: {result.error}")


if __name__ == "__main__":
    # Test with daily data
    test_with_nxt_data()

    # Test with all timeframes
    test_all_timeframes()
