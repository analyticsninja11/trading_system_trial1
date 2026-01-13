# RSI Combined Agent

## Overview
The **RSI Combined Agent** is a comprehensive technical analysis tool that merges standard RSI indicator calculations with advanced features. This agent combines the functionality of both `RSIAgent` and `RSIValueAgent` into a single, powerful analysis tool.

## Features

### 1. Standard RSI Calculation
- **RSI Formula**: Standard 14-period Relative Strength Index
- **Configurable Period**: Customize the calculation period (default: 14)
- **Works Across All Timeframes**: Daily, Weekly, Monthly

### 2. Zone Detection with Configurable Thresholds
- **Overbought/Oversold Zones**: Fully configurable thresholds (default: 70/30)
- **Extreme Levels**: Detect extreme overbought (>90) and oversold (<10) conditions
- **Special Check**: "is_above_90" flag for orchestrator compatibility
- **Five Zones**:
  - Extreme Overbought (>90)
  - Overbought (≥70)
  - Neutral (30-70)
  - Oversold (≤30)
  - Extreme Oversold (<10)

### 3. Trend Analysis
- **Direction**: Rising or Falling
- **Strength**: Strong, Moderate, or Weak
- **Momentum**: Rate of change over recent periods
- **Consecutive Moves**: Track trending behavior
- **Trending Flag**: Identifies sustained directional movement

### 4. Trading Signals
Generates intelligent trading signals based on:
- Zone transitions (e.g., exiting oversold)
- Extreme levels
- Current zone position

### 5. Statistical Analysis
- Mean, Median, Max, Min, Standard Deviation
- Recent value tracking
- Historical context

## Usage

### Basic Usage
```python
from agents.rsi_combined_agent import RSICombinedAgent
import pandas as pd

# Prepare your OHLCV data
df = pd.DataFrame({
    'Open': [...],
    'High': [...],
    'Low': [...],
    'Close': [...]
})

# Initialize agent (uses default config: 70/30 thresholds)
agent = RSICombinedAgent()

# Run analysis
result = agent.run(df)

# Check if successful
if result.is_successful():
    summary = result.summary

    # Access RSI data
    print(f"RSI Value: {summary['latest_rsi']}")
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

### With Custom Configuration (Crypto-style 80/20)
```python
from agents.rsi_combined_agent import RSICombinedAgent
from config import RSIConfig

# Custom RSI parameters for crypto trading
custom_config = RSIConfig()
custom_config.period = 14
custom_config.overbought_threshold = 80.0
custom_config.oversold_threshold = 20.0
custom_config.extreme_overbought = 95.0
custom_config.extreme_oversold = 5.0

agent = RSICombinedAgent(config=custom_config)
result = agent.run(df)
```

### With Import Script
```python
from agents.rsi_combined_agent import RSICombinedAgent
from scripts.import_price_data import import_ticker_data
import pandas as pd

# Import data
nxt_data = import_ticker_data('NXT', data_dir='data')
df_daily = nxt_data['daily']

# Convert to agent format
df_agent = pd.DataFrame({
    'Open': df_daily['open'],
    'High': df_daily['high'],
    'Low': df_daily['low'],
    'Close': df_daily['close']
})

# Run agent
agent = RSICombinedAgent()
result = agent.run(df_agent)
```

## Configuration Options

```python
class RSIConfig:
    period: int = 14                         # RSI calculation period
    overbought_threshold: float = 70.0       # Overbought level
    oversold_threshold: float = 30.0         # Oversold level
    extreme_overbought: float = 90.0         # Extreme overbought
    extreme_oversold: float = 10.0           # Extreme oversold
```

### Common Configurations

**Traditional (Default)**
- Period: 14
- Overbought: 70 / Oversold: 30
- Extreme: 90 / 10

**Crypto Trading**
- Period: 14
- Overbought: 80 / Oversold: 20
- Extreme: 95 / 5

**Conservative**
- Period: 21
- Overbought: 65 / Oversold: 35
- Extreme: 85 / 15

**Aggressive**
- Period: 9
- Overbought: 75 / Oversold: 25
- Extreme: 90 / 10

## Output Structure

### AgentResult Object
```python
result = agent.run(df)

# Properties
result.agent_name       # "RSI Combined Agent"
result.status          # "completed" or "failed"
result.data            # DataFrame with RSI column added
result.summary         # Dictionary with analysis results
result.error           # Error message (if failed)
result.timestamp       # Timestamp of execution

# Methods
result.is_successful() # Returns True if completed successfully
result.get_signal()    # Returns trading signal: "BUY", "SELL", or "NEUTRAL"
```

### Summary Dictionary Structure
```python
summary = {
    # Core RSI Values
    "latest_rsi": float,
    "rsi_value": float,  # Same as latest_rsi (compatibility)

    # Zone Detection
    "zone": str,  # "Extreme Overbought" | "Overbought" | "Neutral" | "Oversold" | "Extreme Oversold"
    "condition": str,  # Zone in uppercase (compatibility)

    # Trading Signal
    "signal": str,  # "BUY" | "SELL" | "NEUTRAL"
    "trading_signal": str,  # Same as signal (compatibility)

    # Trend Analysis
    "trend_analysis": {
        "direction": "Rising" | "Falling",
        "strength": "Strong" | "Moderate" | "Weak",
        "momentum": float,  # Rate of change
        "consecutive_moves": int,
        "is_trending": bool
    },

    # Extreme Levels
    "extreme_levels": {
        "is_above_extreme_overbought": bool,
        "is_below_extreme_oversold": bool,
        "is_above_90": bool,  # For orchestrator compatibility
        "extreme_overbought_threshold": float,
        "extreme_oversold_threshold": float
    },

    # Recent Values
    "recent_rsi_values": [float, ...],  # Last 5 values

    # Statistics
    "rsi_stats": {
        "mean": float,
        "max": float,
        "min": float,
        "std": float,
        "median": float
    },

    # Compatibility Fields
    "rsi_zone": str,  # Same as zone
    "rsi_trend": str,  # Same as trend_analysis.direction

    # Configuration
    "parameters": {
        "period": int,
        "overbought_threshold": float,
        "oversold_threshold": float,
        "extreme_overbought": float,
        "extreme_oversold": float
    }
}
```

### DataFrame Columns
The `result.data` DataFrame includes:
- Original OHLCV columns
- `RSI`: RSI values for each row

## Trading Signal Logic

The agent generates trading signals based on:

1. **Zone Transitions** (highest priority):
   - BUY: Moving out of oversold zone (RSI crosses above 30)
   - SELL: Moving into overbought zone (RSI crosses above 70)

2. **Extreme Levels**:
   - BUY: RSI < 10 (extreme oversold)
   - SELL: RSI > 90 (extreme overbought)

3. **Current Zone**:
   - BUY: In oversold zone
   - SELL: In overbought zone
   - NEUTRAL: In neutral zone

## Timeframe Support

The agent works seamlessly across all timeframes:

```python
agent = RSICombinedAgent()

# Daily
daily_result = agent.run(daily_df)

# Weekly
weekly_result = agent.run(weekly_df)

# Monthly
monthly_result = agent.run(monthly_df)
```

**Note**: The default RSI period (14) is calibrated for daily data. For weekly/monthly data, consider adjusting the period accordingly.

## Testing

Run the comprehensive test suite:
```bash
python tests/test_rsi_combined.py
```

This will:
1. Test with real NXT Daily data
2. Test across all timeframes (Daily, Weekly, Monthly)
3. Test with custom configuration
4. Display detailed analysis results
5. Verify all functionality

## Migration from Separate Agents

### Before (Two Agents)
```python
# Old approach with two agents
rsi_agent = RSIAgent(period=14, overbought=70, oversold=30)
rsi_value_agent = RSIValueAgent(period=14)

result1 = rsi_agent.run(df)
result2 = rsi_value_agent.run(df)

signal = result1['summary']['trading_signal']
is_above_90 = result2['output']['is_above_90']
```

### After (One Agent)
```python
# New approach with combined agent
rsi_agent = RSICombinedAgent()
result = rsi_agent.run(df)

signal = result.summary['signal']
is_above_90 = result.summary['extreme_levels']['is_above_90']
trend = result.summary['trend_analysis']['direction']
```

## Advantages Over Separate Agents

1. **Single Calculation**: RSI calculated once, not twice
2. **Better Performance**: Reduced computational overhead
3. **Unified Output**: All analysis in one structured result
4. **Configurable Thresholds**: Adapt to different trading styles
5. **Comprehensive Analysis**: Combines signals, zones, and trends
6. **Timeframe Flexible**: Works across daily, weekly, monthly
7. **Easier Maintenance**: Single codebase to maintain
8. **Backward Compatible**: Works with existing orchestrators

## Integration with Trading System

The Combined RSI Agent is designed to work seamlessly with:
- Orchestrator systems
- Multi-agent trading frameworks
- Backtesting engines
- Real-time trading applications

It follows the `UnifiedAgent` interface for consistent integration across your trading system.

## Example Output

```
RSI ANALYSIS
Current RSI:      80.4
Zone:            Overbought
Trading Signal:  SELL

TREND ANALYSIS
Direction:       Rising
Strength:        Weak
Momentum:        0.81
Is Trending:     Yes

EXTREME LEVELS
Above 90:        No
Above 90 (Extreme OB): No
Below 10 (Extreme OS): No

STATISTICS
Mean:            52.08
Max:             99.21
Min:             0.0
Std:             16.62
Median:          52.29
```

## Requirements

- Python 3.7+
- pandas
- numpy
- UnifiedAgent base class
- config module with RSIConfig

## Best Practices

1. **Choose appropriate thresholds** for your market:
   - Stocks: 70/30
   - Crypto: 80/20
   - Forex: 70/30 or 65/35

2. **Consider timeframe** when setting period:
   - Daily: 14 (standard)
   - Weekly: Keep 14 for consistency
   - Monthly: Consider 12

3. **Use trend analysis** to confirm signals:
   - Strong momentum + signal = high confidence
   - Weak momentum + signal = lower confidence

4. **Monitor extreme levels** for risk management:
   - RSI > 90: High risk for longs
   - RSI < 10: High risk for shorts
