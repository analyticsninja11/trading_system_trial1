"""
Unit tests for UnifiedAgent base class.
"""
import unittest
import pandas as pd
import numpy as np
import sys
import os
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.unified_agent import UnifiedAgent, AgentResult
from exceptions import (
    EmptyDataFrameError,
    MissingColumnsError,
    InsufficientDataError
)


class TestAgent(UnifiedAgent):
    """Test agent implementation for testing."""

    def __init__(self, min_rows=1):
        super().__init__(name="Test Agent", agent_type="test")
        self._min_rows = min_rows

    def process(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Simple test processing."""
        return {
            "data": df,
            "output": {"test": "value", "signal": "NEUTRAL"},
            "summary": {"rows": len(df)}
        }

    def get_minimum_rows(self) -> int:
        return self._min_rows


class FailingAgent(UnifiedAgent):
    """Agent that always fails for testing error handling."""

    def __init__(self):
        super().__init__(name="Failing Agent")

    def process(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Always raises an exception."""
        raise RuntimeError("Intentional failure for testing")


class TestAgentResult(unittest.TestCase):
    """Test AgentResult class."""

    def test_initialization(self):
        """Test AgentResult initialization."""
        result = AgentResult(
            agent_name="Test",
            status="completed",
            output={"value": 42}
        )
        self.assertEqual(result.agent_name, "Test")
        self.assertEqual(result.status, "completed")
        self.assertEqual(result.output["value"], 42)

    def test_to_dict(self):
        """Test conversion to dictionary."""
        result = AgentResult(
            agent_name="Test",
            status="completed",
            output={"value": 42}
        )
        result_dict = result.to_dict()

        self.assertEqual(result_dict["agent"], "Test")
        self.assertEqual(result_dict["status"], "completed")
        self.assertEqual(result_dict["output"]["value"], 42)

    def test_is_successful(self):
        """Test success check."""
        # Successful result
        result = AgentResult(agent_name="Test", status="completed")
        self.assertTrue(result.is_successful())

        # Failed result
        result = AgentResult(agent_name="Test", status="failed", error="Error message")
        self.assertFalse(result.is_successful())

    def test_get_signal(self):
        """Test signal extraction."""
        # Signal in output
        result = AgentResult(
            agent_name="Test",
            status="completed",
            output={"signal": "BUY"}
        )
        self.assertEqual(result.get_signal(), "BUY")

        # Signal in summary
        result = AgentResult(
            agent_name="Test",
            status="completed",
            summary={"signal": "SELL"}
        )
        self.assertEqual(result.get_signal(), "SELL")

        # No signal
        result = AgentResult(agent_name="Test", status="completed")
        self.assertIsNone(result.get_signal())


class TestUnifiedAgent(unittest.TestCase):
    """Test UnifiedAgent base class."""

    def setUp(self):
        """Set up test data."""
        # Create sample OHLCV data
        dates = pd.date_range('2024-01-01', periods=100)
        self.df = pd.DataFrame({
            'Date': dates,
            'Open': np.random.uniform(100, 110, 100),
            'High': np.random.uniform(110, 120, 100),
            'Low': np.random.uniform(90, 100, 100),
            'Close': np.random.uniform(100, 110, 100),
            'Volume': np.random.randint(1000000, 2000000, 100)
        })

    def test_agent_initialization(self):
        """Test agent initialization."""
        agent = TestAgent()
        self.assertEqual(agent.name, "Test Agent")
        self.assertEqual(agent.agent_type, "test")
        self.assertEqual(agent.status, "initialized")

    def test_successful_run(self):
        """Test successful agent execution."""
        agent = TestAgent()
        result = agent.run(self.df)

        self.assertIsInstance(result, AgentResult)
        self.assertEqual(result.status, "completed")
        self.assertIsNone(result.error)
        self.assertTrue(result.is_successful())

    def test_failed_run(self):
        """Test failed agent execution."""
        agent = FailingAgent()
        result = agent.run(self.df)

        self.assertEqual(result.status, "failed")
        self.assertIsNotNone(result.error)
        self.assertIn("Intentional failure", result.error)
        self.assertFalse(result.is_successful())

    def test_empty_dataframe_validation(self):
        """Test validation with empty DataFrame."""
        agent = TestAgent()
        empty_df = pd.DataFrame()

        result = agent.run(empty_df)
        self.assertEqual(result.status, "failed")
        self.assertIn("EmptyDataFrameError", result.error)

    def test_missing_columns_validation(self):
        """Test validation with missing columns."""
        agent = TestAgent()
        incomplete_df = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=10),
            'Open': np.random.uniform(100, 110, 10)
            # Missing High, Low, Close
        })

        result = agent.run(incomplete_df)
        self.assertEqual(result.status, "failed")
        self.assertIn("MissingColumnsError", result.error)

    def test_insufficient_data_validation(self):
        """Test validation with insufficient data."""
        agent = TestAgent(min_rows=100)
        small_df = self.df.head(50)  # Only 50 rows

        result = agent.run(small_df)
        self.assertEqual(result.status, "failed")
        self.assertIn("InsufficientDataError", result.error)

    def test_get_latest_signal(self):
        """Test getting latest signal."""
        agent = TestAgent()
        agent.run(self.df)

        signal = agent.get_latest_signal()
        self.assertEqual(signal, "NEUTRAL")

    def test_get_status(self):
        """Test getting agent status."""
        agent = TestAgent()
        self.assertEqual(agent.get_status(), "initialized")

        agent.run(self.df)
        self.assertEqual(agent.get_status(), "completed")

    def test_repr(self):
        """Test string representation."""
        agent = TestAgent()
        repr_str = repr(agent)

        self.assertIn("Test Agent", repr_str)
        self.assertIn("test", repr_str)
        self.assertIn("initialized", repr_str)


if __name__ == '__main__':
    unittest.main()
