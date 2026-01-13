"""
Test Combined RSI Agent with real NXT data
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.rsi_combined_agent import RSICombinedAgent
from scripts.import_price_data import import_ticker_data
from config import RSIConfig
import pandas as pd


def test_with_nxt_data():
    """Test Combined RSI Agent with NXT Daily data"""
    print("=" * 80)
    print("Testing RSI Combined Agent with NXT Data")
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

    # Initialize agent with default config
    agent = RSICombinedAgent()

    # Run agent
    print("\nRunning RSI Combined Agent...")
    result = agent.run(df_agent)

    # Display results
    if result.is_successful():
        print(f"\n{'Status:':<35} {result.status.upper()} ✓")
        print(f"{'Agent:':<35} {result.agent_name}")

        summary = result.summary

        print("\n" + "=" * 80)
        print("RSI ANALYSIS")
        print("=" * 80)
        print(f"{'Current RSI:':<35} {summary['latest_rsi']}")
        print(f"{'Zone:':<35} {summary['zone']}")
        print(f"{'Trading Signal:':<35} {summary['signal']}")

        print("\n" + "=" * 80)
        print("TREND ANALYSIS")
        print("=" * 80)
        trend = summary['trend_analysis']
        print(f"{'Direction:':<35} {trend['direction']}")
        print(f"{'Strength:':<35} {trend['strength']}")
        print(f"{'Momentum:':<35} {trend['momentum']}")
        print(f"{'Consecutive Moves:':<35} {trend['consecutive_moves']}")
        print(f"{'Is Trending:':<35} {'Yes' if trend['is_trending'] else 'No'}")

        print("\n" + "=" * 80)
        print("EXTREME LEVELS")
        print("=" * 80)
        extreme = summary['extreme_levels']
        print(f"{'Above 90 (for orchestrator):':<35} {'Yes' if extreme['is_above_90'] else 'No'}")
        print(f"{'Above {:.0f} (Extreme Overbought):' :<35} {'Yes' if extreme['is_above_extreme_overbought'] else 'No'}".format(extreme['extreme_overbought_threshold']))
        print(f"{'Below {:.0f} (Extreme Oversold):' :<35} {'Yes' if extreme['is_below_extreme_oversold'] else 'No'}".format(extreme['extreme_oversold_threshold']))

        print("\n" + "=" * 80)
        print("STATISTICS")
        print("=" * 80)
        stats = summary['rsi_stats']
        for key, value in stats.items():
            print(f"{key.capitalize():<35} {value}")

        print("\n" + "=" * 80)
        print("RECENT RSI VALUES (Last 5 days)")
        print("=" * 80)
        for i, val in enumerate(summary['recent_rsi_values'], 1):
            print(f"  {i}. {val}")

        print("\n" + "=" * 80)
        print("PARAMETERS")
        print("=" * 80)
        params = summary['parameters']
        print(f"{'Period:':<35} {params['period']}")
        print(f"{'Overbought Threshold:':<35} {params['overbought_threshold']}")
        print(f"{'Oversold Threshold:':<35} {params['oversold_threshold']}")
        print(f"{'Extreme Overbought:':<35} {params['extreme_overbought']}")
        print(f"{'Extreme Oversold:':<35} {params['extreme_oversold']}")

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

    agent = RSICombinedAgent()

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
            trend = summary['trend_analysis']

            print(f"{'RSI Value:':<30} {summary['latest_rsi']}")
            print(f"{'Zone:':<30} {summary['zone']}")
            print(f"{'Signal:':<30} {summary['signal']}")
            print(f"{'Trend:':<30} {trend['direction']} ({trend['strength']})")
            print(f"{'Momentum:':<30} {trend['momentum']}")
        else:
            print(f"Error: {result.error}")


def test_custom_config():
    """Test with custom configuration (crypto-style thresholds)"""
    print("\n\n" + "=" * 80)
    print("Testing with Custom Configuration (80/20 Thresholds)")
    print("=" * 80)

    # Import NXT daily data
    nxt_data = import_ticker_data('NXT', data_dir='data')
    df = nxt_data['daily']

    # Convert to agent format
    df_agent = pd.DataFrame({
        'Open': df['open'],
        'High': df['high'],
        'Low': df['low'],
        'Close': df['close']
    })

    # Create custom config
    custom_config = RSIConfig()
    custom_config.period = 14
    custom_config.overbought_threshold = 80.0
    custom_config.oversold_threshold = 20.0
    custom_config.extreme_overbought = 95.0
    custom_config.extreme_oversold = 5.0

    agent = RSICombinedAgent(config=custom_config)
    result = agent.run(df_agent)

    if result.is_successful():
        summary = result.summary
        print(f"\n{'RSI Value:':<35} {summary['latest_rsi']}")
        print(f"{'Zone (80/20):':<35} {summary['zone']}")
        print(f"{'Signal:':<35} {summary['signal']}")
        print(f"{'Overbought Threshold:':<35} {custom_config.overbought_threshold}")
        print(f"{'Oversold Threshold:':<35} {custom_config.oversold_threshold}")
        print("\nCustom configuration working correctly ✓")
    else:
        print(f"Error: {result.error}")


if __name__ == "__main__":
    # Test with daily data
    test_with_nxt_data()

    # Test with all timeframes
    test_all_timeframes()

    # Test with custom config
    test_custom_config()
