"""
Sub Agent base class for Google ADK compatibility
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
import pandas as pd


class SubAgent(ABC):
    """
    Base class for sub-agents that process specific indicators.
    Compatible with Google's Agent Development Kit (ADK).
    """

    def __init__(self, name: str):
        self.name = name
        self.status = "initialized"

    @abstractmethod
    def process(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Process the data and return indicator output.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            Dictionary with indicator results
        """
        pass

    def run(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Execute the sub-agent's processing.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            Dictionary containing agent status and results
        """
        try:
            self.status = "running"
            print(f"[{self.name}] Processing...")

            result = self.process(df.copy())

            self.status = "completed"
            print(f"[{self.name}] Completed")

            return {
                "agent": self.name,
                "status": "completed",
                "output": result,
                "error": None
            }

        except Exception as e:
            self.status = "failed"
            print(f"[{self.name}] Error: {e}")

            return {
                "agent": self.name,
                "status": "failed",
                "output": None,
                "error": str(e)
            }
