"""
Streamlit UI for Agentic Trading System
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

from orchestrator import AgentOrchestrator


def get_available_tickers():
    """
    Scan data folder for available ticker CSV files.

    Returns:
        List of tuples: (display_name, ticker, timeframe)
    """
    data_dir = "data"
    tickers = []

    if os.path.exists(data_dir):
        for filename in os.listdir(data_dir):
            if filename.endswith('.csv'):
                # Parse filename: ticker_timeframe.csv
                name_parts = filename.replace('.csv', '').split('_')
                if len(name_parts) >= 2:
                    ticker = name_parts[0]
                    timeframe = '_'.join(name_parts[1:])
                    display_name = f"{ticker.upper()} ({timeframe.capitalize()})"
                    tickers.append((display_name, ticker, timeframe))

    return sorted(tickers, key=lambda x: x[0])


def create_price_chart(df):
    """
    Create candlestick chart with volume.

    Args:
        df: DataFrame with OHLCV data

    Returns:
        Plotly figure
    """
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.7, 0.3],
        subplot_titles=('Price', 'Volume')
    )

    # Candlestick chart
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

    # Volume bars
    colors = ['red' if close < open else 'green'
              for close, open in zip(df['Close'], df['Open'])]

    fig.add_trace(
        go.Bar(
            x=df['Date'],
            y=df['Volume'],
            name='Volume',
            marker_color=colors
        ),
        row=2, col=1
    )

    fig.update_layout(
        height=600,
        xaxis_rangeslider_visible=False,
        showlegend=False
    )

    return fig


def create_indicator_chart(df, indicator_type):
    """
    Create chart for specific indicator.

    Args:
        df: DataFrame with indicator data
        indicator_type: Type of indicator ('MACD', 'SMA', 'RSI')

    Returns:
        Plotly figure
    """
    fig = go.Figure()

    if indicator_type == 'MACD':
        # MACD line
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['MACD'],
            name='MACD', line=dict(color='blue', width=2)
        ))

        # Signal line
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['MACD_Signal'],
            name='Signal', line=dict(color='red', width=2)
        ))

        # Histogram
        colors = ['green' if val >= 0 else 'red' for val in df['MACD_Histogram']]
        fig.add_trace(go.Bar(
            x=df['Date'], y=df['MACD_Histogram'],
            name='Histogram', marker_color=colors
        ))

        fig.update_layout(
            title='MACD Indicator',
            yaxis_title='MACD Value',
            height=400
        )

    elif indicator_type == 'SMA':
        # Price
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['Close'],
            name='Price', line=dict(color='black', width=2)
        ))

        # SMAs
        if 'SMA_20' in df.columns:
            fig.add_trace(go.Scatter(
                x=df['Date'], y=df['SMA_20'],
                name='SMA 20', line=dict(color='blue', width=2)
            ))

        if 'SMA_50' in df.columns:
            fig.add_trace(go.Scatter(
                x=df['Date'], y=df['SMA_50'],
                name='SMA 50', line=dict(color='red', width=2)
            ))

        fig.update_layout(
            title='Simple Moving Averages',
            yaxis_title='Price',
            height=400
        )

    elif indicator_type == 'RSI':
        # RSI line
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['RSI'],
            name='RSI', line=dict(color='purple', width=2)
        ))

        # Overbought line
        fig.add_hline(y=70, line_dash="dash", line_color="red",
                      annotation_text="Overbought (70)")

        # Oversold line
        fig.add_hline(y=30, line_dash="dash", line_color="green",
                      annotation_text="Oversold (30)")

        # Middle line
        fig.add_hline(y=50, line_dash="dot", line_color="gray")

        fig.update_layout(
            title='Relative Strength Index (RSI)',
            yaxis_title='RSI Value',
            height=400,
            yaxis=dict(range=[0, 100])
        )

    fig.update_xaxis_title('Date')
    return fig


def main():
    """
    Main Streamlit application.
    """
    st.set_page_config(
        page_title="Agentic Trading System",
        page_icon="📈",
        layout="wide"
    )

    st.title("📈 Agentic Trading System")
    st.markdown("Multi-Agent Technical Indicator Analysis")

    # Sidebar controls
    st.sidebar.header("Configuration")

    # Get available tickers
    available_tickers = get_available_tickers()

    if not available_tickers:
        st.error("No data files found in the 'data' folder. Please add CSV files.")
        return

    # Ticker selection
    ticker_options = {display: (ticker, timeframe)
                      for display, ticker, timeframe in available_tickers}
    selected_display = st.sidebar.selectbox(
        "Select Ticker",
        options=list(ticker_options.keys())
    )
    selected_ticker, selected_timeframe = ticker_options[selected_display]

    # Date range selection
    st.sidebar.subheader("Date Range")

    use_date_filter = st.sidebar.checkbox("Filter by date range", value=False)

    start_date = None
    end_date = None

    if use_date_filter:
        col1, col2 = st.sidebar.columns(2)
        with col1:
            start_date_input = st.date_input(
                "Start Date",
                value=datetime(2024, 1, 1)
            )
            start_date = start_date_input.strftime("%d/%m/%Y")

        with col2:
            end_date_input = st.date_input(
                "End Date",
                value=datetime.now()
            )
            end_date = end_date_input.strftime("%d/%m/%Y")

        st.sidebar.caption(f"UK Format: {start_date} to {end_date}")

    # Execution mode
    execution_mode = st.sidebar.radio(
        "Execution Mode",
        options=["Sequential", "Parallel"],
        help="Sequential runs agents one by one. Parallel runs all agents simultaneously."
    )

    # Run analysis button
    run_button = st.sidebar.button("🚀 Run Analysis", type="primary", use_container_width=True)

    # Initialize session state
    if 'orchestrator' not in st.session_state:
        st.session_state.orchestrator = None
    if 'results' not in st.session_state:
        st.session_state.results = None

    # Run analysis
    if run_button:
        with st.spinner("Running agentic workflow..."):
            # Create orchestrator
            orchestrator = AgentOrchestrator()
            orchestrator.initialize_agents()

            # Load data
            success = orchestrator.load_data(
                ticker=selected_ticker,
                timeframe=selected_timeframe,
                start_date=start_date,
                end_date=end_date
            )

            if not success:
                st.error("Failed to load data. Please check the ticker and date range.")
                return

            # Run agents
            if execution_mode == "Sequential":
                results = orchestrator.run_agents_sequential()
            else:
                results = orchestrator.run_agents_parallel()

            # Store in session state
            st.session_state.orchestrator = orchestrator
            st.session_state.results = results

        st.success("Analysis completed successfully!")

    # Display results
    if st.session_state.results:
        results = st.session_state.results
        orchestrator = st.session_state.orchestrator

        # Overview metrics
        st.header("📊 Analysis Overview")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Ticker", results['ticker'])
        with col2:
            st.metric("Timeframe", results['timeframe'].capitalize())
        with col3:
            st.metric("Data Points", results['data_points'])
        with col4:
            st.metric("Execution Mode", results['execution_mode'].capitalize())

        # Date range
        st.caption(f"Period: {results['date_range']['start']} to {results['date_range']['end']}")

        # Consolidated signals
        st.header("🎯 Consolidated Trading Signals")

        consolidated = orchestrator.get_consolidated_signals()

        col1, col2, col3 = st.columns(3)
        with col1:
            signal = consolidated['overall_signal']
            color = "green" if signal == "BUY" else "red" if signal == "SELL" else "gray"
            st.markdown(f"### Overall Signal: :{color}[{signal}]")
        with col2:
            st.metric("Confidence", f"{consolidated['confidence']}%")
        with col3:
            st.metric("Active Agents", consolidated['total_agents'])

        # Individual signals breakdown
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("BUY Signals", consolidated['individual_signals']['BUY'])
        with col2:
            st.metric("SELL Signals", consolidated['individual_signals']['SELL'])
        with col3:
            st.metric("NEUTRAL Signals", consolidated['individual_signals']['NEUTRAL'])

        # Agent results
        st.header("🤖 Agent Results")

        tabs = st.tabs([agent_name for agent_name in results['agents'].keys()])

        for tab, (agent_name, result) in zip(tabs, results['agents'].items()):
            with tab:
                if result['status'] == 'completed' and result['summary']:
                    # Summary metrics
                    st.subheader("Summary")

                    summary = result['summary']

                    # Display key metrics
                    cols = st.columns(3)
                    col_idx = 0

                    for key, value in summary.items():
                        if key not in ['parameters', 'rsi_stats', 'sma_values', 'price_position'] and not isinstance(value, dict):
                            with cols[col_idx % 3]:
                                st.metric(key.replace('_', ' ').title(), value)
                                col_idx += 1

                    # Display parameters
                    if 'parameters' in summary:
                        st.subheader("Parameters")
                        st.json(summary['parameters'])

                    # Display chart
                    st.subheader("Indicator Chart")
                    combined_df = orchestrator.get_combined_dataframe()

                    if 'MACD' in agent_name:
                        fig = create_indicator_chart(combined_df, 'MACD')
                    elif 'SMA' in agent_name:
                        fig = create_indicator_chart(combined_df, 'SMA')
                    elif 'RSI' in agent_name:
                        fig = create_indicator_chart(combined_df, 'RSI')
                    else:
                        fig = None

                    if fig:
                        st.plotly_chart(fig, use_container_width=True)

                elif result['error']:
                    st.error(f"Agent failed: {result['error']}")

        # Price chart
        st.header("📈 Price Chart")
        combined_df = orchestrator.get_combined_dataframe()
        price_fig = create_price_chart(combined_df)
        st.plotly_chart(price_fig, use_container_width=True)

        # Data table
        with st.expander("📋 View Raw Data"):
            st.dataframe(combined_df, use_container_width=True)

            # Download button
            csv = combined_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"{results['ticker']}_{results['timeframe']}_analysis.csv",
                mime="text/csv"
            )


if __name__ == "__main__":
    main()
