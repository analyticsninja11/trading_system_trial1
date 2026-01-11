"""
Data Import Agent for handling different CSV file formats
"""
import pandas as pd
import os
from typing import Optional
from datetime import datetime


class DataImportAgent:
    """
    Agent responsible for importing and normalizing price data from various CSV formats.

    Handles:
    - Different column naming conventions (time/Date, lowercase/capitalized)
    - Missing Volume column
    - Date filtering and parsing
    - File naming convention: ticker_timeframe.csv
    """

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.name = "Data Import Agent"

    def detect_format(self, df: pd.DataFrame) -> str:
        """
        Detect CSV format based on column names.

        Returns:
            'time_format' for lowercase time,open,high,low,close
            'date_format' for capitalized Date,Open,High,Low,Close,Volume
        """
        columns = [col.strip() for col in df.columns]

        if 'time' in columns:
            return 'time_format'
        elif 'Date' in columns:
            return 'date_format'
        else:
            raise ValueError(f"Unknown CSV format. Columns: {columns}")

    def normalize_columns(self, df: pd.DataFrame, format_type: str) -> pd.DataFrame:
        """
        Normalize column names to standard format: Date, Open, High, Low, Close, Volume
        """
        # Remove trailing empty columns
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        df = df.dropna(axis=1, how='all')

        if format_type == 'time_format':
            # Map lowercase time format to standard format
            column_mapping = {
                'time': 'Date',
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close'
            }

            # Clean column names (remove trailing commas/spaces)
            df.columns = [col.strip() for col in df.columns]

            # Rename columns
            df = df.rename(columns=column_mapping)

            # Add Volume column with zeros if missing
            if 'Volume' not in df.columns:
                df['Volume'] = 0

        elif format_type == 'date_format':
            # Already in standard format, just ensure Volume exists
            if 'Volume' not in df.columns:
                df['Volume'] = 0

        return df

    def load_ticker_data(
        self,
        ticker: str,
        timeframe: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Load and normalize ticker data from CSV file.

        Args:
            ticker: Stock ticker symbol (e.g., 'googl', 'nxt')
            timeframe: Time period ('daily', 'weekly', 'monthly')
            start_date: Start date in DD/MM/YYYY format (optional)
            end_date: End date in DD/MM/YYYY format (optional)

        Returns:
            DataFrame with normalized columns: Date, Open, High, Low, Close, Volume
        """
        # Try lowercase filename first
        filename = f"{ticker.lower()}_{timeframe.lower()}.csv"
        filepath = os.path.join(self.data_dir, filename)

        # If not found, try uppercase ticker with capitalized timeframe
        if not os.path.exists(filepath):
            filename = f"{ticker.upper()}_{timeframe.capitalize()}.csv"
            filepath = os.path.join(self.data_dir, filename)

        if not os.path.exists(filepath):
            raise FileNotFoundError(
                f"Could not find data file for {ticker} {timeframe}. "
                f"Tried: {ticker.lower()}_{timeframe.lower()}.csv and "
                f"{ticker.upper()}_{timeframe.capitalize()}.csv"
            )

        # Load CSV
        df = pd.read_csv(filepath)

        # Detect format
        format_type = self.detect_format(df)

        # Normalize columns
        df = self.normalize_columns(df, format_type)

        # Parse dates
        df['Date'] = pd.to_datetime(df['Date'])

        # Filter by date range if provided
        if start_date:
            start_dt = datetime.strptime(start_date, "%d/%m/%Y")
            df = df[df['Date'] >= start_dt]

        if end_date:
            end_dt = datetime.strptime(end_date, "%d/%m/%Y")
            df = df[df['Date'] <= end_dt]

        # Sort by date and reset index
        df = df.sort_values('Date').reset_index(drop=True)

        # Ensure all required columns are present
        required_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        return df[required_columns]

    def get_available_tickers(self) -> list:
        """
        Scan data folder for available ticker CSV files.

        Returns:
            List of ticker symbols (uppercase) sorted alphabetically
        """
        tickers = set()

        if not os.path.exists(self.data_dir):
            return []

        for filename in os.listdir(self.data_dir):
            if filename.endswith('.csv'):
                # Extract ticker from filename
                # Support both formats: ticker_timeframe.csv and TICKER_Timeframe.csv
                parts = filename.replace('.csv', '').split('_')
                if len(parts) >= 2:
                    ticker = parts[0]
                    tickers.add(ticker.upper())

        return sorted(list(tickers))

    def normalize_file(self, source_path: str, target_path: str) -> None:
        """
        Normalize a CSV file and save to target path.

        Useful for converting files from various formats to standard format.
        """
        df = pd.read_csv(source_path)
        format_type = self.detect_format(df)
        df = self.normalize_columns(df, format_type)
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date').reset_index(drop=True)

        # Save normalized file
        df.to_csv(target_path, index=False)
        print(f"Normalized file saved to: {target_path}")
