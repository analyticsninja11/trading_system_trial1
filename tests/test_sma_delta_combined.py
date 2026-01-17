"""
Tests for SMA Delta Combined Agent.
"""
import unittest
import pandas as pd
import numpy as np
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.sma_delta_combined_agent import SMADeltaCombinedAgent
from agents.unified_agent import AgentResult
from config import SMADeltaConfig
from exceptions import InsufficientDataError, EmptyDataFrameError, MissingColumnsError


class TestSMADeltaCombinedAgent(unittest.TestCase):
    """Test suite for SMADeltaCombinedAgent."""

    def setUp(self):
        """Set up test fixtures with monthly data."""
        np.random.seed(42)
        # 24 months of data
        dates = pd.date_range(start='2022-01-01', periods=24, freq='ME')

        # Simulate price data with uptrend
        base_price = 100
        trend = np.linspace(0, 40, 24)
        noise = np.random.randn(24) * 3
        close_prices = base_price + trend + noise

        self.df = pd.DataFrame({
            'Date': dates,
            'Open': close_prices * 0.99,
            'High': close_prices * 1.02,
            'Low': close_prices * 0.98,
            'Close': close_prices,
            'Volume': np.random.randint(1000000, 5000000, 24)
        })

    def test_initialization_default_config(self):
        """Test agent initialization with default configuration."""
        agent = SMADeltaCombinedAgent()
        self.assertEqual(agent.name, "SMA Delta Combined Agent")
        self.assertEqual(agent.agent_type, "indicator")
        self.assertEqual(agent.short_period, 6)
        self.assertEqual(agent.long_period, 12)

    def test_initialization_custom_config(self):
        """Test agent initialization with custom configuration."""
        config = SMADeltaConfig(short_lookback_months=3, long_lookback_months=6)
        agent = SMADeltaCombinedAgent(config=config)
        self.assertEqual(agent.short_period, 3)
        self.assertEqual(agent.long_period, 6)

    def test_minimum_rows(self):
        """Test minimum rows calculation."""
        agent = SMADeltaCombinedAgent()
        self.assertEqual(agent.get_minimum_rows(), 13)  # long_period + 1

    def test_successful_execution(self):
        """Test successful execution returns AgentResult."""
        agent = SMADeltaCombinedAgent()
        result = agent.run(self.df)

        self.assertIsInstance(result, AgentResult)
        self.assertTrue(result.is_successful())
        self.assertEqual(result.status, "completed")
        self.assertIsNone(result.error)

    def test_sma_columns_calculated(self):
        """Test SMA columns are calculated."""
        agent = SMADeltaCombinedAgent()
        result = agent.run(self.df)

        self.assertIn('SMA_6', result.data.columns)
        self.assertIn('SMA_12', result.data.columns)
        self.assertIn('SMA_Delta', result.data.columns)

    def test_delta_change_column(self):
        """Test delta change column is calculated."""
        agent = SMADeltaCombinedAgent()
        result = agent.run(self.df)

        self.assertIn('SMA_Delta_Change', result.data.columns)
        self.assertIn('SMA_Delta_Percent', result.data.columns)

    def test_summary_structure(self):
        """Test summary contains expected keys."""
        agent = SMADeltaCombinedAgent()
        result = agent.run(self.df)

        expected_keys = [
            'sma_delta', 'sma_delta_percent', 'sma_delta_trend',
            'trend_strength', 'is_delta_rising', 'is_delta_positive',
            'is_favorable_for_buy', 'signal', 'current_values',
            'trend_analysis', 'parameters'
        ]

        for key in expected_keys:
            self.assertIn(key, result.summary)

    def test_signal_generation(self):
        """Test signal is BUY, SELL, or NEUTRAL."""
        agent = SMADeltaCombinedAgent()
        result = agent.run(self.df)

        self.assertIn(result.summary['signal'], ['BUY', 'SELL', 'NEUTRAL'])
        self.assertEqual(result.summary['signal'], result.get_signal())

    def test_rising_delta_means_buy(self):
        """Test that rising delta results in BUY signal."""
        agent = SMADeltaCombinedAgent()
        result = agent.run(self.df)

        if result.summary['is_delta_rising']:
            self.assertEqual(result.summary['signal'], 'BUY')
        else:
            self.assertEqual(result.summary['signal'], 'SELL')

    def test_trend_descriptions(self):
        """Test trend descriptions are valid."""
        agent = SMADeltaCombinedAgent()
        result = agent.run(self.df)

        valid_trends = [
            "Positive and Rising",
            "Negative but Rising",
            "Positive but Falling",
            "Negative and Falling"
        ]
        self.assertIn(result.summary['sma_delta_trend'], valid_trends)

    def test_trend_strength_values(self):
        """Test trend strength has valid values."""
        agent = SMADeltaCombinedAgent()
        result = agent.run(self.df)

        valid_strengths = ['STRONGLY_BULLISH', 'BULLISH', 'BEARISH', 'STRONGLY_BEARISH']
        self.assertIn(result.summary['trend_strength'], valid_strengths)

    def test_favorable_for_buy_logic(self):
        """Test favorable for buy matches is_rising."""
        agent = SMADeltaCombinedAgent()
        result = agent.run(self.df)

        self.assertEqual(
            result.summary['is_favorable_for_buy'],
            result.summary['is_delta_rising']
        )

    def test_current_values_structure(self):
        """Test current values contains expected keys."""
        agent = SMADeltaCombinedAgent()
        result = agent.run(self.df)

        current = result.summary['current_values']
        self.assertIn('close', current)
        self.assertIn('sma_6', current)
        self.assertIn('sma_12', current)

    def test_trend_analysis_structure(self):
        """Test trend analysis contains expected keys."""
        agent = SMADeltaCombinedAgent()
        result = agent.run(self.df)

        trend = result.summary['trend_analysis']
        self.assertIn('direction', trend)
        self.assertIn('consecutive_periods', trend)
        self.assertIn('momentum', trend)
        self.assertIn('last_deltas', trend)

    def test_delta_stats_structure(self):
        """Test delta stats contains expected keys."""
        agent = SMADeltaCombinedAgent()
        result = agent.run(self.df)

        stats = result.summary['delta_stats']
        self.assertIn('mean', stats)
        self.assertIn('max', stats)
        self.assertIn('min', stats)
        self.assertIn('std', stats)

    def test_insufficient_data_error(self):
        """Test error handling for insufficient data."""
        small_df = self.df.head(5)  # Less than required rows
        agent = SMADeltaCombinedAgent()
        result = agent.run(small_df)

        self.assertFalse(result.is_successful())
        self.assertEqual(result.status, "failed")
        self.assertIn("InsufficientDataError", result.error)

    def test_empty_dataframe_error(self):
        """Test error handling for empty DataFrame."""
        agent = SMADeltaCombinedAgent()
        result = agent.run(pd.DataFrame())

        self.assertFalse(result.is_successful())
        self.assertIn("EmptyDataFrameError", result.error)

    def test_missing_columns_error(self):
        """Test error handling for missing columns."""
        df_missing = self.df.drop(columns=['Close'])
        agent = SMADeltaCombinedAgent()
        result = agent.run(df_missing)

        self.assertFalse(result.is_successful())
        self.assertIn("MissingColumnsError", result.error)

    def test_parameters_in_summary(self):
        """Test parameters are included in summary."""
        config = SMADeltaConfig(short_lookback_months=3, long_lookback_months=9)
        agent = SMADeltaCombinedAgent(config=config)
        result = agent.run(self.df)

        params = result.summary['parameters']
        self.assertEqual(params['short_period'], 3)
        self.assertEqual(params['long_period'], 9)

    def test_backward_compatibility(self):
        """Test backward compatibility fields."""
        agent = SMADeltaCombinedAgent()
        result = agent.run(self.df)

        self.assertEqual(result.summary['signal'], result.summary['trading_signal'])

    def test_is_rising_last_2_periods(self):
        """Test is_rising_last_2_periods field."""
        agent = SMADeltaCombinedAgent()
        result = agent.run(self.df)

        self.assertIn('is_rising_last_2_periods', result.summary)
        self.assertIsInstance(result.summary['is_rising_last_2_periods'], bool)

    def test_last_deltas_list(self):
        """Test last deltas is a list of floats."""
        agent = SMADeltaCombinedAgent()
        result = agent.run(self.df)

        last_deltas = result.summary['trend_analysis']['last_deltas']
        self.assertIsInstance(last_deltas, list)
        self.assertGreater(len(last_deltas), 0)
        for delta in last_deltas:
            self.assertIsInstance(delta, float)

    def test_custom_periods_columns(self):
        """Test custom periods create correct column names."""
        config = SMADeltaConfig(short_lookback_months=3, long_lookback_months=6)
        agent = SMADeltaCombinedAgent(config=config)
        result = agent.run(self.df)

        self.assertIn('SMA_3', result.data.columns)
        self.assertIn('SMA_6', result.data.columns)


class TestSMADeltaConfigValidation(unittest.TestCase):
    """Test SMADeltaConfig validation."""

    def test_valid_config(self):
        """Test valid configuration passes validation."""
        config = SMADeltaConfig(short_lookback_months=6, long_lookback_months=12)
        config.validate()  # Should not raise

    def test_invalid_short_greater_than_long(self):
        """Test validation fails when short >= long."""
        config = SMADeltaConfig(short_lookback_months=12, long_lookback_months=6)
        with self.assertRaises(ValueError):
            config.validate()

    def test_invalid_negative_period(self):
        """Test validation fails for negative periods."""
        config = SMADeltaConfig(short_lookback_months=-1, long_lookback_months=12)
        with self.assertRaises(ValueError):
            config.validate()


if __name__ == '__main__':
    unittest.main()
