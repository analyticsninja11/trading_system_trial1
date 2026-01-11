# Data Import Guide

## Overview

The trading system now includes a **DataImportAgent** that automatically handles different CSV file formats. This allows you to import data from various sources without manual conversion.

---

## Supported File Formats

### Format 1: Time-based (lowercase columns)
```csv
time,open,high,low,close
2021-01-04,100.5,102.3,99.8,101.2
```

**Characteristics:**
- Lowercase column names: `time`, `open`, `high`, `low`, `close`
- No Volume column (automatically added with value 0)
- Date column named "time"

### Format 2: Standard OHLCV (capitalized columns)
```csv
Date,Open,High,Low,Close,Volume
2021-01-04,100.5,102.3,99.8,101.2,1000000
```

**Characteristics:**
- Capitalized column names: `Date`, `Open`, `High`, `Low`, `Close`, `Volume`
- Standard OHLCV format
- Date column named "Date"

---

## File Naming Convention

All data files must follow this naming pattern:

```
{ticker}_{timeframe}.csv
```

**Examples:**
- `googl_daily.csv` - Google daily prices
- `nxt_monthly.csv` - NXT monthly prices
- `aapl_weekly.csv` - Apple weekly prices

**Supported timeframes:**
- `daily` - Daily price data
- `weekly` - Weekly price data
- `monthly` - Monthly price data

---

## How It Works

The **DataImportAgent** automatically:

1. **Detects Format**: Identifies whether the CSV uses time/lowercase or Date/capitalized columns
2. **Normalizes Columns**: Converts all formats to standard: `Date`, `Open`, `High`, `Low`, `Close`, `Volume`
3. **Adds Missing Data**: If Volume column is missing, adds it with value 0
4. **Parses Dates**: Converts date strings to datetime objects
5. **Filters Data**: Applies date range filters if specified
6. **Sorts Data**: Ensures data is sorted chronologically

---

## Adding New Ticker Data

### Option 1: Direct Copy (if already in standard format)

If your CSV is already in standard format with columns `Date,Open,High,Low,Close,Volume`:

```bash
# Copy to data folder with proper naming
cp your_file.csv data/ticker_daily.csv
```

### Option 2: Use DataImportAgent to Normalize

If your CSV has a different format:

```python
from utils.data_importer import DataImportAgent

agent = DataImportAgent()

# Normalize and save
agent.normalize_file(
    source_path='your_file.csv',
    target_path='data/ticker_daily.csv'
)
```

### Option 3: Manual Export

For `.numbers` or Excel files:

1. Export to CSV format
2. Save in the root directory or data folder
3. Run the normalization script:

```bash
python3 -c "
from utils.data_importer import DataImportAgent
agent = DataImportAgent()
agent.normalize_file('YourFile.csv', 'data/ticker_daily.csv')
"
```

---

## Using the DataImportAgent

### In Python Code

```python
from utils.data_importer import DataImportAgent

# Initialize agent
agent = DataImportAgent()

# Load ticker data
df = agent.load_ticker_data(
    ticker='nxt',
    timeframe='daily',
    start_date='01/01/2022',  # Optional, UK format
    end_date='31/12/2022'      # Optional, UK format
)

# Get available tickers
tickers = agent.get_available_tickers()
print(tickers)  # ['AAPL', 'GOOGL', 'NXT']
```

### Via CLI

The CLI (`main_adk.py`) automatically uses DataImportAgent:

```bash
python3 main_adk.py --ticker nxt --start-date 01/01/2022 --end-date 31/12/2022
```

### Via Web UI

The Streamlit UI (`ui/app_adk.py`) automatically:
- Scans the data folder for available tickers
- Uses DataImportAgent to load data
- Handles both format types transparently

---

## Current Tickers

The system currently has data for:

- **GOOGL** (Google) - Daily & Monthly
- **AAPL** (Apple) - Daily
- **NXT** - Daily & Monthly

---

## Data Quality Requirements

For accurate analysis, ensure your data:

1. **Minimum Rows**:
   - Daily data: At least 26 rows for MACD calculations
   - Monthly data: At least 12 rows for SMA delta calculations

2. **Date Format**:
   - Accepted formats: YYYY-MM-DD, DD/MM/YYYY
   - Will be automatically parsed by the agent

3. **Numeric Values**:
   - All OHLC values must be numeric
   - No missing values in critical columns

---

## Troubleshooting

### Issue: "File not found"
**Solution**: Check the file naming convention. File must be `{ticker}_{timeframe}.csv` in the `data/` folder.

### Issue: "Unknown CSV format"
**Solution**: Ensure your CSV has either:
- `time,open,high,low,close` (lowercase), or
- `Date,Open,High,Low,Close,Volume` (capitalized)

### Issue: "Insufficient data" warnings
**Solution**: Ensure you have enough historical data:
- MACD: Minimum 26 daily records
- RSI: Minimum 14 daily records
- SMA Delta: Minimum 12 monthly records

### Issue: Monthly data missing
**Solution**: The system can work with just daily data. You can manually create monthly data by:

```python
import pandas as pd

# Load daily data
daily_df = pd.read_csv('data/ticker_daily.csv')
daily_df['Date'] = pd.to_datetime(daily_df['Date'])
daily_df.set_index('Date', inplace=True)

# Resample to monthly
monthly_df = daily_df.resample('M').agg({
    'Open': 'first',
    'High': 'max',
    'Low': 'min',
    'Close': 'last',
    'Volume': 'sum'
})

# Save
monthly_df.to_csv('data/ticker_monthly.csv')
```

---

## Examples

### Example 1: Import NXT Data

```bash
# NXT files were provided as NXT_Daily.csv, NXT_Monthly.csv
# Normalize them:

python3 -c "
from utils.data_importer import DataImportAgent
agent = DataImportAgent()
agent.normalize_file('NXT_Daily.csv', 'data/nxt_daily.csv')
agent.normalize_file('NXT_Monthly.csv', 'data/nxt_monthly.csv')
"
```

### Example 2: Check Available Tickers

```bash
python3 -c "
from utils.data_importer import DataImportAgent
agent = DataImportAgent()
print(agent.get_available_tickers())
"
```

### Example 3: Load and Inspect Data

```python
from utils.data_importer import DataImportAgent

agent = DataImportAgent()

# Load NXT daily data for 2022
df = agent.load_ticker_data('nxt', 'daily', '01/01/2022', '31/12/2022')

print(f"Rows: {len(df)}")
print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")
print(f"\nColumns: {df.columns.tolist()}")
print(f"\nFirst 5 rows:\n{df.head()}")
```

---

## File Structure

```
trading_system_trial1/
├── data/
│   ├── googl_daily.csv      # Standard format
│   ├── googl_monthly.csv    # Standard format
│   ├── aapl_daily.csv       # Standard format
│   ├── nxt_daily.csv        # Normalized from time format
│   └── nxt_monthly.csv      # Normalized from time format
├── utils/
│   ├── __init__.py
│   └── data_importer.py     # DataImportAgent implementation
├── main_adk.py              # Uses DataImportAgent
└── ui/app_adk.py            # Uses DataImportAgent
```

---

## Benefits of DataImportAgent

✅ **Automatic Format Detection**: No need to manually convert files
✅ **Flexible Column Naming**: Handles both uppercase and lowercase
✅ **Missing Data Handling**: Adds default Volume if missing
✅ **Consistent Output**: All data normalized to same format
✅ **Date Filtering**: Built-in support for date ranges
✅ **File Discovery**: Automatically scans for available tickers

---

## Next Steps

1. **Add Weekly Support**: Currently supports daily and monthly. Weekly can be added by ensuring weekly CSV files exist.

2. **Batch Import**: Create a script to normalize all files at once:

```bash
python3 scripts/normalize_all_data.py
```

3. **Data Validation**: Add validation to check data quality before import.

---

## Summary

The DataImportAgent makes it easy to work with price data from any source. Simply:

1. Place your CSV file in the data folder (or root directory)
2. Name it `ticker_timeframe.csv`
3. Run the system - DataImportAgent handles the rest!

No manual conversion needed. The agent automatically detects the format and normalizes it for you.
