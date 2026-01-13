"""
Generic Price Data Import Script

This script imports price data from CSV files with format: {TICKER}_{TIMEFRAME}.csv
Extracts ticker symbol and timeframe from filename and returns a DataFrame with:
- date (DD/MM/YYYY format)
- open
- high
- low
- close
"""

import pandas as pd
import os
from pathlib import Path
from typing import Union, List
import re


def import_price_data(file_path: str) -> pd.DataFrame:
    """
    Import price data from a CSV file.

    Args:
        file_path: Path to the CSV file (format: {TICKER}_{TIMEFRAME}.csv)

    Returns:
        DataFrame with columns: date, open, high, low, close
        Date format: DD/MM/YYYY
    """
    # Read the CSV file, selecting only required columns
    df = pd.read_csv(
        file_path,
        usecols=['time', 'open', 'high', 'low', 'close']
    )

    # Rename 'time' column to 'date'
    df.rename(columns={'time': 'date'}, inplace=True)

    # Convert date to datetime and format as DD/MM/YYYY
    df['date'] = pd.to_datetime(df['date'])
    df['date'] = df['date'].dt.strftime('%d/%m/%Y')

    return df


def import_multiple_files(file_paths: List[str]) -> dict:
    """
    Import multiple price data files.

    Args:
        file_paths: List of file paths to import

    Returns:
        Dictionary with keys as (ticker, timeframe) tuples and values as DataFrames
    """
    results = {}

    for file_path in file_paths:
        # Extract ticker and timeframe from filename
        filename = Path(file_path).stem  # e.g., "NXT_Daily"
        match = re.match(r'(.+?)_(Daily|Weekly|Monthly)', filename, re.IGNORECASE)

        if match:
            ticker = match.group(1)
            timeframe = match.group(2).lower()

            # Import the data
            df = import_price_data(file_path)

            # Store with key (ticker, timeframe)
            results[(ticker, timeframe)] = df
            print(f"Imported {ticker} {timeframe} data: {len(df)} rows")
        else:
            print(f"Warning: Could not parse filename: {filename}")

    return results


def import_ticker_data(ticker: str, data_dir: str = 'data') -> dict:
    """
    Import all available timeframes for a specific ticker.

    Args:
        ticker: Ticker symbol (e.g., 'NXT')
        data_dir: Directory containing the CSV files

    Returns:
        Dictionary with timeframe as key and DataFrame as value
    """
    results = {}
    timeframes = ['Daily', 'Weekly', 'Monthly']

    for timeframe in timeframes:
        file_path = os.path.join(data_dir, f"{ticker}_{timeframe}.csv")

        if os.path.exists(file_path):
            df = import_price_data(file_path)
            results[timeframe.lower()] = df
            print(f"Imported {ticker} {timeframe} data: {len(df)} rows")
        else:
            print(f"File not found: {file_path}")

    return results


def main():
    """
    Example usage: Import all NXT data files
    """
    print("=" * 60)
    print("Price Data Import Script")
    print("=" * 60)

    # Method 1: Import specific ticker
    print("\n### Method 1: Import all timeframes for NXT ticker ###")
    nxt_data = import_ticker_data('NXT', data_dir='data')

    # Display summary for each timeframe
    for timeframe, df in nxt_data.items():
        print(f"\n{timeframe.upper()} Data Summary:")
        print(f"Total rows: {len(df)}")
        print(f"Date range: {df['date'].iloc[0]} to {df['date'].iloc[-1]}")
        print(f"\nFirst 3 rows:")
        print(df.head(3).to_string(index=False))

    # Method 2: Import specific file
    print("\n\n### Method 2: Import single file ###")
    daily_df = import_price_data('data/NXT_Daily.csv')
    print(f"\nDaily data shape: {daily_df.shape}")
    print(daily_df.head(3).to_string(index=False))

    # Method 3: Import multiple files at once
    print("\n\n### Method 3: Import multiple files ###")
    file_list = [
        'data/NXT_Daily.csv',
        'data/NXT_Weekly.csv',
        'data/NXT_Monthly.csv'
    ]
    all_data = import_multiple_files(file_list)

    print(f"\nTotal datasets imported: {len(all_data)}")
    for key, df in all_data.items():
        ticker, timeframe = key
        print(f"  {ticker} - {timeframe}: {len(df)} rows")

    return nxt_data


if __name__ == "__main__":
    main()
