"""
Unit tests for configuration module.
"""
import unittest
import json
import tempfile
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import (
    TradingSystemConfig,
    MACDConfig,
    RSIConfig,
    SMAConfig,
    SupertrendConfig,
    OrchestratorConfig
)
from exceptions import ConfigurationError


class TestMACDConfig(unittest.TestCase):
    """Test MACD configuration."""

    def test_default_values(self):
        """Test default MACD configuration values."""
        config = MACDConfig()
        self.assertEqual(config.fast_period, 12)
        self.assertEqual(config.slow_period, 26)
        self.assertEqual(config.signal_period, 9)

    def test_custom_values(self):
        """Test custom MACD configuration values."""
        config = MACDConfig(fast_period=10, slow_period=20, signal_period=5)
        self.assertEqual(config.fast_period, 10)
        self.assertEqual(config.slow_period, 20)
        self.assertEqual(config.signal_period, 5)

    def test_validation_success(self):
        """Test successful MACD validation."""
        config = MACDConfig()
        config.validate()  # Should not raise

    def test_validation_fast_greater_than_slow(self):
        """Test MACD validation fails when fast >= slow."""
        config = MACDConfig(fast_period=26, slow_period=12)
        with self.assertRaises(ValueError) as context:
            config.validate()
        self.assertIn("fast_period must be less than slow_period", str(context.exception))

    def test_validation_negative_period(self):
        """Test MACD validation fails with negative periods."""
        config = MACDConfig(fast_period=-1, slow_period=26)
        with self.assertRaises(ValueError) as context:
            config.validate()
        self.assertIn("positive integers", str(context.exception))


class TestRSIConfig(unittest.TestCase):
    """Test RSI configuration."""

    def test_default_values(self):
        """Test default RSI configuration values."""
        config = RSIConfig()
        self.assertEqual(config.period, 14)
        self.assertEqual(config.overbought_threshold, 70.0)
        self.assertEqual(config.oversold_threshold, 30.0)

    def test_validation_success(self):
        """Test successful RSI validation."""
        config = RSIConfig()
        config.validate()  # Should not raise

    def test_validation_threshold_order(self):
        """Test RSI validation fails when oversold >= overbought."""
        config = RSIConfig(oversold_threshold=80, overbought_threshold=20)
        with self.assertRaises(ValueError):
            config.validate()

    def test_validation_negative_period(self):
        """Test RSI validation fails with negative period."""
        config = RSIConfig(period=-5)
        with self.assertRaises(ValueError):
            config.validate()


class TestSMAConfig(unittest.TestCase):
    """Test SMA configuration."""

    def test_default_values(self):
        """Test default SMA configuration values."""
        config = SMAConfig()
        self.assertEqual(config.short_period, 20)
        self.assertEqual(config.long_period, 50)

    def test_validation_success(self):
        """Test successful SMA validation."""
        config = SMAConfig()
        config.validate()  # Should not raise

    def test_validation_short_greater_than_long(self):
        """Test SMA validation fails when short >= long."""
        config = SMAConfig(short_period=50, long_period=20)
        with self.assertRaises(ValueError):
            config.validate()


class TestTradingSystemConfig(unittest.TestCase):
    """Test master trading system configuration."""

    def test_default_config(self):
        """Test default configuration creation."""
        config = TradingSystemConfig()
        self.assertIsInstance(config.macd, MACDConfig)
        self.assertIsInstance(config.rsi, RSIConfig)
        self.assertIsInstance(config.sma, SMAConfig)

    def test_validate_all(self):
        """Test validation of all sub-configurations."""
        config = TradingSystemConfig()
        config.validate()  # Should not raise

    def test_to_dict(self):
        """Test conversion to dictionary."""
        config = TradingSystemConfig()
        config_dict = config.to_dict()

        self.assertIn("macd", config_dict)
        self.assertIn("rsi", config_dict)
        self.assertIn("sma", config_dict)
        self.assertEqual(config_dict["macd"]["fast_period"], 12)
        self.assertEqual(config_dict["rsi"]["period"], 14)

    def test_from_dict(self):
        """Test creation from dictionary."""
        config_dict = {
            "macd": {"fast_period": 10, "slow_period": 20, "signal_period": 5},
            "rsi": {"period": 10, "overbought_threshold": 75, "oversold_threshold": 25}
        }
        config = TradingSystemConfig.from_dict(config_dict)

        self.assertEqual(config.macd.fast_period, 10)
        self.assertEqual(config.rsi.period, 10)

    def test_json_serialization(self):
        """Test JSON save and load."""
        config = TradingSystemConfig()
        config.macd.fast_period = 15

        # Save to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
            config.to_json_file(temp_path)

        try:
            # Load from file
            loaded_config = TradingSystemConfig.from_json_file(temp_path)
            self.assertEqual(loaded_config.macd.fast_period, 15)
        finally:
            # Cleanup
            os.unlink(temp_path)


class TestOrchestratorConfig(unittest.TestCase):
    """Test Orchestrator configuration."""

    def test_default_values(self):
        """Test default orchestrator configuration."""
        config = OrchestratorConfig()
        self.assertEqual(config.min_buy_conditions, 2)
        self.assertEqual(config.default_execution_mode, "parallel")
        self.assertEqual(config.max_workers, 4)

    def test_validation_success(self):
        """Test successful orchestrator validation."""
        config = OrchestratorConfig()
        config.validate()  # Should not raise

    def test_validation_invalid_mode(self):
        """Test orchestrator validation fails with invalid execution mode."""
        config = OrchestratorConfig(default_execution_mode="invalid")
        with self.assertRaises(ValueError) as context:
            config.validate()
        self.assertIn("parallel", str(context.exception))


if __name__ == '__main__':
    unittest.main()
