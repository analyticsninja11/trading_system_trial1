# Trading System Project Context

## Project Overview

**Name:** Agentic Trading System with Multi-Agent Technical Analysis
**Type:** Python-based technical analysis system using multi-agent architecture
**Status:** Recently refactored with professional architecture
**GitHub:** https://github.com/analyticsninja11/trading_system_trial1

## Purpose

This system implements a hierarchical multi-agent architecture for technical indicator analysis of financial data. It supports both traditional indicator agents and Google ADK-compatible orchestration patterns.

## Recent Major Changes (Latest)

✅ **ALL AGENT MIGRATIONS COMPLETE** (2026-01-17)

### What Was Done

1. **SupertrendCombinedAgent** - Migrated Supertrend agent to UnifiedAgent architecture
   - ATR (Average True Range) calculation
   - Dynamic upper/lower bands based on ATR multiplier
   - Green/Red signal detection (bullish/bearish)
   - Trend stability analysis (Very Stable to Volatile)
   - Distance from Supertrend line tracking
   - Full test coverage (22 tests)
   - Documentation: `agents/README_SUPERTREND_COMBINED.md`

2. **SMADeltaCombinedAgent** - Migrated SMA Delta agent to UnifiedAgent architecture
   - Short-term and long-term SMA calculation (6/12 months default)
   - Delta analysis (difference between SMAs)
   - Rising/falling delta detection
   - Trend strength classification (STRONGLY_BULLISH to STRONGLY_BEARISH)
   - Momentum and consecutive period tracking
   - Full test coverage (27 tests)
   - Documentation: `agents/README_SMA_DELTA_COMBINED.md`

3. **SMACombinedAgent** - Migrated SMA agent to UnifiedAgent architecture
   - Multi-period SMA calculation (configurable periods)
   - Golden Cross / Death Cross detection
   - Price position analysis (above/below each SMA)
   - SMA trend analysis with slope calculation
   - SMA alignment detection (bullish/bearish/mixed)
   - Trading signals based on crossovers and price position
   - Full test coverage (24 tests)
   - Documentation: `agents/README_SMA_COMBINED.md`

### Previous: Agent Consolidation (Commit: 8b56eed)

1. **MACDCombinedAgent** - Merged MACDAgent + MACDSeasonalAgent into single agent
   - Integrates standard MACD analysis with seasonal pattern recognition
   - Identifies market seasons (Spring, Summer, Autumn, Winter)
   - Intelligent recommendations with confluence detection
   - Works across all timeframes (daily, weekly, monthly)

2. **RSICombinedAgent** - Merged RSIAgent + RSIValueAgent into single agent
   - Configurable thresholds for different trading styles (70/30, 80/20, etc.)
   - Comprehensive trend analysis (direction, strength, momentum)
   - 5-zone detection (Extreme OB/OS, OB/OS, Neutral)
   - Works across all timeframes with customizable parameters

3. **Generic Price Data Importer** - Created unified data import script
   - Handles multiple timeframes (Daily, Weekly, Monthly)
   - Auto-detects ticker and timeframe from filename
   - Converts dates to DD/MM/YYYY format
   - Returns clean DataFrames with OHLCV data

### Previous: Major Refactoring (Commit: 60557cb)

1. **Unified Agent Interface** - Single consistent API replacing BaseAgent/SubAgent
2. **Centralized Configuration** - All parameters in `config.py` instead of hardcoded
3. **Custom Exception Hierarchy** - 15+ specific exception types for clear errors
4. **Testing Infrastructure** - 45 passing tests (100% pass rate)
5. **Example Migration** - MACD agent refactored to demonstrate pattern

## Project Structure

```
trading_system_trial1/
├── agents/                          # Agent implementations
│   ├── unified_agent.py            # ✨ Unified base class
│   ├── macd_combined_agent.py      # ✅ Combined MACD (standard + seasonal)
│   ├── rsi_combined_agent.py       # ✅ Combined RSI (standard + value)
│   ├── sma_combined_agent.py       # ✅ Combined SMA (multi-period + crossovers)
│   ├── supertrend_combined_agent.py # ✅ NEW: Combined Supertrend (ATR bands + signals)
│   ├── sma_delta_combined_agent.py # ✅ NEW: Combined SMA Delta (momentum analysis)
│   ├── README_MACD_COMBINED.md     # MACD documentation
│   ├── README_RSI_COMBINED.md      # RSI documentation
│   ├── README_SMA_COMBINED.md      # SMA documentation
│   ├── README_SUPERTREND_COMBINED.md # ✅ NEW: Supertrend documentation
│   ├── README_SMA_DELTA_COMBINED.md # ✅ NEW: SMA Delta documentation
│   ├── base_agent.py               # OLD: Traditional base (being phased out)
│   ├── sub_agent.py                # OLD: ADK base (being phased out)
│   ├── sma_agent.py                # OLD: Legacy (replaced by sma_combined_agent.py)
│   ├── supertrend_agent.py         # OLD: Legacy (replaced by supertrend_combined_agent.py)
│   ├── sma_delta_agent.py          # OLD: Legacy (replaced by sma_delta_combined_agent.py)
│   └── orchestrator_agent.py       # ✅ UPDATED: Uses combined agents
│
├── scripts/                         # ✅ NEW: Utility scripts
│   ├── import_price_data.py        # Generic price data importer
│   └── README.md                   # Import script documentation
│
├── config.py                        # ✨ Centralized configuration
├── exceptions.py                    # ✨ Custom exception hierarchy
│
├── tests/                           # Test suite
│   ├── test_config.py              # Configuration tests (20 tests)
│   ├── test_unified_agent.py       # Agent base tests (13 tests)
│   ├── test_macd_agent.py          # MACD tests (12 tests)
│   ├── test_macd_combined.py       # MACD combined tests
│   ├── test_rsi_combined.py        # RSI combined tests
│   ├── test_sma_combined.py        # SMA combined tests (24 tests)
│   ├── test_supertrend_combined.py # ✅ NEW: Supertrend tests (22 tests)
│   ├── test_sma_delta_combined.py  # ✅ NEW: SMA Delta tests (27 tests)
│   └── requirements-test.txt       # Testing dependencies
│
├── ui/                              # Streamlit interfaces
│   ├── app.py                      # Basic agents UI
│   └── app_adk.py                  # ADK system UI
│
├── utils/
│   └── data_importer.py            # CSV data handling
│
├── data/                            # Historical price data
│   ├── googl_daily.csv
│   ├── googl_monthly.csv
│   ├── aapl_daily.csv
│   ├── NXT_Daily.csv               # ✅ NEW: NXT daily data
│   ├── NXT_Weekly.csv              # ✅ NEW: NXT weekly data
│   └── NXT_Monthly.csv             # ✅ NEW: NXT monthly data
│
├── orchestrator.py                  # ✅ UPDATED: Uses combined agents
├── main.py                          # CLI entry point (basic)
├── main_adk.py                      # CLI entry point (ADK)
│
├── MACD_CONSOLIDATION_SUMMARY.md   # ✅ NEW: MACD consolidation details
├── RSI_CONSOLIDATION_SUMMARY.md    # ✅ NEW: RSI consolidation details
├── REFACTORING_GUIDE.md            # Comprehensive refactoring guide
├── REFACTORING_SUMMARY.md          # Executive summary
├── QUICK_START_REFACTORED.md       # Quick start guide
└── requirements.txt                 # Production dependencies
```

## Architecture Patterns

### Current State: Dual System

**1. Legacy System (Being Phased Out)**
- Uses `BaseAgent` and `SubAgent` classes
- Magic numbers hardcoded throughout
- Generic exception handling
- No tests

**2. New Refactored System (Recommended)**
- Uses `UnifiedAgent` base class
- Configuration via `config.py`
- Specific exception types from `exceptions.py`
- Comprehensive test coverage

### Migration Status

| Component | Old | New | Status |
|-----------|-----|-----|--------|
| Base Classes | BaseAgent, SubAgent | UnifiedAgent | ✅ Complete |
| Configuration | Hardcoded | config.py | ✅ Complete |
| Error Handling | Generic | exceptions.py | ✅ Complete |
| MACD Agent | macd_agent.py + macd_seasonal_agent.py | macd_combined_agent.py | ✅ Complete |
| RSI Agent | rsi_agent.py + rsi_value_agent.py | rsi_combined_agent.py | ✅ Complete |
| SMA Agent | sma_agent.py | sma_combined_agent.py | ✅ Complete |
| Supertrend Agent | supertrend_agent.py | supertrend_combined_agent.py | ✅ Complete |
| SMA Delta Agent | sma_delta_agent.py | sma_delta_combined_agent.py | ✅ Complete |
| Price Importer | - | scripts/import_price_data.py | ✅ Complete |
| Testing | None | 118 tests | ✅ Complete |

## Technical Indicators Implemented

| Indicator | Purpose | Default Parameters | Agent File | Features |
|-----------|---------|-------------------|------------|----------|
| **MACD Combined** | Trend + Seasons | Fast: 12, Slow: 26, Signal: 9 | macd_combined_agent.py | Standard MACD + Seasonal patterns (Spring/Summer/Autumn/Winter) + Confluence analysis |
| **RSI Combined** | Momentum + Zones | Period: 14, OB/OS: 70/30, Extreme: 90/10 | rsi_combined_agent.py | RSI calculation + Configurable thresholds + Trend analysis + 5-zone detection |
| **SMA Combined** | Moving averages + Crossovers | Periods: 20/50 | sma_combined_agent.py | Multi-period SMAs + Golden/Death Cross + Price position + Trend + Alignment analysis |
| **Supertrend Combined** | Trend indicator | ATR: 10, Multiplier: 3.0 | supertrend_combined_agent.py | ATR bands + Green/Red signals + Trend stability + Distance tracking |
| **SMA Delta Combined** | Monthly SMA change | Lookback: 6/12 months | sma_delta_combined_agent.py | Delta analysis + Rising/Falling detection + Momentum + Trend strength |

## Configuration System

### Key Configuration Classes

```python
from config import get_config

config = get_config()

# Access indicator configs
config.macd.fast_period        # 12
config.macd.slow_period        # 26
config.macd.signal_period      # 9

config.rsi.period              # 14
config.rsi.overbought_threshold # 70
config.rsi.oversold_threshold  # 30

config.sma.short_period        # 20
config.sma.long_period         # 50

config.supertrend.atr_length   # 10
config.supertrend.atr_multiplier # 3.0

# Orchestration settings
config.orchestrator.min_buy_conditions  # 2
config.orchestrator.max_workers        # 4
config.orchestrator.default_execution_mode # "parallel"
```

### Customizing Configuration

```python
from config import TradingSystemConfig, MACDConfig

# Method 1: Modify default
config = get_config()
config.macd.fast_period = 10
config.validate()

# Method 2: Create custom
custom_macd = MACDConfig(fast_period=10, slow_period=20, signal_period=5)

# Method 3: Load from JSON
config = TradingSystemConfig.from_json_file('my_config.json')

# Method 4: Save to JSON
config.to_json_file('custom_config.json')
```

## Exception Hierarchy

### Categories

1. **Data Validation**
   - `InsufficientDataError(required, actual, agent_name)`
   - `MissingColumnsError(missing_columns, agent_name)`
   - `EmptyDataFrameError(agent_name)`
   - `InvalidDataFormatError()`

2. **Configuration**
   - `InvalidParameterError(parameter, value, reason)`

3. **Agent Execution**
   - `AgentInitializationError(agent_name, message)`
   - `AgentExecutionError(agent_name, message)`
   - `IndicatorCalculationError(agent_name, message)`

4. **Orchestration**
   - `AgentTimeoutError(agent_name, timeout_seconds)`
   - `ParallelExecutionError(failed_agents, message)`

5. **Data Import**
   - `FileNotFoundError(file_path)`
   - `UnsupportedFileFormatError(file_path, supported_formats)`
   - `DateParsingError(date_string, expected_format)`

6. **Signal Processing**
   - `ConflictingSignalsError(signals)`
   - `InsufficientSignalsError(required, actual)`

## Testing

### Running Tests

```bash
# Run all tests (45 tests)
python -m unittest discover tests

# Run specific test suite
python -m unittest tests.test_config          # 20 tests
python -m unittest tests.test_unified_agent   # 13 tests
python -m unittest tests.test_macd_agent      # 12 tests

# Run with verbose output
python -m unittest discover tests -v

# Run single test
python -m unittest tests.test_config.TestMACDConfig.test_default_values
```

### Test Coverage

- **Configuration:** 20/20 passing ✓
- **Unified Agent:** 13/13 passing ✓
- **MACD Agent:** 12/12 passing ✓
- **SMA Combined:** 24/24 passing ✓
- **Supertrend Combined:** 22/22 passing ✓
- **SMA Delta Combined:** 27/27 passing ✓
- **Total:** 118 tests passing ✓

## Using the Refactored System

### Example: MACD Combined Agent

```python
from agents.macd_combined_agent import MACDCombinedAgent
from config import MACDConfig
import pandas as pd

# Load data
df = pd.read_csv('data/googl_daily.csv')

# Option 1: Use default config
agent = MACDCombinedAgent()
result = agent.run(df)

# Option 2: Use custom config
custom_config = MACDConfig(fast_period=10, slow_period=20, signal_period=5)
agent = MACDCombinedAgent(config=custom_config)
result = agent.run(df)

# Check results
if result.is_successful():
    print(f"Signal: {result.get_signal()}")
    print(f"Summary: {result.summary}")
    print(f"Latest MACD: {result.summary['latest_macd']}")
    print(f"Trend: {result.summary['trend']}")

    # Access seasonal analysis
    seasonal = result.summary['seasonal_analysis']
    print(f"Season: {seasonal['current_season']}")
    print(f"Is Bullish Season: {seasonal['is_bullish_season']}")

    # Access recommendation
    rec = result.summary['recommendation']
    print(f"Action: {rec['action']}")
    print(f"Confidence: {rec['confidence']}")
    print(f"Reasoning: {rec['reasoning']}")
else:
    print(f"Error: {result.error}")

# Access data
df_with_indicators = result.data
```

### Example: RSI Combined Agent

```python
from agents.rsi_combined_agent import RSICombinedAgent
from config import RSIConfig
import pandas as pd

# Load data
df = pd.read_csv('data/googl_daily.csv')

# Option 1: Use default config (70/30)
agent = RSICombinedAgent()
result = agent.run(df)

# Option 2: Crypto-style thresholds (80/20)
custom_config = RSIConfig()
custom_config.overbought_threshold = 80.0
custom_config.oversold_threshold = 20.0
agent = RSICombinedAgent(config=custom_config)
result = agent.run(df)

# Check results
if result.is_successful():
    summary = result.summary
    print(f"RSI: {summary['latest_rsi']}")
    print(f"Zone: {summary['zone']}")
    print(f"Signal: {summary['signal']}")

    # Access trend analysis
    trend = summary['trend_analysis']
    print(f"Trend: {trend['direction']} ({trend['strength']})")
    print(f"Momentum: {trend['momentum']}")

    # Check extreme levels
    extreme = summary['extreme_levels']
    print(f"Above 90: {extreme['is_above_90']}")
else:
    print(f"Error: {result.error}")
```

### Example: SMA Combined Agent

```python
from agents.sma_combined_agent import SMACombinedAgent
from config import SMAConfig
import pandas as pd

# Load data
df = pd.read_csv('data/googl_daily.csv')

# Option 1: Use default config (20/50)
agent = SMACombinedAgent()
result = agent.run(df)

# Option 2: Use custom config
config = SMAConfig(short_period=10, long_period=30)
agent = SMACombinedAgent(config=config)
result = agent.run(df)

# Option 3: Use multiple periods
agent = SMACombinedAgent(periods=[10, 20, 50, 200])
result = agent.run(df)

# Check results
if result.is_successful():
    summary = result.summary
    print(f"Signal: {summary['signal']}")
    print(f"Price: {summary['latest_price']}")
    print(f"SMA Values: {summary['sma_values']}")

    # Check crossover
    crossover = summary['crossover']
    if crossover['detected']:
        print(f"Pattern: {crossover['pattern']}")  # GOLDEN_CROSS or DEATH_CROSS

    # Check alignment
    print(f"Alignment: {summary['alignment']['status']}")  # BULLISH, BEARISH, MIXED

    # Check trend
    print(f"Overall Trend: {summary['trend_analysis']['overall']}")
else:
    print(f"Error: {result.error}")
```

### Example: Supertrend Combined Agent

```python
from agents.supertrend_combined_agent import SupertrendCombinedAgent
from config import SupertrendConfig
import pandas as pd

# Load data
df = pd.read_csv('data/googl_daily.csv')

# Option 1: Use default config (ATR: 10, Multiplier: 3.0)
agent = SupertrendCombinedAgent()
result = agent.run(df)

# Option 2: Use custom config (tighter bands)
config = SupertrendConfig(atr_length=14, atr_multiplier=2.0)
agent = SupertrendCombinedAgent(config=config)
result = agent.run(df)

# Check results
if result.is_successful():
    summary = result.summary
    print(f"Signal: {summary['supertrend_signal']}")  # Green or Red
    print(f"Is Green (Bullish): {summary['is_green']}")
    print(f"Trading Signal: {summary['signal']}")  # BUY or SELL
    print(f"Distance: {summary['distance_percent']}%")

    # Trend analysis
    trend = summary['trend_analysis']
    print(f"Stability: {trend['stability']}")  # Very Stable, Stable, Moderate, Volatile
    print(f"Duration: {trend['duration']} periods")
else:
    print(f"Error: {result.error}")
```

### Example: SMA Delta Combined Agent

```python
from agents.sma_delta_combined_agent import SMADeltaCombinedAgent
from config import SMADeltaConfig
import pandas as pd

# Load monthly data
df = pd.read_csv('data/googl_monthly.csv')

# Option 1: Use default config (6/12 months)
agent = SMADeltaCombinedAgent()
result = agent.run(df)

# Option 2: Use custom config
config = SMADeltaConfig(short_lookback_months=3, long_lookback_months=6)
agent = SMADeltaCombinedAgent(config=config)
result = agent.run(df)

# Check results
if result.is_successful():
    summary = result.summary
    print(f"Delta: {summary['sma_delta']}")
    print(f"Trend: {summary['sma_delta_trend']}")  # e.g., "Positive and Rising"
    print(f"Rising: {summary['is_delta_rising']}")
    print(f"Signal: {summary['signal']}")  # BUY or SELL

    # For ADK system compatibility
    print(f"Rising Last 2 Periods: {summary['is_rising_last_2_periods']}")
else:
    print(f"Error: {result.error}")
```

### Example: Import Price Data

```python
from scripts.import_price_data import import_ticker_data

# Import all timeframes for a ticker
nxt_data = import_ticker_data('NXT', data_dir='data')

# Access different timeframes
daily_df = nxt_data['daily']
weekly_df = nxt_data['weekly']
monthly_df = nxt_data['monthly']

print(f"Daily: {len(daily_df)} rows")
print(f"Weekly: {len(weekly_df)} rows")
print(f"Monthly: {len(monthly_df)} rows")

# DataFrame has: date, open, high, low, close
# Date format: DD/MM/YYYY
```

### Example: Error Handling

```python
from agents.macd_agent_refactored import MACDAgent
from exceptions import InsufficientDataError, MissingColumnsError

agent = MACDAgent()

try:
    result = agent.run(df)
except InsufficientDataError as e:
    print(f"Need {e.required} rows, got {e.actual}")
except MissingColumnsError as e:
    print(f"Missing columns: {', '.join(e.missing_columns)}")
```

## Coding Standards & Patterns

### When Creating New Agents

1. **Inherit from UnifiedAgent**
   ```python
   from agents.unified_agent import UnifiedAgent

   class MyAgent(UnifiedAgent):
       def __init__(self, config=None):
           super().__init__(name="My Agent", agent_type="indicator")
           self.config = config or get_config().my_indicator
   ```

2. **Implement Required Methods**
   ```python
   def process(self, df: pd.DataFrame) -> Dict[str, Any]:
       # Calculate indicators
       result_df = self._calculate(df)

       # Generate summary
       summary = self._generate_summary(result_df)

       # Add signal to summary
       summary["signal"] = self._get_signal(result_df)

       return {
           "data": result_df,
           "summary": summary
       }

   def get_minimum_rows(self) -> int:
       return self.config.required_period
   ```

3. **Use Custom Exceptions**
   ```python
   from exceptions import InsufficientDataError

   if len(df) < min_rows:
       raise InsufficientDataError(
           required=min_rows,
           actual=len(df),
           agent_name=self.name
       )
   ```

4. **Use Configuration**
   ```python
   # Don't hardcode
   self.period = 14  # BAD

   # Use config
   self.period = self.config.period  # GOOD
   ```

### When Writing Tests

```python
import unittest
from agents.my_agent import MyAgent

class TestMyAgent(unittest.TestCase):
    def setUp(self):
        # Create test data
        self.df = create_test_dataframe()

    def test_initialization(self):
        agent = MyAgent()
        self.assertEqual(agent.name, "My Agent")

    def test_calculation(self):
        agent = MyAgent()
        result = agent.run(self.df)
        self.assertTrue(result.is_successful())
        self.assertIn('my_indicator', result.data.columns)
```

## Data Format

### Required CSV Columns

All CSV files must have these columns (case-sensitive):
- `Date` or `time` - Date/timestamp
- `Open` - Opening price
- `High` - High price
- `Low` - Low price
- `Close` - Closing price
- `Volume` - Trading volume (auto-generated if missing)

### Supported Date Formats

- User input: `DD/MM/YYYY` (UK format)
- Internal: `YYYY-MM-DD` (ISO format)
- CSV: Various formats (auto-detected)

## Execution Modes

### Parallel Execution (Default)
```python
orchestrator = AgentOrchestrator(ticker="GOOGL")
results = orchestrator.run_agents_parallel()  # Faster
```

### Sequential Execution
```python
results = orchestrator.run_agents_sequential()  # Easier to debug
```

## Signal Consolidation Logic

### Basic System
Simple majority voting across 3 agents (MACD, RSI, SMA)

### ADK System
Requires 2 of 4 conditions for BUY signal:
1. MACD Season = Spring or Summer
2. RSI < 90
3. SMA Delta rising (last 2 months)
4. Supertrend = Green

## Important Notes

### DO
✅ Use `UnifiedAgent` for new agents
✅ Use `config.py` for all parameters
✅ Use specific exceptions from `exceptions.py`
✅ Write tests for new features
✅ Follow the MACD refactored example
✅ Validate configuration before use
✅ Check `result.is_successful()` before using data

### DON'T
❌ Hardcode magic numbers
❌ Use `BaseAgent` or `SubAgent` for new code
❌ Use generic `Exception` or `ValueError`
❌ Skip writing tests
❌ Modify config without calling `validate()`
❌ Assume agent execution succeeded without checking

## Dependencies

### Production
- pandas==2.1.4
- numpy==1.26.2
- ta==0.11.0
- streamlit==1.29.0
- plotly==5.18.0

### Testing
- pytest>=7.4.0
- pytest-cov>=4.1.0
- pytest-mock>=3.11.1
- coverage>=7.3.0

Install: `pip install -r tests/requirements-test.txt`

## Next Steps / TODO

### High Priority - ALL COMPLETE ✅
1. ✅ ~~Migrate RSI agent to UnifiedAgent~~ - COMPLETE (RSICombinedAgent)
2. ✅ ~~Migrate MACD agent to UnifiedAgent~~ - COMPLETE (MACDCombinedAgent)
3. ✅ ~~Migrate SMA agent to UnifiedAgent~~ - COMPLETE (SMACombinedAgent)
4. ✅ ~~Migrate Supertrend agent to UnifiedAgent~~ - COMPLETE (SupertrendCombinedAgent)
5. ✅ ~~Migrate SMA Delta agent to UnifiedAgent~~ - COMPLETE (SMADeltaCombinedAgent)

### Medium Priority
6. ✅ ~~Update orchestrators to use combined agents~~ - COMPLETE
7. ⏳ Add logging framework (use LoggingConfig)
8. ⏳ Update data importer with custom exceptions
9. ⏳ Update orchestrator to use all combined agents

### Low Priority
10. ⏳ Update Streamlit UIs to use config system and combined agents
11. ⏳ Implement weighted voting for signals
12. ⏳ Add timeout handling for agent execution
13. ⏳ Push changes to GitHub repository

## Useful Commands

```bash
# Run tests
python -m unittest discover tests

# Run specific UI
streamlit run ui/app.py
streamlit run ui/app_adk.py

# Run CLI
python main.py --ticker googl --timeframe daily --mode parallel
python main_adk.py --ticker googl --mode parallel

# Check Python version
python --version  # Requires Python 3.8+

# Install dependencies
pip install -r requirements.txt
pip install -r tests/requirements-test.txt
```

## Documentation Files

- **MACD_CONSOLIDATION_SUMMARY.md** - MACD agent consolidation details
- **RSI_CONSOLIDATION_SUMMARY.md** - RSI agent consolidation details
- **agents/README_MACD_COMBINED.md** - MACD Combined Agent documentation
- **agents/README_RSI_COMBINED.md** - RSI Combined Agent documentation
- **agents/README_SMA_COMBINED.md** - SMA Combined Agent documentation
- **agents/README_SUPERTREND_COMBINED.md** - Supertrend Combined Agent documentation
- **agents/README_SMA_DELTA_COMBINED.md** - SMA Delta Combined Agent documentation
- **scripts/README.md** - Price data import script documentation
- **REFACTORING_GUIDE.md** - Comprehensive guide (567 lines)
- **REFACTORING_SUMMARY.md** - Executive summary with metrics
- **QUICK_START_REFACTORED.md** - Quick start guide
- **README.md** - Original project README
- **README_ADK.md** - ADK system documentation
- **QUICKSTART.md** - Original quickstart
- **DATA_IMPORT_GUIDE.md** - Data import guide

## Contact & Support

For questions about:
- **Migration patterns** - See `agents/macd_agent_refactored.py`
- **Configuration** - See `config.py` and tests
- **Testing** - See `tests/` directory
- **Architecture** - See REFACTORING_GUIDE.md

## Version History

- **Latest (2026-01-17)** - ALL AGENTS MIGRATED: Supertrend + SMA Delta combined agents complete (118 tests)
- **Previous (2026-01-17)** - SMA Agent Migration: SMACombinedAgent with crossover detection
- **Previous (8b56eed)** - Agent Consolidation: Combined MACD and RSI agents + Generic price importer
- **Previous (60557cb)** - Major refactoring: Fixed all 5 critical issues
- **Initial (bd70bd5)** - Google ADK-compatible agentic trading system

---

**Last Updated:** 2026-01-17
**System Status:** ✅ Production Ready - ALL AGENTS MIGRATED
**Test Status:** ✅ All 118 tests passing
**Agent Status:** ✅ MACD Combined, ✅ RSI Combined, ✅ SMA Combined, ✅ Supertrend Combined, ✅ SMA Delta Combined
