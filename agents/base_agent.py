"""
Base Agent class for technical indicator analysis
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import pandas as pd
from datetime import datetime


class BaseAgent(ABC):
    """
    Abstract base class for technical indicator agents.
    Each agent is responsible for calculating a specific technical indicator.
    """

    def __init__(self, name: str):
        self.name = name
        self.status = "initialized"
        self.result = None
        self.error = None

    @abstractmethod
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate the technical indicator on the provided dataframe.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with calculated indicator columns added
        """
        pass

    def run(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Execute the agent's calculation and return results.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            Dictionary containing agent status, results, and metadata
        """
        try:
            self.status = "running"
            print(f"[{self.name}] Starting calculation...")

            result_df = self.calculate(df.copy())

            self.status = "completed"
            self.result = result_df

            print(f"[{self.name}] Calculation completed successfully")

            return {
                "agent": self.name,
                "status": self.status,
                "data": result_df,
                "summary": self.get_summary(result_df),
                "error": None
            }

        except Exception as e:
            self.status = "failed"
            self.error = str(e)
            print(f"[{self.name}] Error: {e}")

            return {
                "agent": self.name,
                "status": self.status,
                "data": None,
                "summary": None,
                "error": str(e)
            }

    @abstractmethod
    def get_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate a summary of the indicator results.

        Args:
            df: DataFrame with calculated indicators

        Returns:
            Dictionary with summary statistics and insights
        """
        pass

    def get_latest_signal(self, df: pd.DataFrame) -> str:
        """
        Get the latest trading signal based on the indicator.

        Args:
            df: DataFrame with calculated indicators

        Returns:
            String indicating "BUY", "SELL", or "NEUTRAL"
        """
        return "NEUTRAL"
