"""
Unit tests for MACD Agent (refactored version).
"""
import unittest
import pandas as pd
import numpy as np
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.macd_agent_refactored import MACDAgent
from config import MACDConfig


class TestMACDAgent(unittest.TestCase):
    """Test MACD Agent functionality."""

    def setUp(self):
        """Set up test data."""
        # Create sample price data with a clear trend
        dates = pd.date_range('2024-01-01', periods=100)

        # Create uptrend for testing
        base_price = 100
        trend = np.linspace(0, 20, 100)
        noise = np.random.normal(0, 2, 100)
        prices = base_price + trend + noise

        self.df = pd.DataFrame({
            'Date': dates,
            'Open': prices + np.random.uniform(-1, 1, 100),
            'High': prices + np.random.uniform(1, 3, 100),
            'Low': prices + np.random.uniform(-3, -1, 100),
            'Close': prices,
            'Volume': np.random.randint(1000000, 2000000, 100)
        })

    def test_agent_initialization_default(self):
        """Test MACD agent initialization with default config."""
        agent = MACDAgent()

        self.assertEqual(agent.name, "MACD Agent")
        self.assertEqual(agent.fast_period, 12)
        self.assertEqual(agent.slow_period, 26)
        self.assertEqual(agent.signal_period, 9)

    def test_agent_initialization_custom_config(self):
        """Test MACD agent initialization with custom config."""
        config = MACDConfig(fast_period=10, slow_period=20, signal_period=5)
        agent = MACDAgent(config=config)

        self.assertEqual(agent.fast_period, 10)
        self.assertEqual(agent.slow_period, 20)
        self.assertEqual(agent.signal_period, 5)

    def test_minimum_rows(self):
        """Test minimum rows requirement."""
        agent = MACDAgent()
        min_rows = agent.get_minimum_rows()

        # Should be slow_period + signal_period
        self.assertEqual(min_rows, 26 + 9)

    def test_successful_calculation(self):
        """Test successful MACD calculation."""
        agent = MACDAgent()
        result = agent.run(self.df)

        self.assertTrue(result.is_successful())
        self.assertEqual(result.status, "completed")
        self.assertIsNone(result.error)

    def test_output_columns(self):
        """Test that MACD calculation adds correct columns."""
        agent = MACDAgent()
        result = agent.run(self.df)

        df = result.data
        self.assertIn('MACD', df.columns)
        self.assertIn('MACD_Signal', df.columns)
        self.assertIn('MACD_Histogram', df.columns)

    def test_macd_calculation_logic(self):
        """Test MACD calculation produces expected values."""
        agent = MACDAgent()
        result = agent.run(self.df)

        df = result.data

        # MACD should not be all NaN
        self.assertFalse(df['MACD'].isna().all())

        # Histogram should equal MACD - Signal
        histogram_check = np.allclose(
            df['MACD_Histogram'].dropna(),
            (df['MACD'] - df['MACD_Signal']).dropna(),
            rtol=1e-5
        )
        self.assertTrue(histogram_check)

    def test_summary_generation(self):
        """Test summary statistics generation."""
        agent = MACDAgent()
        result = agent.run(self.df)

        summary = result.summary

        # Check required fields
        self.assertIn('latest_macd', summary)
        self.assertIn('latest_signal', summary)
        self.assertIn('latest_histogram', summary)
        self.assertIn('trend', summary)
        self.assertIn('parameters', summary)

        # Check parameter values
        params = summary['parameters']
        self.assertEqual(params['fast_period'], 12)
        self.assertEqual(params['slow_period'], 26)
        self.assertEqual(params['signal_period'], 9)

    def test_trend_detection(self):
        """Test trend detection (bullish/bearish)."""
        agent = MACDAgent()
        result = agent.run(self.df)

        summary = result.summary
        trend = summary['trend']

        # Should be either BULLISH or BEARISH
        self.assertIn(trend, ['BULLISH', 'BEARISH'])

    def test_signal_generation(self):
        """Test trading signal generation."""
        agent = MACDAgent()
        result = agent.run(self.df)

        signal = result.get_signal()

        # Should be one of the valid signals
        self.assertIn(signal, ['BUY', 'SELL', 'NEUTRAL'])

    def test_insufficient_data(self):
        """Test handling of insufficient data."""
        agent = MACDAgent()
        small_df = self.df.head(20)  # Less than required minimum

        result = agent.run(small_df)

        self.assertEqual(result.status, "failed")
        self.assertIn("InsufficientDataError", result.error)

    def test_bullish_crossover_detection(self):
        """Test detection of bullish crossover."""
        # Create data that will produce a bullish crossover
        dates = pd.date_range('2024-01-01', periods=50)

        # Downtrend then uptrend
        prices = np.concatenate([
            np.linspace(110, 100, 25),  # Downtrend
            np.linspace(100, 115, 25)   # Uptrend
        ])

        df = pd.DataFrame({
            'Date': dates,
            'Open': prices,
            'High': prices + 1,
            'Low': prices - 1,
            'Close': prices,
            'Volume': np.ones(50) * 1000000
        })

        agent = MACDAgent()
        result = agent.run(df)

        summary = result.summary

        # Check if crossover detected (may or may not be at the last point)
        self.assertIn('crossover', summary)

    def test_process_method_returns_required_keys(self):
        """Test that process method returns all required keys."""
        agent = MACDAgent()
        result = agent.run(self.df)

        # Check result has expected components
        self.assertIsNotNone(result.data)
        self.assertIsNotNone(result.summary)

        # Verify process output structure
        process_result = agent.process(self.df)
        self.assertIn('data', process_result)
        self.assertIn('summary', process_result)
        # Signal should be in summary
        self.assertIn('signal', process_result['summary'])


if __name__ == '__main__':
    unittest.main()
