# Agentic Trading System

A multi-agent system for technical indicator analysis using autonomous agents. Each agent specializes in calculating and analyzing a specific technical indicator (MACD, SMA, RSI).

## Features

- **Multi-Agent Architecture**: Dedicated agents for each indicator
  - MACD Agent: Moving Average Convergence Divergence
  - SMA Agent: Simple Moving Averages (20 & 50 periods)
  - RSI Agent: Relative Strength Index

- **Flexible Execution**: Sequential or parallel agent execution
- **Interactive UI**: Streamlit-based web interface
- **CLI Support**: Command-line interface for automation
- **Date Filtering**: UK date format (DD/MM/YYYY)
- **Visual Analytics**: Interactive charts with Plotly
- **Consolidated Signals**: Aggregated trading recommendations

## Project Structure

```
trading_system_trial1/
├── agents/
│   ├── __init__.py
│   ├── base_agent.py       # Base agent class
│   ├── macd_agent.py       # MACD indicator agent
│   ├── sma_agent.py        # SMA indicator agent
│   └── rsi_agent.py        # RSI indicator agent
├── data/
│   ├── googl_daily.csv     # Google daily prices
│   ├── googl_monthly.csv   # Google monthly prices
│   └── aapl_daily.csv      # Apple daily prices
├── ui/
│   └── app.py              # Streamlit UI application
├── orchestrator.py         # Agent orchestrator
├── main.py                 # CLI entry point
└── requirements.txt        # Python dependencies
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Web UI (Recommended)

Launch the Streamlit interface:

```bash
streamlit run ui/app.py
```

Features:
- Select ticker from available CSV files in data folder
- Choose date range using UK format (DD/MM/YYYY)
- Select execution mode (Sequential or Parallel)
- View consolidated signals and individual agent results
- Interactive charts for each indicator
- Download analyzed data as CSV

### Command Line

Run analysis from terminal:

```bash
# Basic usage
python main.py --ticker googl --timeframe daily

# With date filtering (UK format)
python main.py --ticker googl --timeframe daily --start-date 01/01/2024 --end-date 31/03/2024

# Parallel execution
python main.py --ticker aapl --timeframe daily --mode parallel
```

Arguments:
- `--ticker`: Stock ticker symbol (required)
- `--timeframe`: Data timeframe - daily, monthly, etc. (required)
- `--start-date`: Start date in DD/MM/YYYY format (optional)
- `--end-date`: End date in DD/MM/YYYY format (optional)
- `--mode`: Execution mode - sequential or parallel (default: sequential)

## Data Format

CSV files should be named as `{ticker}_{timeframe}.csv` and placed in the `data/` folder.

Required columns:
- Date: Date in YYYY-MM-DD format
- Open: Opening price
- High: Highest price
- Low: Lowest price
- Close: Closing price
- Volume: Trading volume

Example: `googl_daily.csv`, `aapl_monthly.csv`

## Agent Details

### MACD Agent
- **Calculation**: 12-day EMA - 26-day EMA
- **Signal Line**: 9-day EMA of MACD
- **Signals**: Bullish/Bearish crossovers
- **Output**: MACD line, Signal line, Histogram

### SMA Agent
- **Periods**: 20 and 50 days
- **Signals**: Golden Cross (bullish), Death Cross (bearish)
- **Analysis**: Price position relative to SMAs
- **Output**: SMA_20, SMA_50 columns

### RSI Agent
- **Period**: 14 days
- **Thresholds**: Overbought (70), Oversold (30)
- **Signals**: Oversold (buy), Overbought (sell)
- **Output**: RSI column with 0-100 scale

## Execution Modes

### Sequential
- Agents run one after another
- Predictable execution order
- Easier to debug
- Lower resource usage

### Parallel
- All agents run simultaneously
- Faster execution
- Better for large datasets
- Uses ThreadPoolExecutor

## Consolidated Signals

The system aggregates individual agent signals into a unified recommendation:

- **BUY**: Majority of agents signal bullish
- **SELL**: Majority of agents signal bearish
- **NEUTRAL**: No clear consensus

Confidence score indicates the percentage of agents agreeing with the signal.

## Output

The system provides:
1. Individual agent summaries
2. Consolidated trading signal
3. Interactive charts
4. Combined CSV with all indicators
5. Raw data access

## Examples

### Example 1: Quick Daily Analysis
```bash
python main.py --ticker googl --timeframe daily
```

### Example 2: Custom Date Range
```bash
python main.py --ticker aapl --timeframe daily \
  --start-date 01/01/2024 --end-date 31/03/2024 \
  --mode parallel
```

### Example 3: Monthly Analysis
```bash
python main.py --ticker googl --timeframe monthly --mode parallel
```

## Extending the System

### Adding New Agents

1. Create a new agent class in `agents/` folder:
```python
from agents.base_agent import BaseAgent

class MyAgent(BaseAgent):
    def calculate(self, df):
        # Your indicator calculation
        return df

    def get_summary(self, df):
        # Return summary dict
        return {}
```

2. Import in `agents/__init__.py`
3. Add to orchestrator in `orchestrator.py`

### Adding New Data

Add CSV files to `data/` folder following the naming convention:
- Format: `{ticker}_{timeframe}.csv`
- Example: `msft_daily.csv`, `tsla_weekly.csv`

## Technical Details

- **Language**: Python 3.8+
- **UI Framework**: Streamlit
- **Charting**: Plotly
- **Data Processing**: Pandas, NumPy
- **Indicators**: Custom implementations and TA library
- **Concurrency**: ThreadPoolExecutor for parallel execution

## Notes

- Date inputs use UK format (DD/MM/YYYY)
- All calculations use closing prices unless specified
- Indicators require minimum data points to calculate properly
- Historical data is not modified, only analyzed

## License

MIT License
