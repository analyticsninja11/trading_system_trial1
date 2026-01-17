# SMA Combined Agent

## Overview

The **SMA Combined Agent** is a comprehensive Simple Moving Average analysis tool that provides multi-period SMA calculation, crossover detection, trend analysis, and trading signals. It follows the `UnifiedAgent` architecture pattern.

## Features

- **Multi-period SMA Calculation**: Calculate SMAs for any number of periods
- **Golden Cross / Death Cross Detection**: Automatic crossover pattern recognition
- **Price Position Analysis**: Track price relative to each SMA
- **Trend Analysis**: Determine SMA direction and overall trend
- **Alignment Analysis**: Bullish/bearish SMA alignment detection
- **Trading Signals**: Generate BUY/SELL/NEUTRAL signals
- **Distance Calculations**: Price distance from each SMA (absolute and percentage)

## Quick Start

```python
from agents.sma_combined_agent import SMACombinedAgent
import pandas as pd

# Load your data
df = pd.read_csv('data/googl_daily.csv')

# Create agent with default config (20/50 SMA)
agent = SMACombinedAgent()

# Run analysis
result = agent.run(df)

if result.is_successful():
    print(f"Signal: {result.summary['signal']}")
    print(f"Price: {result.summary['latest_price']}")
    print(f"SMA Values: {result.summary['sma_values']}")
```

## Configuration

### Default Configuration (via config.py)

```python
from config import SMAConfig

# Default values
short_period = 20  # Short-term SMA
long_period = 50   # Long-term SMA
```

### Custom Configuration

```python
from agents.sma_combined_agent import SMACombinedAgent
from config import SMAConfig

# Option 1: Custom config
config = SMAConfig(short_period=10, long_period=30)
agent = SMACombinedAgent(config=config)

# Option 2: Custom periods list
agent = SMACombinedAgent(periods=[10, 20, 50, 200])
```

## Output Structure

### Summary Fields

| Field | Type | Description |
|-------|------|-------------|
| `latest_price` | float | Current closing price |
| `sma_values` | dict | SMA values for each period |
| `price_position` | dict | ABOVE/BELOW for each SMA |
| `crossover` | dict | Crossover detection details |
| `cross_pattern` | str | GOLDEN_CROSS, DEATH_CROSS, or None |
| `signal` | str | BUY, SELL, or NEUTRAL |
| `trend_analysis` | dict | Trend info for each SMA |
| `price_distances` | dict | Distance from each SMA |
| `alignment` | dict | SMA alignment analysis |
| `parameters` | dict | Configuration used |

### Crossover Object

```python
crossover = {
    "detected": True,          # Was a crossover detected?
    "pattern": "GOLDEN_CROSS", # GOLDEN_CROSS or DEATH_CROSS
    "description": "...",      # Human-readable description
    "is_bullish": True         # Is this a bullish crossover?
}
```

### Trend Analysis Object

```python
trend_analysis = {
    "SMA_20": {
        "direction": "Rising",  # Rising, Falling, or Flat
        "slope": 0.45,          # Numerical slope
        "current_value": 125.50
    },
    "SMA_50": {...},
    "overall": "BULLISH"  # STRONGLY_BULLISH, BULLISH, NEUTRAL, BEARISH, STRONGLY_BEARISH
}
```

### Alignment Object

```python
alignment = {
    "status": "BULLISH",  # BULLISH, BEARISH, MIXED, or Unknown
    "description": "Perfect bullish alignment - shorter SMAs above longer SMAs",
    "is_aligned": True
}
```

## Crossover Patterns

### Golden Cross (Bullish)
- Short-term SMA crosses **above** long-term SMA
- Indicates potential uptrend beginning
- Signal: **BUY**

### Death Cross (Bearish)
- Short-term SMA crosses **below** long-term SMA
- Indicates potential downtrend beginning
- Signal: **SELL**

## Signal Logic

1. **Crossover Priority**: Golden Cross → BUY, Death Cross → SELL
2. **Price Position**:
   - Price above ALL SMAs → BUY
   - Price below ALL SMAs → SELL
   - Otherwise → NEUTRAL

## Usage Examples

### Basic Usage

```python
from agents.sma_combined_agent import SMACombinedAgent
import pandas as pd

# Load data
df = pd.read_csv('data/aapl_daily.csv')

# Run with defaults
agent = SMACombinedAgent()
result = agent.run(df)

if result.is_successful():
    summary = result.summary

    # Get trading signal
    print(f"Signal: {summary['signal']}")

    # Check crossover
    if summary['crossover']['detected']:
        print(f"Pattern: {summary['crossover']['pattern']}")

    # Get price position
    for sma, position in summary['price_position'].items():
        print(f"{sma}: {position}")
```

### Multiple Timeframe Analysis

```python
# Analyze with 4 SMAs
agent = SMACombinedAgent(periods=[10, 20, 50, 200])
result = agent.run(df)

# Check alignment
alignment = result.summary['alignment']
print(f"Alignment: {alignment['status']}")

# Check overall trend
overall_trend = result.summary['trend_analysis']['overall']
print(f"Overall Trend: {overall_trend}")
```

### Custom Configuration

```python
from config import SMAConfig

# Shorter periods for more responsive signals
config = SMAConfig(short_period=5, long_period=20)
config.validate()

agent = SMACombinedAgent(config=config)
result = agent.run(df)
```

### Error Handling

```python
from exceptions import InsufficientDataError

agent = SMACombinedAgent()
result = agent.run(df)

if not result.is_successful():
    print(f"Error: {result.error}")
else:
    # Process result
    print(f"Signal: {result.get_signal()}")
```

## Data Requirements

### Minimum Rows
- Default (50 SMA): **51 rows minimum**
- Formula: `long_period + 1`

### Required Columns
- `Open`
- `High`
- `Low`
- `Close`

### Optional Columns
- `Volume`
- `Date`

## Testing

```bash
# Run SMA Combined Agent tests
python -m unittest tests.test_sma_combined

# Run with verbose output
python -m unittest tests.test_sma_combined -v
```

## Integration with Orchestrator

```python
from agents.sma_combined_agent import SMACombinedAgent

# Create agent for orchestrator
sma_agent = SMACombinedAgent()
result = sma_agent.run(df)

# Get signal for consolidation
signal = result.get_signal()  # BUY, SELL, or NEUTRAL
```

## Migration Notes

### From Old SMAAgent

The old `SMAAgent` used:
- Hardcoded periods
- `BaseAgent` inheritance
- Different summary structure

The new `SMACombinedAgent` provides:
- Configurable periods via `SMAConfig`
- `UnifiedAgent` inheritance
- Comprehensive summary with backward-compatible fields

### Backward Compatibility

These fields are preserved for compatibility:
- `trading_signal` (same as `signal`)
- `cross_pattern` (same as `crossover.pattern`)

## Performance Considerations

- SMA calculations use pandas rolling window (efficient)
- Memory usage scales with number of periods
- Recommended: Use 2-4 periods for most analyses

## See Also

- [MACD Combined Agent](README_MACD_COMBINED.md)
- [RSI Combined Agent](README_RSI_COMBINED.md)
- [Unified Agent Base Class](unified_agent.py)
- [Configuration System](../config.py)
