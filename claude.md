# Trading System Project Context

## Project Overview

**Name:** Agentic Trading System with Multi-Agent Technical Analysis
**Type:** Python-based technical analysis system using multi-agent architecture
**Status:** Recently refactored with professional architecture
**GitHub:** https://github.com/analyticsninja11/trading_system_trial1

## Purpose

This system implements a hierarchical multi-agent architecture for technical indicator analysis of financial data. It supports both traditional indicator agents and Google ADK-compatible orchestration patterns.

## Recent Major Changes (Latest Commit)

✅ **All 5 critical architectural issues have been fixed** (Commit: 60557cb)

### What Was Refactored

1. **Unified Agent Interface** - Single consistent API replacing BaseAgent/SubAgent
2. **Centralized Configuration** - All parameters in `config.py` instead of hardcoded
3. **Custom Exception Hierarchy** - 15+ specific exception types for clear errors
4. **Testing Infrastructure** - 45 passing tests (100% pass rate)
5. **Example Migration** - MACD agent refactored to demonstrate pattern

## Project Structure

```
trading_system_trial1/
├── agents/                          # Agent implementations
│   ├── unified_agent.py            # ✨ NEW: Unified base class
│   ├── macd_agent_refactored.py    # ✨ NEW: Example refactored agent
│   ├── base_agent.py               # OLD: Traditional base (being phased out)
│   ├── sub_agent.py                # OLD: ADK base (being phased out)
│   ├── macd_agent.py               # OLD: Original MACD
│   ├── rsi_agent.py                # TODO: Needs migration
│   ├── sma_agent.py                # TODO: Needs migration
│   ├── supertrend_agent.py         # TODO: Needs migration
│   ├── macd_seasonal_agent.py      # TODO: Needs migration
│   ├── rsi_value_agent.py          # TODO: Needs migration
│   ├── sma_delta_agent.py          # TODO: Needs migration
│   └── orchestrator_agent.py       # TODO: Needs updating
│
├── config.py                        # ✨ NEW: Centralized configuration
├── exceptions.py                    # ✨ NEW: Custom exception hierarchy
│
├── tests/                           # ✨ NEW: Test suite
│   ├── test_config.py              # Configuration tests (20 tests)
│   ├── test_unified_agent.py       # Agent base tests (13 tests)
│   ├── test_macd_agent.py          # MACD tests (12 tests)
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
│   └── nxt_daily.csv
│
├── orchestrator.py                  # Basic agent orchestration
├── main.py                          # CLI entry point (basic)
├── main_adk.py                      # CLI entry point (ADK)
│
├── REFACTORING_GUIDE.md            # ✨ NEW: Comprehensive refactoring guide
├── REFACTORING_SUMMARY.md          # ✨ NEW: Executive summary
├── QUICK_START_REFACTORED.md       # ✨ NEW: Quick start guide
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
| MACD Agent | macd_agent.py | macd_agent_refactored.py | ✅ Complete |
| RSI Agent | rsi_agent.py | - | ⏳ TODO |
| SMA Agent | sma_agent.py | - | ⏳ TODO |
| Supertrend Agent | supertrend_agent.py | - | ⏳ TODO |
| Testing | None | 45 tests | ✅ Complete |

## Technical Indicators Implemented

| Indicator | Purpose | Default Parameters | Agent File |
|-----------|---------|-------------------|------------|
| **MACD** | Trend following | Fast: 12, Slow: 26, Signal: 9 | macd_agent.py (old) / macd_agent_refactored.py (new) |
| **RSI** | Momentum oscillator | Period: 14, Levels: 30/70 | rsi_agent.py |
| **SMA** | Moving averages | Periods: 20/50 | sma_agent.py |
| **Supertrend** | Trend indicator | ATR: 10, Multiplier: 3.0 | supertrend_agent.py |
| **MACD Seasonal** | Season classification | Based on MACD histogram | macd_seasonal_agent.py |
| **RSI Value** | RSI with zones | Period: 14, Zone: >90 | rsi_value_agent.py |
| **SMA Delta** | Monthly SMA change | Lookback: 6/12 months | sma_delta_agent.py |

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
- **Total:** 45/45 passing ✓

## Using the Refactored System

### Example: MACD Agent

```python
from agents.macd_agent_refactored import MACDAgent
from config import MACDConfig
import pandas as pd

# Load data
df = pd.read_csv('data/googl_daily.csv')

# Option 1: Use default config
agent = MACDAgent()
result = agent.run(df)

# Option 2: Use custom config
custom_config = MACDConfig(fast_period=10, slow_period=20, signal_period=5)
agent = MACDAgent(config=custom_config)
result = agent.run(df)

# Check results
if result.is_successful():
    print(f"Signal: {result.get_signal()}")
    print(f"Summary: {result.summary}")
    print(f"Latest MACD: {result.summary['latest_macd']}")
    print(f"Trend: {result.summary['trend']}")
else:
    print(f"Error: {result.error}")

# Access data
df_with_indicators = result.data
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

### High Priority
1. ⏳ Migrate RSI agent to UnifiedAgent
2. ⏳ Migrate SMA agent to UnifiedAgent
3. ⏳ Migrate Supertrend agent to UnifiedAgent
4. ⏳ Migrate seasonal/value/delta sub-agents

### Medium Priority
5. ⏳ Update orchestrators to use UnifiedAgent
6. ⏳ Add logging framework (use LoggingConfig)
7. ⏳ Update data importer with custom exceptions

### Low Priority
8. ⏳ Update Streamlit UIs to use config system
9. ⏳ Implement weighted voting for signals
10. ⏳ Add timeout handling for agent execution

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

- **Latest (60557cb)** - Major refactoring: Fixed all 5 critical issues
- **Initial (bd70bd5)** - Google ADK-compatible agentic trading system

---

**Last Updated:** 2026-01-12
**System Status:** ✅ Production Ready (with new refactored components)
**Test Status:** ✅ 45/45 tests passing
