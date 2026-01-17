# SMA Delta Combined Agent

## Overview

The **SMA Delta Combined Agent** analyzes the difference (delta) between short-term and long-term Simple Moving Averages, typically used with monthly data to identify momentum shifts. It follows the `UnifiedAgent` architecture pattern.

## Features

- **Dual SMA Calculation**: Short-term and long-term SMAs
- **Delta Analysis**: Difference between SMAs
- **Trend Direction**: Rising or falling delta
- **Momentum Assessment**: Rate of delta change
- **Strength Classification**: Bullish/Bearish strength levels
- **Trading Signals**: Generate BUY/SELL based on delta direction

## Quick Start

```python
from agents.sma_delta_combined_agent import SMADeltaCombinedAgent
import pandas as pd

# Load monthly data
df = pd.read_csv('data/googl_monthly.csv')

# Create agent with default config (6/12 months)
agent = SMADeltaCombinedAgent()

# Run analysis
result = agent.run(df)

if result.is_successful():
    print(f"Delta: {result.summary['sma_delta']}")
    print(f"Trend: {result.summary['sma_delta_trend']}")
    print(f"Signal: {result.summary['signal']}")
```

## Configuration

### Default Configuration (via config.py)

```python
from config import SMADeltaConfig

# Default values
short_lookback_months = 6   # Short-term SMA period
long_lookback_months = 12   # Long-term SMA period
```

### Custom Configuration

```python
from agents.sma_delta_combined_agent import SMADeltaCombinedAgent
from config import SMADeltaConfig

# Custom config for shorter analysis
config = SMADeltaConfig(short_lookback_months=3, long_lookback_months=6)
agent = SMADeltaCombinedAgent(config=config)
```

## Output Structure

### Summary Fields

| Field | Type | Description |
|-------|------|-------------|
| `sma_delta` | float | Current delta value (short - long SMA) |
| `sma_delta_percent` | float | Delta as percentage of long SMA |
| `sma_delta_trend` | str | Trend description |
| `trend_strength` | str | STRONGLY_BULLISH to STRONGLY_BEARISH |
| `is_delta_rising` | bool | True if delta is increasing |
| `is_delta_positive` | bool | True if short SMA > long SMA |
| `is_favorable_for_buy` | bool | True if conditions favor buying |
| `is_rising_last_2_periods` | bool | Rising for 2 consecutive periods |
| `signal` | str | BUY or SELL |
| `current_values` | dict | Close and SMA values |
| `trend_analysis` | dict | Detailed trend metrics |
| `delta_stats` | dict | Statistical measures |
| `parameters` | dict | Configuration used |

### Trend Descriptions

| Trend | Delta Sign | Direction | Interpretation |
|-------|-----------|-----------|----------------|
| Positive and Rising | + | ↑ | Strong bullish momentum |
| Negative but Rising | - | ↑ | Recovering, potential reversal |
| Positive but Falling | + | ↓ | Losing momentum, watch for reversal |
| Negative and Falling | - | ↓ | Strong bearish momentum |

### Trend Strength

| Strength | Condition |
|----------|-----------|
| STRONGLY_BULLISH | Positive AND Rising |
| BULLISH | Negative but Rising |
| BEARISH | Positive but Falling |
| STRONGLY_BEARISH | Negative AND Falling |

## Signal Logic

### BUY Signal
- Delta is **rising** (short SMA gaining on long SMA)
- Indicates improving momentum
- `is_favorable_for_buy = True`

### SELL Signal
- Delta is **falling** (short SMA losing to long SMA)
- Indicates weakening momentum
- `is_favorable_for_buy = False`

## How SMA Delta Works

1. **Calculate SMAs**:
   - Short SMA (default 6 periods)
   - Long SMA (default 12 periods)

2. **Calculate Delta**: `Delta = Short SMA - Long SMA`

3. **Analyze Direction**:
   - Rising delta = Bullish momentum building
   - Falling delta = Bearish momentum building

4. **Generate Signal**:
   - Rising → BUY
   - Falling → SELL

## Usage Examples

### Basic Usage

```python
from agents.sma_delta_combined_agent import SMADeltaCombinedAgent
import pandas as pd

df = pd.read_csv('data/aapl_monthly.csv')
agent = SMADeltaCombinedAgent()
result = agent.run(df)

if result.is_successful():
    summary = result.summary

    # Delta analysis
    print(f"Delta: {summary['sma_delta']}")
    print(f"Rising: {summary['is_delta_rising']}")
    print(f"Signal: {summary['signal']}")

    # Trend details
    print(f"Trend: {summary['sma_delta_trend']}")
    print(f"Strength: {summary['trend_strength']}")

    # Check for ADK system compatibility
    if summary['is_rising_last_2_periods']:
        print("Meets ADK buy condition: Delta rising for last 2 months")
```

### For ADK System

```python
# ADK system checks if delta is rising for last 2 months
agent = SMADeltaCombinedAgent()
result = agent.run(df)

# This is one of the 4 buy conditions in ADK
is_favorable = result.summary['is_rising_last_2_periods']
```

### Custom Periods

```python
from config import SMADeltaConfig

# Faster response (3/6 months)
fast_config = SMADeltaConfig(short_lookback_months=3, long_lookback_months=6)
agent_fast = SMADeltaCombinedAgent(config=fast_config)

# Slower, more stable (6/18 months)
slow_config = SMADeltaConfig(short_lookback_months=6, long_lookback_months=18)
agent_slow = SMADeltaCombinedAgent(config=slow_config)
```

### Trend Analysis

```python
result = agent.run(df)
trend = result.summary['trend_analysis']

print(f"Direction: {trend['direction']}")
print(f"Consecutive periods: {trend['consecutive_periods']}")
print(f"Momentum: {trend['momentum']}")
print(f"Recent deltas: {trend['last_deltas']}")
```

## Data Requirements

### Minimum Rows
- Default (12-month long SMA): **13 rows minimum**
- Formula: `long_period + 1`

### Required Columns
- `Open`
- `High`
- `Low`
- `Close`

### Recommended Timeframe
- **Monthly data** for standard analysis
- Can be used with any timeframe (interpret periods accordingly)

## DataFrame Columns Added

After running the agent, these columns are added:
- `SMA_6` (or custom short period)
- `SMA_12` (or custom long period)
- `SMA_Delta` - Difference between SMAs
- `SMA_Delta_Change` - Period-over-period delta change
- `SMA_Delta_Percent` - Delta as percentage of long SMA

## Testing

```bash
# Run SMA Delta Combined Agent tests
python -m unittest tests.test_sma_delta_combined

# Run with verbose output
python -m unittest tests.test_sma_delta_combined -v
```

## Integration with Orchestrator

```python
from agents.sma_delta_combined_agent import SMADeltaCombinedAgent

# Create agent for orchestrator
delta_agent = SMADeltaCombinedAgent()
result = delta_agent.run(monthly_df)

# For ADK system compatibility
is_rising = result.summary['is_rising_last_2_periods']  # Buy condition
```

## See Also

- [MACD Combined Agent](README_MACD_COMBINED.md)
- [RSI Combined Agent](README_RSI_COMBINED.md)
- [SMA Combined Agent](README_SMA_COMBINED.md)
- [Supertrend Combined Agent](README_SUPERTREND_COMBINED.md)
