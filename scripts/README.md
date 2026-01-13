# Price Data Import Script

## Overview
Generic script to import price data from CSV files with format: `{TICKER}_{TIMEFRAME}.csv`

## Features
- Automatically extracts ticker symbol and timeframe from filename
- Supports Daily, Weekly, and Monthly timeframes
- Returns clean DataFrame with columns: date, open, high, low, close
- Date format: DD/MM/YYYY
- Filters out unnecessary technical indicator columns

## Usage

### Method 1: Import all timeframes for a ticker
```python
from scripts.import_price_data import import_ticker_data

# Import all available timeframes for NXT
nxt_data = import_ticker_data('NXT', data_dir='data')

# Access specific timeframes
daily_df = nxt_data['daily']
weekly_df = nxt_data['weekly']
monthly_df = nxt_data['monthly']
```

### Method 2: Import a single file
```python
from scripts.import_price_data import import_price_data

# Import specific file
df = import_price_data('data/NXT_Daily.csv')
```

### Method 3: Import multiple files at once
```python
from scripts.import_price_data import import_multiple_files

file_list = [
    'data/NXT_Daily.csv',
    'data/NXT_Weekly.csv',
    'data/NXT_Monthly.csv'
]

all_data = import_multiple_files(file_list)

# Access data using (ticker, timeframe) tuple
nxt_daily = all_data[('NXT', 'daily')]
```

## Output Format
All methods return a DataFrame with the following structure:

| date       | open | high | low  | close |
|------------|------|------|------|-------|
| 04/01/2016 | 5252.79 | 5270.99 | 5176.34 | 5234.58 |

- **date**: String in DD/MM/YYYY format
- **open, high, low, close**: Float values

## Running the Example
```bash
python scripts/import_price_data.py
```

This will demonstrate all three import methods with the NXT data files.
