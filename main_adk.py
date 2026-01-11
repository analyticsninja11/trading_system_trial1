"""
Main entry point for Google ADK-compatible Agentic Trading System
"""
import pandas as pd
import argparse
import os
from datetime import datetime
from agents.orchestrator_agent import OrchestratorAgent
from utils.data_importer import DataImportAgent


# Initialize data import agent
data_importer = DataImportAgent()


def load_data(ticker: str, timeframe: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    Load price data from CSV file using DataImportAgent.

    Args:
        ticker: Stock ticker symbol
        timeframe: Time period (daily, weekly, monthly)
        start_date: Start date in DD/MM/YYYY format
        end_date: End date in DD/MM/YYYY format

    Returns:
        DataFrame with OHLCV data
    """
    return data_importer.load_ticker_data(ticker, timeframe, start_date, end_date)


def main():
    parser = argparse.ArgumentParser(
        description='Google ADK-compatible Agentic Trading System'
    )
    parser.add_argument('--ticker', required=True, help='Stock ticker symbol (e.g., googl, aapl)')
    parser.add_argument('--start-date', help='Start date in DD/MM/YYYY format (UK format)')
    parser.add_argument('--end-date', help='End date in DD/MM/YYYY format (UK format)')
    parser.add_argument('--mode', default='parallel', choices=['parallel', 'sequential'],
                       help='Execution mode (default: parallel)')
    parser.add_argument('--atr-length', type=int, default=10,
                       help='Supertrend ATR length (default: 10)')
    parser.add_argument('--atr-multiplier', type=float, default=3.0,
                       help='Supertrend ATR multiplier (default: 3.0)')

    args = parser.parse_args()

    print("=" * 80)
    print("GOOGLE ADK-COMPATIBLE AGENTIC TRADING SYSTEM")
    print("=" * 80)
    print(f"\nTicker: {args.ticker.upper()}")
    print(f"Execution Mode: {args.mode.upper()}")

    try:
        # Load daily data
        print("\nLoading daily data...")
        daily_df = load_data(args.ticker, 'daily', args.start_date, args.end_date)
        print(f"Loaded {len(daily_df)} daily records")
        print(f"Date range: {daily_df['Date'].min().strftime('%d/%m/%Y')} to "
              f"{daily_df['Date'].max().strftime('%d/%m/%Y')}")

        # Load monthly data
        print("\nLoading monthly data...")
        try:
            monthly_df = load_data(args.ticker, 'monthly', args.start_date, args.end_date)
            print(f"Loaded {len(monthly_df)} monthly records")
        except FileNotFoundError:
            print("Monthly data not found, will resample from daily data")
            monthly_df = None

        # Initialize orchestrator
        print("\nInitializing Orchestrator Agent...")
        orchestrator = OrchestratorAgent()

        # Configure Supertrend parameters
        orchestrator.supertrend_agent.atr_length = args.atr_length
        orchestrator.supertrend_agent.multiplier = args.atr_multiplier

        # Run orchestrator
        results = orchestrator.run(daily_df, monthly_df, mode=args.mode)

        # Print summary
        orchestrator.print_summary(results)

        # Print detailed BUY signal analysis
        print("\n" + "=" * 80)
        print("DETAILED BUY SIGNAL ANALYSIS")
        print("=" * 80)

        buy_eval = results["buy_signal_evaluation"]
        details = buy_eval["condition_details"]

        print(f"\n🎯 Final Recommendation: {buy_eval['recommendation']}")
        print(f"   Signal Strength: {buy_eval['conditions_met']}/4 conditions met")

        print("\n📊 Detailed Condition Analysis:\n")

        # Condition 1: MACD Season
        if "macd" in details:
            macd = details["macd"]
            print(f"1. MACD Season: {macd['season']}")
            print(f"   - Is Bullish Season: {macd['is_bullish']}")
            print(f"   - Condition Met: {'✅ YES' if macd['condition_met'] else '❌ NO'}")
            print(f"   - Required: Spring or Summer\n")

        # Condition 2: RSI
        if "rsi" in details:
            rsi = details["rsi"]
            print(f"2. RSI Value: {rsi['rsi_value']}")
            print(f"   - Is Above 90: {rsi['is_above_90']}")
            print(f"   - Condition Met: {'✅ YES' if rsi['condition_met'] else '❌ NO'}")
            print(f"   - Required: Not above 90\n")

        # Condition 3: SMA Delta
        if "sma" in details:
            sma = details["sma"]
            print(f"3. SMA Delta: {sma['delta']}")
            print(f"   - Trend: {sma['trend']}")
            print(f"   - Rising Last 2 Months: {sma['is_rising_last_2_months']}")
            print(f"   - Condition Met: {'✅ YES' if sma['condition_met'] else '❌ NO'}")
            print(f"   - Required: Negative and Rising OR Positive and Rising\n")

        # Condition 4: Supertrend
        if "supertrend" in details:
            st = details["supertrend"]
            print(f"4. Supertrend Signal: {st['signal']}")
            print(f"   - Is Green: {st['is_green']}")
            print(f"   - Condition Met: {'✅ YES' if st['condition_met'] else '❌ NO'}")
            print(f"   - Required: Green\n")

        print("=" * 80)

        # Save results to file
        output_file = f"{args.ticker.lower()}_analysis_results.txt"
        with open(output_file, 'w') as f:
            f.write(f"Analysis Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Ticker: {args.ticker.upper()}\n")
            f.write(f"BUY Signal: {buy_eval['recommendation']}\n")
            f.write(f"Conditions Met: {buy_eval['conditions_met']}/4\n\n")
            f.write("Individual Conditions:\n")
            for key, value in buy_eval["individual_conditions"].items():
                f.write(f"  {key}: {'✅' if value else '❌'}\n")

        print(f"\nResults saved to: {output_file}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
