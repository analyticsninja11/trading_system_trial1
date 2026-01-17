# Supertrend Combined Agent

## Overview

The **Supertrend Combined Agent** is a trend-following indicator that uses ATR (Average True Range) to calculate dynamic support/resistance bands. It follows the `UnifiedAgent` architecture pattern.

## Features

- **ATR Calculation**: Average True Range for volatility measurement
- **Dynamic Bands**: Upper and lower bands based on ATR multiplier
- **Green/Red Signals**: Clear trend direction indication
- **Trend Stability Analysis**: Measures signal consistency
- **Distance Tracking**: Price distance from Supertrend line
- **Trading Signals**: Generate BUY/SELL based on trend direction

## Quick Start

```python
from agents.supertrend_combined_agent import SupertrendCombinedAgent
import pandas as pd

# Load your data
df = pd.read_csv('data/googl_daily.csv')

# Create agent with default config
agent = SupertrendCombinedAgent()

# Run analysis
result = agent.run(df)

if result.is_successful():
    print(f"Signal: {result.summary['supertrend_signal']}")  # Green or Red
    print(f"Trading Signal: {result.summary['signal']}")     # BUY or SELL
    print(f"Trend Stability: {result.summary['trend_analysis']['stability']}")
```

## Configuration

### Default Configuration (via config.py)

```python
from config import SupertrendConfig

# Default values
atr_length = 10      # ATR calculation period
atr_multiplier = 3.0 # Band multiplier
```

### Custom Configuration

```python
from agents.supertrend_combined_agent import SupertrendCombinedAgent
from config import SupertrendConfig

# Custom config for tighter bands
config = SupertrendConfig(atr_length=14, atr_multiplier=2.0)
agent = SupertrendCombinedAgent(config=config)
```

## Output Structure

### Summary Fields

| Field | Type | Description |
|-------|------|-------------|
| `supertrend_signal` | str | "Green" (bullish) or "Red" (bearish) |
| `is_green` | bool | True if bullish trend |
| `signal` | str | BUY or SELL |
| `current_close` | float | Current closing price |
| `supertrend_value` | float | Current Supertrend line value |
| `distance_from_supertrend` | float | Absolute distance from line |
| `distance_percent` | float | Percentage distance |
| `current_atr` | float | Current ATR value |
| `upper_band` | float | Upper band value |
| `lower_band` | float | Lower band value |
| `trend_analysis` | dict | Stability and duration info |
| `parameters` | dict | Configuration used |

### Trend Analysis Object

```python
trend_analysis = {
    "stability": "Stable",          # Very Stable, Stable, Moderate, Volatile
    "duration": 15,                  # Consecutive periods in current trend
    "signal_changes_last_5": 1,     # Number of reversals in last 5 periods
    "recent_signals": ["Green", "Green", "Green", "Green", "Green"]
}
```

## Signal Logic

### Green Signal (Bullish)
- Price is **above** the Supertrend line
- Indicates uptrend
- Trading Signal: **BUY**

### Red Signal (Bearish)
- Price is **below** the Supertrend line
- Indicates downtrend
- Trading Signal: **SELL**

### Trend Stability

| Stability | Signal Changes (last 5) | Description |
|-----------|------------------------|-------------|
| Very Stable | 0 | No reversals |
| Stable | 1 | One reversal |
| Moderate | 2 | Two reversals |
| Volatile | 3+ | Choppy market |

## How Supertrend Works

1. **Calculate ATR**: Measures market volatility
2. **Calculate Bands**:
   - Upper Band = (High + Low)/2 + (Multiplier × ATR)
   - Lower Band = (High + Low)/2 - (Multiplier × ATR)
3. **Determine Trend**:
   - If price closes above upper band → Switch to bullish (Green)
   - If price closes below lower band → Switch to bearish (Red)
   - Otherwise → Continue previous trend

## Usage Examples

### Basic Usage

```python
from agents.supertrend_combined_agent import SupertrendCombinedAgent
import pandas as pd

df = pd.read_csv('data/aapl_daily.csv')
agent = SupertrendCombinedAgent()
result = agent.run(df)

if result.is_successful():
    summary = result.summary

    # Current trend
    print(f"Trend: {summary['supertrend_signal']}")
    print(f"Signal: {summary['signal']}")

    # Position relative to line
    print(f"Distance: {summary['distance_percent']}%")

    # Trend quality
    print(f"Stability: {summary['trend_analysis']['stability']}")
    print(f"Duration: {summary['trend_analysis']['duration']} periods")
```

### Different Multipliers

```python
from config import SupertrendConfig

# Tighter bands (more signals, less reliable)
tight_config = SupertrendConfig(atr_length=10, atr_multiplier=2.0)
agent_tight = SupertrendCombinedAgent(config=tight_config)

# Wider bands (fewer signals, more reliable)
wide_config = SupertrendConfig(atr_length=10, atr_multiplier=4.0)
agent_wide = SupertrendCombinedAgent(config=wide_config)
```

### Error Handling

```python
agent = SupertrendCombinedAgent()
result = agent.run(df)

if not result.is_successful():
    print(f"Error: {result.error}")
else:
    print(f"Signal: {result.get_signal()}")
```

## Data Requirements

### Minimum Rows
- Default (ATR 10): **12 rows minimum**
- Formula: `atr_length + 2`

### Required Columns
- `Open`
- `High`
- `Low`
- `Close`

## DataFrame Columns Added

After running the agent, these columns are added to the data:
- `ATR` - Average True Range
- `Upper_Band` - Upper Supertrend band
- `Lower_Band` - Lower Supertrend band
- `Supertrend` - The active Supertrend line value
- `Supertrend_Signal` - "Green" or "Red"
- `Supertrend_Direction` - 1 (bullish) or -1 (bearish)

## Testing

```bash
# Run Supertrend Combined Agent tests
python -m unittest tests.test_supertrend_combined

# Run with verbose output
python -m unittest tests.test_supertrend_combined -v
```

## Integration with Orchestrator

```python
from agents.supertrend_combined_agent import SupertrendCombinedAgent

# Create agent for orchestrator
st_agent = SupertrendCombinedAgent()
result = st_agent.run(df)

# For ADK system compatibility
is_green = result.summary['is_green']  # Used in buy condition
```

## See Also

- [MACD Combined Agent](README_MACD_COMBINED.md)
- [RSI Combined Agent](README_RSI_COMBINED.md)
- [SMA Combined Agent](README_SMA_COMBINED.md)
- [SMA Delta Combined Agent](README_SMA_DELTA_COMBINED.md)
