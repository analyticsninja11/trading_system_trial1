"""
Unified Agent base class for technical indicator analysis.
Combines functionality from BaseAgent and SubAgent into a single consistent interface.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import pandas as pd
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from exceptions import (
    EmptyDataFrameError,
    MissingColumnsError,
    InsufficientDataError
)


class AgentResult:
    """
    Standardized result container for all agent operations.
    Provides a consistent interface for both simple and complex agent outputs.
    """

    def __init__(
        self,
        agent_name: str,
        status: str,
        data: Optional[pd.DataFrame] = None,
        output: Optional[Dict[str, Any]] = None,
        summary: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ):
        """
        Initialize agent result.

        Args:
            agent_name: Name of the agent that produced this result
            status: Status of the execution ("completed", "failed", "running")
            data: DataFrame with calculated indicators (for full analysis agents)
            output: Dictionary with processed output (for sub-agents)
            summary: Summary statistics and insights
            error: Error message if status is "failed"
        """
        self.agent_name = agent_name
        self.status = status
        self.data = data
        self.output = output
        self.summary = summary
        self.error = error
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary format for backward compatibility."""
        return {
            "agent": self.agent_name,
            "status": self.status,
            "data": self.data,
            "output": self.output,
            "summary": self.summary,
            "error": self.error,
            "timestamp": self.timestamp.isoformat()
        }

    def is_successful(self) -> bool:
        """Check if the agent execution was successful."""
        return self.status == "completed" and self.error is None

    def get_signal(self) -> Optional[str]:
        """Extract trading signal if available in output or summary."""
        if self.output and "signal" in self.output:
            return self.output["signal"]
        if self.summary and "signal" in self.summary:
            return self.summary["signal"]
        return None


class UnifiedAgent(ABC):
    """
    Unified abstract base class for all technical indicator agents.

    This class provides a consistent interface for both traditional indicator agents
    and ADK-compatible sub-agents, eliminating the need for separate BaseAgent and SubAgent classes.
    """

    def __init__(self, name: str, agent_type: str = "indicator"):
        """
        Initialize the unified agent.

        Args:
            name: Human-readable name of the agent
            agent_type: Type of agent ("indicator", "sub-agent", "orchestrator")
        """
        self.name = name
        self.agent_type = agent_type
        self.status = "initialized"
        self.last_result: Optional[AgentResult] = None

    @abstractmethod
    def process(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Process the data and return results.

        This is the core method that must be implemented by all agents.
        For indicator agents, this calculates indicators and returns both data and summary.
        For sub-agents, this returns processed output.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            Dictionary with keys:
                - data (optional): DataFrame with calculated indicators
                - output (optional): Processed results dictionary
                - summary (optional): Summary statistics
                - signal (optional): Trading signal ("BUY", "SELL", "NEUTRAL")
        """
        pass

    def run(self, df: pd.DataFrame) -> AgentResult:
        """
        Execute the agent's processing with error handling and status management.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            AgentResult object containing execution status and results
        """
        try:
            self.status = "running"
            self._log(f"Starting processing...")

            # Validate input
            self._validate_input(df)

            # Process data
            result_dict = self.process(df.copy())

            # Extract components from result
            data = result_dict.get("data")
            output = result_dict.get("output")
            summary = result_dict.get("summary")

            # If summary not provided but we have data, try to generate it
            if summary is None and data is not None:
                summary = self._generate_summary(data)

            self.status = "completed"
            self._log(f"Processing completed successfully")

            # Create result object
            result = AgentResult(
                agent_name=self.name,
                status="completed",
                data=data,
                output=output,
                summary=summary,
                error=None
            )

            self.last_result = result
            return result

        except Exception as e:
            self.status = "failed"
            error_msg = f"{type(e).__name__}: {str(e)}"
            self._log(f"Error: {error_msg}")

            result = AgentResult(
                agent_name=self.name,
                status="failed",
                data=None,
                output=None,
                summary=None,
                error=error_msg
            )

            self.last_result = result
            return result

    def _validate_input(self, df: pd.DataFrame) -> None:
        """
        Validate input DataFrame before processing.

        Args:
            df: DataFrame to validate

        Raises:
            EmptyDataFrameError: If DataFrame is empty or None
            MissingColumnsError: If required columns are missing
            InsufficientDataError: If insufficient data rows
        """
        if df is None or df.empty:
            raise EmptyDataFrameError(agent_name=self.name)

        # Check for required columns
        required_cols = ["Open", "High", "Low", "Close"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise MissingColumnsError(missing_columns=missing_cols, agent_name=self.name)

        # Check minimum data points
        min_rows = self.get_minimum_rows()
        if len(df) < min_rows:
            raise InsufficientDataError(required=min_rows, actual=len(df), agent_name=self.name)

    def get_minimum_rows(self) -> int:
        """
        Get minimum number of rows required for this agent to function.

        Returns:
            Minimum number of rows (default: 1)
        """
        return 1

    def _generate_summary(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """
        Generate a basic summary from the result DataFrame.
        Agents can override this for custom summaries.

        Args:
            df: DataFrame with calculated indicators

        Returns:
            Summary dictionary or None
        """
        return None

    def _log(self, message: str) -> None:
        """
        Log a message with agent name prefix.

        Args:
            message: Message to log
        """
        print(f"[{self.name}] {message}")

    def get_latest_signal(self) -> Optional[str]:
        """
        Get the latest trading signal from the last execution.

        Returns:
            Trading signal ("BUY", "SELL", "NEUTRAL") or None
        """
        if self.last_result:
            return self.last_result.get_signal()
        return None

    def get_status(self) -> str:
        """Get current agent status."""
        return self.status

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', type='{self.agent_type}', status='{self.status}')"
