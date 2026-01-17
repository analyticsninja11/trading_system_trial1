"""
Tests for Supertrend Combined Agent.
"""
import unittest
import pandas as pd
import numpy as np
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.supertrend_combined_agent import SupertrendCombinedAgent
from agents.unified_agent import AgentResult
from config import SupertrendConfig
from exceptions import InsufficientDataError, EmptyDataFrameError, MissingColumnsError


class TestSupertrendCombinedAgent(unittest.TestCase):
    """Test suite for SupertrendCombinedAgent."""

    def setUp(self):
        """Set up test fixtures."""
        np.random.seed(42)
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')

        # Simulate price data with uptrend
        base_price = 100
        trend = np.linspace(0, 30, 100)
        noise = np.random.randn(100) * 2
        close_prices = base_price + trend + noise

        self.df = pd.DataFrame({
            'Date': dates,
            'Open': close_prices * (1 + np.random.uniform(-0.005, 0.005, 100)),
            'High': close_prices * (1 + np.abs(np.random.randn(100)) * 0.015),
            'Low': close_prices * (1 - np.abs(np.random.randn(100)) * 0.015),
            'Close': close_prices,
            'Volume': np.random.randint(1000000, 5000000, 100)
        })

        # Ensure High >= max(Open, Close) and Low <= min(Open, Close)
        self.df['High'] = self.df[['High', 'Close', 'Open']].max(axis=1)
        self.df['Low'] = self.df[['Low', 'Close', 'Open']].min(axis=1)

    def test_initialization_default_config(self):
        """Test agent initialization with default configuration."""
        agent = SupertrendCombinedAgent()
        self.assertEqual(agent.name, "Supertrend Combined Agent")
        self.assertEqual(agent.agent_type, "indicator")
        self.assertEqual(agent.atr_length, 10)
        self.assertEqual(agent.multiplier, 3.0)

    def test_initialization_custom_config(self):
        """Test agent initialization with custom configuration."""
        config = SupertrendConfig(atr_length=14, atr_multiplier=2.0)
        agent = SupertrendCombinedAgent(config=config)
        self.assertEqual(agent.atr_length, 14)
        self.assertEqual(agent.multiplier, 2.0)

    def test_minimum_rows(self):
        """Test minimum rows calculation."""
        agent = SupertrendCombinedAgent()
        self.assertEqual(agent.get_minimum_rows(), 12)  # atr_length + 2

    def test_successful_execution(self):
        """Test successful execution returns AgentResult."""
        agent = SupertrendCombinedAgent()
        result = agent.run(self.df)

        self.assertIsInstance(result, AgentResult)
        self.assertTrue(result.is_successful())
        self.assertEqual(result.status, "completed")
        self.assertIsNone(result.error)

    def test_atr_calculation(self):
        """Test ATR column is calculated."""
        agent = SupertrendCombinedAgent()
        result = agent.run(self.df)

        self.assertIn('ATR', result.data.columns)
        # ATR should have some valid values (not all NaN)
        self.assertFalse(result.data['ATR'].dropna().empty)

    def test_supertrend_columns(self):
        """Test Supertrend columns are calculated."""
        agent = SupertrendCombinedAgent()
        result = agent.run(self.df)

        self.assertIn('Supertrend', result.data.columns)
        self.assertIn('Supertrend_Signal', result.data.columns)
        self.assertIn('Supertrend_Direction', result.data.columns)
        self.assertIn('Upper_Band', result.data.columns)
        self.assertIn('Lower_Band', result.data.columns)

    def test_summary_structure(self):
        """Test summary contains expected keys."""
        agent = SupertrendCombinedAgent()
        result = agent.run(self.df)

        expected_keys = [
            'supertrend_signal', 'is_green', 'signal',
            'current_close', 'supertrend_value',
            'distance_from_supertrend', 'distance_percent',
            'current_atr', 'trend_analysis', 'parameters'
        ]

        for key in expected_keys:
            self.assertIn(key, result.summary)

    def test_signal_values(self):
        """Test supertrend signal is Green or Red."""
        agent = SupertrendCombinedAgent()
        result = agent.run(self.df)

        self.assertIn(result.summary['supertrend_signal'], ['Green', 'Red'])
        self.assertIsInstance(result.summary['is_green'], bool)

    def test_trading_signal(self):
        """Test trading signal is BUY or SELL."""
        agent = SupertrendCombinedAgent()
        result = agent.run(self.df)

        self.assertIn(result.summary['signal'], ['BUY', 'SELL'])
        self.assertEqual(result.summary['signal'], result.get_signal())

    def test_green_signal_means_buy(self):
        """Test that Green signal results in BUY."""
        agent = SupertrendCombinedAgent()
        result = agent.run(self.df)

        if result.summary['is_green']:
            self.assertEqual(result.summary['signal'], 'BUY')
        else:
            self.assertEqual(result.summary['signal'], 'SELL')

    def test_trend_analysis_structure(self):
        """Test trend analysis contains expected keys."""
        agent = SupertrendCombinedAgent()
        result = agent.run(self.df)

        trend = result.summary['trend_analysis']
        self.assertIn('stability', trend)
        self.assertIn('duration', trend)
        self.assertIn('signal_changes_last_5', trend)
        self.assertIn('recent_signals', trend)

    def test_trend_stability_values(self):
        """Test trend stability has valid values."""
        agent = SupertrendCombinedAgent()
        result = agent.run(self.df)

        valid_stability = ['Very Stable', 'Stable', 'Moderate', 'Volatile']
        self.assertIn(result.summary['trend_analysis']['stability'], valid_stability)

    def test_distance_calculations(self):
        """Test distance from Supertrend calculations."""
        agent = SupertrendCombinedAgent()
        result = agent.run(self.df)

        self.assertIsNotNone(result.summary['distance_from_supertrend'])
        self.assertIsNotNone(result.summary['distance_percent'])

    def test_band_values(self):
        """Test upper and lower band values are present."""
        agent = SupertrendCombinedAgent()
        result = agent.run(self.df)

        self.assertIsNotNone(result.summary['upper_band'])
        self.assertIsNotNone(result.summary['lower_band'])

    def test_insufficient_data_error(self):
        """Test error handling for insufficient data."""
        small_df = self.df.head(5)  # Less than required rows
        agent = SupertrendCombinedAgent()
        result = agent.run(small_df)

        self.assertFalse(result.is_successful())
        self.assertEqual(result.status, "failed")
        self.assertIn("InsufficientDataError", result.error)

    def test_empty_dataframe_error(self):
        """Test error handling for empty DataFrame."""
        agent = SupertrendCombinedAgent()
        result = agent.run(pd.DataFrame())

        self.assertFalse(result.is_successful())
        self.assertIn("EmptyDataFrameError", result.error)

    def test_missing_columns_error(self):
        """Test error handling for missing columns."""
        df_missing = self.df.drop(columns=['High'])
        agent = SupertrendCombinedAgent()
        result = agent.run(df_missing)

        self.assertFalse(result.is_successful())
        self.assertIn("MissingColumnsError", result.error)

    def test_parameters_in_summary(self):
        """Test parameters are included in summary."""
        config = SupertrendConfig(atr_length=14, atr_multiplier=2.5)
        agent = SupertrendCombinedAgent(config=config)
        result = agent.run(self.df)

        params = result.summary['parameters']
        self.assertEqual(params['atr_length'], 14)
        self.assertEqual(params['multiplier'], 2.5)

    def test_backward_compatibility(self):
        """Test backward compatibility fields."""
        agent = SupertrendCombinedAgent()
        result = agent.run(self.df)

        self.assertEqual(result.summary['signal'], result.summary['trading_signal'])

    def test_recent_signals_list(self):
        """Test recent signals is a list of valid values."""
        agent = SupertrendCombinedAgent()
        result = agent.run(self.df)

        recent = result.summary['trend_analysis']['recent_signals']
        self.assertIsInstance(recent, list)
        self.assertEqual(len(recent), 5)
        for signal in recent:
            self.assertIn(signal, ['Green', 'Red'])


class TestSupertrendConfigValidation(unittest.TestCase):
    """Test SupertrendConfig validation."""

    def test_valid_config(self):
        """Test valid configuration passes validation."""
        config = SupertrendConfig(atr_length=14, atr_multiplier=2.0)
        config.validate()  # Should not raise

    def test_invalid_atr_length(self):
        """Test validation fails for invalid ATR length."""
        config = SupertrendConfig(atr_length=0, atr_multiplier=2.0)
        with self.assertRaises(ValueError):
            config.validate()

    def test_invalid_multiplier(self):
        """Test validation fails for invalid multiplier."""
        config = SupertrendConfig(atr_length=10, atr_multiplier=0)
        with self.assertRaises(ValueError):
            config.validate()


if __name__ == '__main__':
    unittest.main()
