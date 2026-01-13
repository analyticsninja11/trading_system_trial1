# MACD Combined Agent

## Overview
The **MACD Combined Agent** is a comprehensive technical analysis tool that merges standard MACD indicator calculations with seasonal pattern recognition. This agent combines the functionality of both `MACDAgent` and `MACDSeasonalAgent` into a single, powerful analysis tool.

## Features

### 1. Standard MACD Analysis
- **MACD Line**: 12-period EMA - 26-period EMA
- **Signal Line**: 9-period EMA of MACD
- **Histogram**: MACD - Signal Line
- **Trend Detection**: BULLISH/BEARISH
- **Crossover Detection**: Identifies bullish and bearish crossovers
- **Trading Signals**: BUY, SELL, or NEUTRAL based on crossovers

### 2. Seasonal Pattern Recognition
Identifies four market "seasons" based on MACD histogram patterns:

| Season | Condition | Interpretation |
|--------|-----------|----------------|
| **Spring** | Histogram < 0, increasing | Accumulation phase - potential reversal from bearish to bullish |
| **Summer** | Histogram > 0, increasing | Strong bullish trend - momentum increasing |
| **Autumn** | Histogram > 0, decreasing | Distribution phase - potential reversal from bullish to bearish |
| **Winter** | Histogram < 0, decreasing | Strong bearish trend - momentum decreasing |

### 3. Intelligent Recommendations
Generates trading recommendations by analyzing confluence between:
- Standard MACD signals
- Seasonal patterns
- Overall trend direction
- Histogram momentum

## Usage

### Basic Usage
```python
from agents.macd_combined_agent import MACDCombinedAgent
import pandas as pd

# Prepare your OHLCV data
df = pd.DataFrame({
    'Open': [...],
    'High': [...],
    'Low': [...],
    'Close': [...],
    'Volume': [...]  # Optional
})

# Initialize agent (uses default config)
agent = MACDCombinedAgent()

# Run analysis
result = agent.run(df)

# Check if successful
if result.is_successful():
    summary = result.summary

    # Access standard MACD data
    print(f"Signal: {summary['signal']}")
    print(f"Trend: {summary['trend']}")
    print(f"MACD: {summary['latest_macd']}")

    # Access seasonal analysis
    seasonal = summary['seasonal_analysis']
    print(f"Season: {seasonal['current_season']}")
    print(f"Is Bullish Season: {seasonal['is_bullish_season']}")

    # Access recommendation
    rec = summary['recommendation']
    print(f"Action: {rec['action']}")
    print(f"Confidence: {rec['confidence']}")
    print(f"Reasoning: {rec['reasoning']}")
else:
    print(f"Error: {result.error}")
```

### With Custom Configuration
```python
from agents.macd_combined_agent import MACDCombinedAgent
from config import MACDConfig

# Custom MACD parameters
custom_config = MACDConfig(
    fast_period=8,
    slow_period=21,
    signal_period=5
)

agent = MACDCombinedAgent(config=custom_config)
result = agent.run(df)
```

### Using with Import Script
```python
from agents.macd_combined_agent import MACDCombinedAgent
from scripts.import_price_data import import_ticker_data
import pandas as pd

# Import data
nxt_data = import_ticker_data('NXT', data_dir='data')
df_daily = nxt_data['daily']

# Convert to agent format (capital letters for columns)
df_agent = pd.DataFrame({
    'Open': df_daily['open'],
    'High': df_daily['high'],
    'Low': df_daily['low'],
    'Close': df_daily['close']
})

# Run agent
agent = MACDCombinedAgent()
result = agent.run(df_agent)
```

## Output Structure

### AgentResult Object
```python
result = agent.run(df)

# Properties
result.agent_name       # "MACD Combined Agent"
result.status          # "completed" or "failed"
result.data            # DataFrame with MACD columns added
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
    # Standard MACD Analysis
    "latest_macd": float,
    "latest_signal": float,
    "latest_histogram": float,
    "trend": "BULLISH" | "BEARISH",
    "crossover": "BULLISH_CROSSOVER" | "BEARISH_CROSSOVER" | None,
    "signal": "BUY" | "SELL" | "NEUTRAL",
    "parameters": {
        "fast_period": int,
        "slow_period": int,
        "signal_period": int
    },

    # Seasonal Analysis
    "seasonal_analysis": {
        "current_season": "Spring" | "Summer" | "Autumn" | "Winter" | "Neutral",
        "is_bullish_season": bool,
        "histogram_trend": "Increasing" | "Decreasing",
        "histogram_momentum": float,
        "recent_histogram_values": [float, ...],
        "season_distribution": {season: count},
        "season_interpretation": str
    },

    # Recommendation
    "recommendation": {
        "action": "BUY" | "SELL" | "NEUTRAL",
        "strength": "STRONG" | "MODERATE" | "WEAK",
        "confidence": "HIGH" | "MEDIUM" | "LOW",
        "reasoning": [str, ...],
        "confluence": bool  # True if signal and season align
    }
}
```

### DataFrame Columns
The `result.data` DataFrame includes:
- Original OHLCV columns
- `MACD`: MACD line values
- `MACD_Signal`: Signal line values
- `MACD_Histogram`: Histogram values

## Recommendation Logic

### Signal Strength & Confidence

| Condition | Strength | Confidence | Explanation |
|-----------|----------|------------|-------------|
| BUY + Bullish Season | STRONG | HIGH | Signal and season align perfectly |
| BUY + Bearish Season | WEAK | LOW | Signal conflicts with season |
| SELL + Bearish Season | STRONG | HIGH | Signal and season align perfectly |
| SELL + Bullish Season | WEAK | LOW | Signal conflicts with season |
| NEUTRAL | MODERATE | MEDIUM | No clear signal |

### Confluence
**Confluence** occurs when the trading signal aligns with the seasonal pattern:
- ✓ BUY signal during Spring or Summer (bullish seasons)
- ✓ SELL signal during Autumn or Winter (bearish seasons)
- ✗ BUY signal during Autumn or Winter
- ✗ SELL signal during Spring or Summer

## Testing

Run the comprehensive test suite:
```bash
python tests/test_macd_combined.py
```

This will:
1. Test with real NXT Daily data
2. Test across all timeframes (Daily, Weekly, Monthly)
3. Display detailed analysis results
4. Verify all functionality

## Requirements

- Python 3.7+
- pandas
- numpy
- UnifiedAgent base class
- config module with MACDConfig

## Migration from Separate Agents

If you're currently using `MACDAgent` and `MACDSeasonalAgent` separately:

### Before:
```python
macd_agent = MACDAgent()
seasonal_agent = MACDSeasonalAgent()

macd_result = macd_agent.run(df)
seasonal_result = seasonal_agent.run(df)
```

### After:
```python
combined_agent = MACDCombinedAgent()
result = combined_agent.run(df)

# Access both analyses in one result
signal = result.summary['signal']
season = result.summary['seasonal_analysis']['current_season']
recommendation = result.summary['recommendation']
```

## Advantages Over Separate Agents

1. **Single Calculation**: MACD calculated once instead of twice
2. **Integrated Analysis**: Recommendations consider both signals and seasons
3. **Better Performance**: Reduced computational overhead
4. **Simplified Interface**: One agent call instead of two
5. **Confluence Detection**: Automatically identifies when signals align with seasons
6. **Comprehensive Output**: All analysis in one structured result

## Example Output

```
STANDARD MACD ANALYSIS
======================
MACD Line:                     117.082
Signal Line:                   23.5667
Histogram:                     93.5153
Trend:                         BULLISH
Trading Signal:                NEUTRAL

SEASONAL ANALYSIS
=================
Current Season:                Summer
Interpretation:                Strong bullish trend - momentum increasing
Bullish Season:                Yes
Histogram Trend:               Increasing
Histogram Momentum:            20.2006

RECOMMENDATION
==============
Action:                        NEUTRAL
Strength:                      MODERATE
Confidence:                    MEDIUM
Signal-Season Confluence:      No

Reasoning:
  • No clear trading signal at this time
  • Overall trend: BULLISH
```

## Integration with Trading System

The Combined MACD Agent is designed to work seamlessly with:
- Orchestrator systems
- Multi-agent trading frameworks
- Backtesting engines
- Real-time trading applications

It follows the `UnifiedAgent` interface for consistent integration across your trading system.
