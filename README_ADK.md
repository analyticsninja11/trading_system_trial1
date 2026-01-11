## Google ADK-Compatible Agentic Trading System

A multi-agent trading system compatible with Google's Agent Development Kit (ADK). The system uses a **Base Orchestrator Agent** that coordinates **4 specialized sub-agents** running in parallel to generate BUY signals.

---

## 🏗️ Architecture

### Base Agent (Orchestrator)
- Coordinates all sub-agents with parallel processing
- Evaluates BUY signals using 2-of-4 condition logic
- Compatible with Google ADK standards

### Sub-Agents

1. **MACD Seasonal Agent** (Daily Timeframe)
   - Identifies market seasons based on MACD histogram
   - **Spring**: Histogram < 0, two consecutive bars increasing
   - **Summer**: Histogram > 0, two consecutive bars increasing
   - **Autumn**: Histogram > 0, two consecutive bars decreasing
   - **Winter**: Histogram < 0, two consecutive bars decreasing
   - **Output**: Current season

2. **RSI Value Agent** (Daily Timeframe)
   - Calculates Relative Strength Index
   - Period: 14 days (default)
   - **Output**: Actual RSI value (0-100)

3. **SMA Delta Agent** (Monthly Timeframe)
   - Calculates 6-month and 12-month Simple Moving Averages
   - **Output**: Delta between SMAs and trend (rising/falling)

4. **Supertrend Agent** (Daily Timeframe)
   - Calculates Supertrend indicator using ATR
   - ATR Length: 10 (configurable)
   - Multiplier: 3.0 (configurable)
   - **Output**: Green (bullish) or Red (bearish)

---

## 🎯 BUY Signal Logic

**BUY signal is triggered when 2 out of 4 conditions are met:**

| Condition | Requirement |
|-----------|-------------|
| 1. MACD Season | Spring OR Summer |
| 2. RSI Value | NOT above 90 |
| 3. SMA Delta | (Negative AND Rising) OR (Positive AND Rising) for last 2 monthly points |
| 4. Supertrend | Green signal |

---

## 🚀 Quick Start

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run via Command Line
```bash
# Basic usage
python main_adk.py --ticker googl

# With custom parameters
python main_adk.py --ticker googl --mode parallel --atr-length 10 --atr-multiplier 3.0

# With date filtering (UK format)
python main_adk.py --ticker aapl --start-date 01/01/2024 --end-date 31/03/2024
```

### Run via Web UI
```bash
streamlit run ui/app_adk.py
```

---

## 📋 Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--ticker` | Stock ticker symbol (required) | - |
| `--start-date` | Start date in DD/MM/YYYY (UK format) | None |
| `--end-date` | End date in DD/MM/YYYY (UK format) | None |
| `--mode` | Execution mode: parallel or sequential | parallel |
| `--atr-length` | Supertrend ATR length | 10 |
| `--atr-multiplier` | Supertrend ATR multiplier | 3.0 |

---

## 📊 Data Format

Place CSV files in the `data/` folder with naming convention:
- `{ticker}_daily.csv` - Daily price data
- `{ticker}_weekly.csv` - Weekly price data (optional)
- `{ticker}_monthly.csv` - Monthly price data (optional)

**The DataImportAgent automatically handles multiple CSV formats:**

### Format 1: Standard OHLCV
```csv
Date,Open,High,Low,Close,Volume
2021-01-04,100.5,102.3,99.8,101.2,1000000
```

### Format 2: Time-based (auto-converted)
```csv
time,open,high,low,close
2021-01-04,100.5,102.3,99.8,101.2
```

**Note:** Volume column is optional and will be added automatically if missing.

**Example files:**
- `googl_daily.csv` - Standard format
- `aapl_daily.csv` - Standard format
- `nxt_daily.csv` - Normalized from time format
- `googl_monthly.csv` - Monthly data

See [DATA_IMPORT_GUIDE.md](DATA_IMPORT_GUIDE.md) for complete import documentation.

---

## 🤖 Agent Execution Flow

```
1. Orchestrator Agent initializes
   ↓
2. Load daily and monthly data
   ↓
3. Run 4 sub-agents in PARALLEL:
   - MACD Seasonal Agent (daily data)
   - RSI Value Agent (daily data)
   - SMA Delta Agent (monthly data)
   - Supertrend Agent (daily data)
   ↓
4. Collect all sub-agent outputs
   ↓
5. Evaluate 4 conditions
   ↓
6. Generate BUY signal if ≥ 2 conditions met
   ↓
7. Return recommendation: BUY or HOLD/WAIT
```

---

## 💻 Usage Examples

### Example 1: Quick Analysis
```bash
python main_adk.py --ticker googl
```

**Output:**
```
🎯 Final Recommendation: BUY
Signal Strength: 3/4 conditions met

1. MACD Season: Summer ✅
2. RSI Value: 65.23 ✅
3. SMA Delta: Positive and Rising ✅
4. Supertrend: Red ❌
```

### Example 2: Custom Date Range
```bash
python main_adk.py --ticker aapl --start-date 01/01/2024 --end-date 31/03/2024
```

### Example 3: Custom Supertrend Parameters
```bash
python main_adk.py --ticker googl --atr-length 14 --atr-multiplier 2.5
```

---

## 🌐 Web UI Features

Launch with: `streamlit run ui/app_adk.py`

**Features:**
- Ticker selection dropdown
- Date range picker (UK format)
- Configurable Supertrend parameters
- BUY signal dashboard
- Detailed condition breakdown
- Individual sub-agent result tabs
- Interactive price charts
- Real-time analysis

---

## 📁 Project Structure

```
trading_system_trial1/
├── agents/
│   ├── sub_agent.py              # Base sub-agent class
│   ├── orchestrator_agent.py     # Base orchestrator agent
│   ├── macd_seasonal_agent.py    # MACD seasonal sub-agent
│   ├── rsi_value_agent.py        # RSI value sub-agent
│   ├── sma_delta_agent.py        # SMA delta sub-agent
│   └── supertrend_agent.py       # Supertrend sub-agent
├── utils/
│   ├── __init__.py               # Utils package
│   └── data_importer.py          # DataImportAgent for CSV handling
├── data/
│   ├── googl_daily.csv           # Google daily data
│   ├── googl_monthly.csv         # Google monthly data
│   ├── aapl_daily.csv            # Apple daily data
│   ├── nxt_daily.csv             # NXT daily data
│   └── nxt_monthly.csv           # NXT monthly data
├── ui/
│   └── app_adk.py                # Streamlit UI
├── main_adk.py                   # CLI entry point
├── requirements.txt              # Dependencies
├── README_ADK.md                 # Main documentation
├── QUICKSTART.md                 # Quick start guide
└── DATA_IMPORT_GUIDE.md          # Data import documentation
```

---

## 🔧 Google ADK Compatibility

This system follows Google ADK principles:

1. **Orchestrator Pattern**: Base agent coordinates sub-agents
2. **Parallel Processing**: Sub-agents run concurrently
3. **Clear Interfaces**: Standardized input/output formats
4. **Modular Design**: Easy to add new sub-agents
5. **Error Handling**: Graceful failure handling
6. **Logging**: Comprehensive execution logging

---

## 🧪 Testing

Test the system:

```bash
# Test MACD seasonal logic
python -c "
from agents.macd_seasonal_agent import MACDSeasonalAgent
import pandas as pd
df = pd.read_csv('data/googl_daily.csv')
agent = MACDSeasonalAgent()
result = agent.run(df)
print(result['output'])
"

# Test orchestrator
python main_adk.py --ticker googl --mode parallel
```

---

## 📈 Performance

**Execution Times** (approximate, 60 days of data):
- Sequential Mode: ~2-3 seconds
- Parallel Mode: ~1-1.5 seconds
- Speedup: ~2x with parallel execution

---

## 🔄 Extending the System

### Adding a New Sub-Agent

1. Create new agent file in `agents/`:

```python
from agents.sub_agent import SubAgent

class MyNewAgent(SubAgent):
    def __init__(self):
        super().__init__(name="My New Agent")

    def process(self, df):
        # Your logic here
        return {"output": "result"}
```

2. Add to orchestrator in `orchestrator_agent.py`:

```python
from .my_new_agent import MyNewAgent

class OrchestratorAgent:
    def __init__(self):
        # ... existing code ...
        self.my_agent = MyNewAgent()
        self.sub_agents.append(self.my_agent)
```

3. Update BUY signal logic if needed

---

## 📝 Output Format

### CLI Output
Results are saved to `{ticker}_analysis_results.txt`:
```
Analysis Date: 11/01/2026 18:30:45
Ticker: GOOGL
BUY Signal: BUY
Conditions Met: 3/4

Individual Conditions:
  condition_1_macd_season: ✅
  condition_2_rsi_check: ✅
  condition_3_sma_delta: ✅
  condition_4_supertrend: ❌
```

### Programmatic Access
```python
from agents.orchestrator_agent import OrchestratorAgent
import pandas as pd

daily_df = pd.read_csv('data/googl_daily.csv')
orchestrator = OrchestratorAgent()
results = orchestrator.run(daily_df, mode='parallel')

buy_signal = results['buy_signal_evaluation']['buy_signal']
conditions_met = results['buy_signal_evaluation']['conditions_met']
```

---

## ⚙️ Configuration

### Modify Agent Parameters

```python
orchestrator = OrchestratorAgent()

# Customize MACD
orchestrator.macd_agent.fast_period = 10
orchestrator.macd_agent.slow_period = 20

# Customize RSI
orchestrator.rsi_agent.period = 20

# Customize SMA
orchestrator.sma_agent.short_period = 3
orchestrator.sma_agent.long_period = 6

# Customize Supertrend
orchestrator.supertrend_agent.atr_length = 14
orchestrator.supertrend_agent.multiplier = 2.5
```

---

## 🛠️ Troubleshooting

**Issue**: "File not found" error
- **Solution**: Ensure CSV files are in `data/` folder with correct naming

**Issue**: "Insufficient data" warnings
- **Solution**: Ensure CSV has enough rows (minimum 26 for MACD, 14 for RSI)

**Issue**: Monthly data not found
- **Solution**: System will auto-resample from daily data if monthly CSV is missing

**Issue**: All conditions failing
- **Solution**: Check data quality and date ranges

---

## 📦 Dependencies

- pandas >= 1.5.0
- numpy >= 1.24.0
- streamlit >= 1.28.0
- plotly >= 5.17.0

Install all: `pip install -r requirements.txt`

---

## 📄 License

MIT License
