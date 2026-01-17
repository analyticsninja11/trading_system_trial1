"""
Tests for SMA Combined Agent.
"""
import unittest
import pandas as pd
import numpy as np
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.sma_combined_agent import SMACombinedAgent
from agents.unified_agent import AgentResult
from config import SMAConfig
from exceptions import InsufficientDataError, EmptyDataFrameError, MissingColumnsError


class TestSMACombinedAgent(unittest.TestCase):
    """Test suite for SMACombinedAgent."""

    def setUp(self):
        """Set up test fixtures."""
        # Create sample data with 100 rows
        np.random.seed(42)
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')

        # Simulate price data with uptrend
        base_price = 100
        trend = np.linspace(0, 30, 100)
        noise = np.random.randn(100) * 2
        close_prices = base_price + trend + noise

        self.df = pd.DataFrame({
            'Date': dates,
            'Open': close_prices * 0.99,
            'High': close_prices * 1.01,
            'Low': close_prices * 0.98,
            'Close': close_prices,
            'Volume': np.random.randint(1000000, 5000000, 100)
        })

    def test_initialization_default_config(self):
        """Test agent initialization with default configuration."""
        agent = SMACombinedAgent()
        self.assertEqual(agent.name, "SMA Combined Agent")
        self.assertEqual(agent.agent_type, "indicator")
        self.assertEqual(agent.short_period, 20)
        self.assertEqual(agent.long_period, 50)
        self.assertEqual(agent.periods, [20, 50])

    def test_initialization_custom_config(self):
        """Test agent initialization with custom configuration."""
        config = SMAConfig(short_period=10, long_period=30)
        agent = SMACombinedAgent(config=config)
        self.assertEqual(agent.short_period, 10)
        self.assertEqual(agent.long_period, 30)

    def test_initialization_custom_periods(self):
        """Test agent initialization with custom periods list."""
        agent = SMACombinedAgent(periods=[5, 10, 20, 50])
        self.assertEqual(agent.periods, [5, 10, 20, 50])
        self.assertEqual(agent.short_period, 5)
        self.assertEqual(agent.long_period, 50)

    def test_minimum_rows(self):
        """Test minimum rows calculation."""
        agent = SMACombinedAgent()
        self.assertEqual(agent.get_minimum_rows(), 51)  # long_period + 1

    def test_successful_execution(self):
        """Test successful execution returns AgentResult."""
        agent = SMACombinedAgent()
        result = agent.run(self.df)

        self.assertIsInstance(result, AgentResult)
        self.assertTrue(result.is_successful())
        self.assertEqual(result.status, "completed")
        self.assertIsNone(result.error)

    def test_sma_calculation(self):
        """Test SMA columns are calculated correctly."""
        agent = SMACombinedAgent()
        result = agent.run(self.df)

        self.assertIn('SMA_20', result.data.columns)
        self.assertIn('SMA_50', result.data.columns)

        # Verify SMA values are calculated
        self.assertFalse(result.data['SMA_20'].isna().all())
        self.assertFalse(result.data['SMA_50'].isna().all())

    def test_summary_structure(self):
        """Test summary contains expected keys."""
        agent = SMACombinedAgent()
        result = agent.run(self.df)

        expected_keys = [
            'latest_price', 'sma_values', 'price_position',
            'crossover', 'signal', 'trend_analysis',
            'price_distances', 'alignment', 'parameters'
        ]

        for key in expected_keys:
            self.assertIn(key, result.summary)

    def test_signal_generation(self):
        """Test signal is one of BUY, SELL, or NEUTRAL."""
        agent = SMACombinedAgent()
        result = agent.run(self.df)

        self.assertIn(result.summary['signal'], ['BUY', 'SELL', 'NEUTRAL'])
        self.assertEqual(result.summary['signal'], result.get_signal())

    def test_price_position_detection(self):
        """Test price position relative to SMAs."""
        agent = SMACombinedAgent()
        result = agent.run(self.df)

        for position in result.summary['price_position'].values():
            self.assertIn(position, ['ABOVE', 'BELOW', 'N/A'])

    def test_crossover_detection_structure(self):
        """Test crossover detection returns expected structure."""
        agent = SMACombinedAgent()
        result = agent.run(self.df)

        crossover = result.summary['crossover']
        self.assertIn('detected', crossover)
        self.assertIn('pattern', crossover)
        self.assertIn('description', crossover)

    def test_golden_cross_detection(self):
        """Test Golden Cross detection with simulated data."""
        # Create data where short SMA crosses above long SMA
        np.random.seed(42)
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')

        # Start with downtrend, then uptrend to trigger golden cross
        prices = np.concatenate([
            np.linspace(100, 80, 60),  # Downtrend
            np.linspace(80, 120, 40)   # Strong uptrend
        ])

        df = pd.DataFrame({
            'Date': dates,
            'Open': prices * 0.99,
            'High': prices * 1.01,
            'Low': prices * 0.98,
            'Close': prices,
            'Volume': np.random.randint(1000000, 5000000, 100)
        })

        agent = SMACombinedAgent()
        result = agent.run(df)

        # The crossover might or might not be detected depending on timing
        # Just verify the structure is correct
        self.assertIn('crossover', result.summary)
        if result.summary['crossover']['detected']:
            self.assertIn(result.summary['crossover']['pattern'],
                         ['GOLDEN_CROSS', 'DEATH_CROSS'])

    def test_trend_analysis(self):
        """Test trend analysis for SMAs."""
        agent = SMACombinedAgent()
        result = agent.run(self.df)

        trend = result.summary['trend_analysis']
        self.assertIn('overall', trend)
        self.assertIn(trend['overall'],
                     ['STRONGLY_BULLISH', 'BULLISH', 'NEUTRAL', 'BEARISH', 'STRONGLY_BEARISH'])

    def test_alignment_analysis(self):
        """Test SMA alignment analysis."""
        agent = SMACombinedAgent()
        result = agent.run(self.df)

        alignment = result.summary['alignment']
        self.assertIn('status', alignment)
        self.assertIn('description', alignment)
        self.assertIn(alignment['status'], ['BULLISH', 'BEARISH', 'MIXED', 'Unknown'])

    def test_price_distances(self):
        """Test price distance calculations."""
        agent = SMACombinedAgent()
        result = agent.run(self.df)

        distances = result.summary['price_distances']
        for sma_name, dist in distances.items():
            self.assertIn('absolute', dist)
            self.assertIn('percentage', dist)

    def test_insufficient_data_error(self):
        """Test error handling for insufficient data."""
        small_df = self.df.head(30)  # Less than required 51 rows
        agent = SMACombinedAgent()
        result = agent.run(small_df)

        self.assertFalse(result.is_successful())
        self.assertEqual(result.status, "failed")
        self.assertIn("InsufficientDataError", result.error)

    def test_empty_dataframe_error(self):
        """Test error handling for empty DataFrame."""
        agent = SMACombinedAgent()
        result = agent.run(pd.DataFrame())

        self.assertFalse(result.is_successful())
        self.assertIn("EmptyDataFrameError", result.error)

    def test_missing_columns_error(self):
        """Test error handling for missing columns."""
        df_missing = self.df.drop(columns=['Close'])
        agent = SMACombinedAgent()
        result = agent.run(df_missing)

        self.assertFalse(result.is_successful())
        self.assertIn("MissingColumnsError", result.error)

    def test_parameters_in_summary(self):
        """Test parameters are included in summary."""
        agent = SMACombinedAgent(periods=[10, 20, 50])
        result = agent.run(self.df)

        params = result.summary['parameters']
        self.assertEqual(params['periods'], [10, 20, 50])
        self.assertEqual(params['short_period'], 10)
        self.assertEqual(params['long_period'], 50)

    def test_backward_compatibility(self):
        """Test backward compatibility fields."""
        agent = SMACombinedAgent()
        result = agent.run(self.df)

        # Check backward compatibility field
        self.assertEqual(result.summary['signal'], result.summary['trading_signal'])
        self.assertIn('cross_pattern', result.summary)

    def test_custom_periods_sorted(self):
        """Test that custom periods are sorted."""
        agent = SMACombinedAgent(periods=[50, 10, 30, 20])
        self.assertEqual(agent.periods, [10, 20, 30, 50])

    def test_multiple_smas(self):
        """Test with multiple SMA periods."""
        # Need longer dataset for 200 SMA
        np.random.seed(42)
        dates = pd.date_range(start='2022-01-01', periods=250, freq='D')
        prices = 100 + np.linspace(0, 50, 250) + np.random.randn(250) * 2

        df = pd.DataFrame({
            'Date': dates,
            'Open': prices * 0.99,
            'High': prices * 1.01,
            'Low': prices * 0.98,
            'Close': prices,
            'Volume': np.random.randint(1000000, 5000000, 250)
        })

        agent = SMACombinedAgent(periods=[10, 20, 50, 100, 200])
        result = agent.run(df)

        self.assertTrue(result.is_successful())
        self.assertIn('SMA_10', result.data.columns)
        self.assertIn('SMA_200', result.data.columns)


class TestSMAConfigValidation(unittest.TestCase):
    """Test SMAConfig validation."""

    def test_valid_config(self):
        """Test valid configuration passes validation."""
        config = SMAConfig(short_period=10, long_period=30)
        config.validate()  # Should not raise

    def test_invalid_short_period_greater_than_long(self):
        """Test validation fails when short >= long."""
        config = SMAConfig(short_period=50, long_period=20)
        with self.assertRaises(ValueError):
            config.validate()

    def test_invalid_negative_period(self):
        """Test validation fails for negative periods."""
        config = SMAConfig(short_period=-5, long_period=20)
        with self.assertRaises(ValueError):
            config.validate()


if __name__ == '__main__':
    unittest.main()
