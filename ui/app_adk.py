"""
Streamlit UI for Google ADK-compatible Agentic Trading System
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.orchestrator_agent import OrchestratorAgent
from utils.data_importer import DataImportAgent

# Initialize data import agent
data_importer = DataImportAgent()


def get_available_tickers():
    """Scan data folder for available ticker CSV files using DataImportAgent."""
    return data_importer.get_available_tickers()


def load_data(ticker: str, timeframe: str, start_date: str = None, end_date: str = None):
    """Load price data from CSV file using DataImportAgent."""
    try:
        df = data_importer.load_ticker_data(ticker, timeframe, start_date, end_date)
        return df
    except FileNotFoundError:
        return None


def create_price_chart(df):
    """Create candlestick chart with volume."""
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.7, 0.3],
        subplot_titles=('Price', 'Volume')
    )

    fig.add_trace(
        go.Candlestick(
            x=df['Date'],
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Price'
        ),
        row=1, col=1
    )

    colors = ['red' if close < open else 'green'
              for close, open in zip(df['Close'], df['Open'])]

    fig.add_trace(
        go.Bar(x=df['Date'], y=df['Volume'], name='Volume', marker_color=colors),
        row=2, col=1
    )

    fig.update_layout(height=600, xaxis_rangeslider_visible=False, showlegend=False)
    return fig


def main():
    st.set_page_config(
        page_title="ADK Trading System",
        page_icon="🤖",
        layout="wide"
    )

    st.title("🤖 Google ADK-Compatible Agentic Trading System")
    st.markdown("**Multi-Agent System with Orchestrator Base Agent**")

    # Sidebar
    st.sidebar.header("Configuration")

    available_tickers = get_available_tickers()
    if not available_tickers:
        st.error("No daily data files found in the 'data' folder.")
        return

    selected_ticker = st.sidebar.selectbox("Select Ticker", options=available_tickers)

    # Date range
    st.sidebar.subheader("Date Range")
    use_date_filter = st.sidebar.checkbox("Filter by date range", value=False)

    start_date = None
    end_date = None

    if use_date_filter:
        col1, col2 = st.sidebar.columns(2)
        with col1:
            start_date_input = st.date_input("Start Date", value=datetime(2024, 1, 1))
            start_date = start_date_input.strftime("%d/%m/%Y")
        with col2:
            end_date_input = st.date_input("End Date", value=datetime.now())
            end_date = end_date_input.strftime("%d/%m/%Y")

        st.sidebar.caption(f"UK Format: {start_date} to {end_date}")

    # Agent parameters
    st.sidebar.subheader("Supertrend Parameters")
    atr_length = st.sidebar.number_input("ATR Length", min_value=1, max_value=50, value=10)
    atr_multiplier = st.sidebar.number_input("ATR Multiplier", min_value=0.5, max_value=10.0, value=3.0, step=0.5)

    # Execution mode
    execution_mode = st.sidebar.radio(
        "Execution Mode",
        options=["Parallel", "Sequential"],
        help="Parallel runs all sub-agents simultaneously"
    )

    # Run button
    run_button = st.sidebar.button("🚀 Run Analysis", type="primary", use_container_width=True)

    # Initialize session state
    if 'results' not in st.session_state:
        st.session_state.results = None

    # Run analysis
    if run_button:
        with st.spinner("Running orchestrator agent..."):
            # Load daily data
            daily_df = load_data(selected_ticker, 'daily', start_date, end_date)

            if daily_df is None or len(daily_df) == 0:
                st.error("Failed to load daily data")
                return

            # Load monthly data
            monthly_df = load_data(selected_ticker, 'monthly', start_date, end_date)

            # Create orchestrator
            orchestrator = OrchestratorAgent()
            orchestrator.supertrend_agent.atr_length = atr_length
            orchestrator.supertrend_agent.multiplier = atr_multiplier

            # Run
            mode = execution_mode.lower()
            results = orchestrator.run(daily_df, monthly_df, mode=mode)

            # Store
            st.session_state.results = results
            st.session_state.daily_df = daily_df
            st.session_state.monthly_df = monthly_df
            st.session_state.ticker = selected_ticker

        st.success("Analysis completed!")

    # Display results
    if st.session_state.results:
        results = st.session_state.results
        buy_eval = results["buy_signal_evaluation"]

        # BUY Signal Header
        st.header("🎯 BUY Signal Analysis")

        signal = buy_eval["recommendation"]
        if signal == "BUY":
            st.success(f"### ✅ {signal}")
        else:
            st.warning(f"### ⏸️ {signal}")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Conditions Met", f"{buy_eval['conditions_met']}/4")
        with col2:
            st.metric("Required", f"{buy_eval['conditions_required']}/4")
        with col3:
            confidence = (buy_eval['conditions_met'] / 4) * 100
            st.metric("Signal Strength", f"{confidence:.0f}%")

        # Condition breakdown
        st.subheader("📊 Condition Breakdown")

        details = buy_eval["condition_details"]

        col1, col2 = st.columns(2)

        with col1:
            # Condition 1: MACD
            if "macd" in details:
                macd = details["macd"]
                status = "✅" if macd["condition_met"] else "❌"
                st.markdown(f"**{status} 1. MACD Season**")
                st.write(f"Current Season: **{macd['season']}**")
                st.write(f"Is Bullish: {macd['is_bullish']}")
                st.caption("Required: Spring or Summer")

            st.markdown("---")

            # Condition 3: SMA
            if "sma" in details:
                sma = details["sma"]
                status = "✅" if sma["condition_met"] else "❌"
                st.markdown(f"**{status} 3. SMA Delta**")
                st.write(f"Delta: **{sma['delta']}**")
                st.write(f"Trend: {sma['trend']}")
                st.write(f"Rising (Last 2 months): {sma['is_rising_last_2_months']}")
                st.caption("Required: Negative & Rising OR Positive & Rising")

        with col2:
            # Condition 2: RSI
            if "rsi" in details:
                rsi = details["rsi"]
                status = "✅" if rsi["condition_met"] else "❌"
                st.markdown(f"**{status} 2. RSI Value**")
                st.write(f"Current RSI: **{rsi['rsi_value']}**")
                st.write(f"Is Above 90: {rsi['is_above_90']}")
                st.caption("Required: Not above 90")

            st.markdown("---")

            # Condition 4: Supertrend
            if "supertrend" in details:
                st_data = details["supertrend"]
                status = "✅" if st_data["condition_met"] else "❌"
                st.markdown(f"**{status} 4. Supertrend**")
                signal_color = "🟢" if st_data['is_green'] else "🔴"
                st.write(f"Signal: **{signal_color} {st_data['signal']}**")
                st.write(f"Is Green: {st_data['is_green']}")
                st.caption("Required: Green")

        # Sub-agent results
        st.header("🤖 Sub-Agent Detailed Results")

        tabs = st.tabs(["MACD Seasonal", "RSI Value", "SMA Delta", "Supertrend"])

        # MACD Tab
        with tabs[0]:
            macd_result = results["sub_agent_results"]["MACD"]
            if macd_result["status"] == "completed":
                output = macd_result["output"]

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Current Season", output["current_season"])
                with col2:
                    st.metric("Latest Histogram", output["latest_histogram"])
                with col3:
                    st.metric("Histogram Trend", output["histogram_trend"])

                st.subheader("Season Distribution")
                if "season_distribution" in output:
                    st.bar_chart(output["season_distribution"])

                st.subheader("Recent Histogram Values")
                st.line_chart(output["recent_histogram_values"])

                with st.expander("Parameters"):
                    st.json(output["parameters"])

        # RSI Tab
        with tabs[1]:
            rsi_result = results["sub_agent_results"]["RSI"]
            if rsi_result["status"] == "completed":
                output = rsi_result["output"]

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("RSI Value", output["rsi_value"])
                with col2:
                    st.metric("RSI Zone", output["rsi_zone"])
                with col3:
                    st.metric("RSI Trend", output["rsi_trend"])

                st.subheader("Recent RSI Values")
                st.line_chart(output["recent_rsi_values"])

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Is Above 90", "Yes" if output["is_above_90"] else "No")
                with col2:
                    with st.expander("RSI Statistics"):
                        st.json(output["rsi_stats"])

        # SMA Tab
        with tabs[2]:
            sma_result = results["sub_agent_results"]["SMA"]
            if sma_result["status"] == "completed":
                output = sma_result["output"]

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("SMA Delta", output["sma_delta"])
                with col2:
                    st.metric("Trend", output["sma_delta_trend"])
                with col3:
                    favorable = "Yes" if output["is_favorable_for_buy"] else "No"
                    st.metric("Favorable for BUY", favorable)

                st.subheader("Last 2 Monthly Deltas")
                st.line_chart(output["last_2_monthly_deltas"])

                with st.expander("Current SMA Values"):
                    st.json(output["current_sma_values"])

        # Supertrend Tab
        with tabs[3]:
            st_result = results["sub_agent_results"]["Supertrend"]
            if st_result["status"] == "completed":
                output = st_result["output"]

                col1, col2, col3 = st.columns(3)
                with col1:
                    signal_emoji = "🟢" if output["is_green"] else "🔴"
                    st.metric("Signal", f"{signal_emoji} {output['supertrend_signal']}")
                with col2:
                    st.metric("Distance from ST", output["distance_from_supertrend"])
                with col3:
                    st.metric("Trend Stability", output["trend_stability"])

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Current Close", output["current_close"])
                    st.metric("Supertrend Value", output["supertrend_value"])
                with col2:
                    st.metric("Current ATR", output["current_atr"])
                    st.metric("Signal Changes (Last 5)", output["signal_changes_last_5"])

                st.subheader("Recent Signals")
                st.write(" → ".join(output["recent_signals"]))

        # Price chart
        st.header("📈 Price Chart")
        daily_df = st.session_state.daily_df
        fig = create_price_chart(daily_df)
        st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
