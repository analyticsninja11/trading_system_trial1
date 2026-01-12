"""
Custom exceptions for the trading system.
Provides specific, meaningful error types for different failure scenarios.
"""
from typing import List, Optional


class TradingSystemException(Exception):
    """Base exception for all trading system errors."""
    pass


# Data validation exceptions
class DataValidationError(TradingSystemException):
    """Raised when data validation fails."""
    pass


class InsufficientDataError(DataValidationError):
    """Raised when there's not enough data for analysis."""

    def __init__(self, required: int, actual: int, agent_name: Optional[str] = None):
        self.required = required
        self.actual = actual
        self.agent_name = agent_name
        msg = f"Insufficient data: need at least {required} rows, got {actual}"
        if agent_name:
            msg = f"[{agent_name}] {msg}"
        super().__init__(msg)


class MissingColumnsError(DataValidationError):
    """Raised when required columns are missing from DataFrame."""

    def __init__(self, missing_columns: List[str], agent_name: Optional[str] = None):
        self.missing_columns = missing_columns
        self.agent_name = agent_name
        msg = f"Missing required columns: {', '.join(missing_columns)}"
        if agent_name:
            msg = f"[{agent_name}] {msg}"
        super().__init__(msg)


class InvalidDataFormatError(DataValidationError):
    """Raised when data format is invalid or unexpected."""
    pass


class EmptyDataFrameError(DataValidationError):
    """Raised when DataFrame is empty or None."""

    def __init__(self, agent_name: Optional[str] = None):
        msg = "DataFrame is empty or None"
        if agent_name:
            msg = f"[{agent_name}] {msg}"
        super().__init__(msg)


# Configuration exceptions
class ConfigurationError(TradingSystemException):
    """Raised when configuration is invalid."""
    pass


class InvalidParameterError(ConfigurationError):
    """Raised when a parameter value is invalid."""

    def __init__(self, parameter: str, value: any, reason: str):
        self.parameter = parameter
        self.value = value
        self.reason = reason
        msg = f"Invalid parameter '{parameter}' = {value}: {reason}"
        super().__init__(msg)


# Agent exceptions
class AgentError(TradingSystemException):
    """Base exception for agent-related errors."""

    def __init__(self, agent_name: str, message: str):
        self.agent_name = agent_name
        super().__init__(f"[{agent_name}] {message}")


class AgentInitializationError(AgentError):
    """Raised when agent initialization fails."""
    pass


class AgentExecutionError(AgentError):
    """Raised when agent execution fails."""
    pass


class IndicatorCalculationError(AgentError):
    """Raised when indicator calculation fails."""
    pass


# Orchestration exceptions
class OrchestrationError(TradingSystemException):
    """Raised when orchestration fails."""
    pass


class AgentTimeoutError(OrchestrationError):
    """Raised when an agent times out during execution."""

    def __init__(self, agent_name: str, timeout_seconds: int):
        self.agent_name = agent_name
        self.timeout_seconds = timeout_seconds
        msg = f"Agent '{agent_name}' timed out after {timeout_seconds} seconds"
        super().__init__(msg)


class ParallelExecutionError(OrchestrationError):
    """Raised when parallel execution encounters an error."""

    def __init__(self, failed_agents: List[str], message: str):
        self.failed_agents = failed_agents
        msg = f"Parallel execution failed for agents: {', '.join(failed_agents)}. {message}"
        super().__init__(msg)


# Data import exceptions
class DataImportError(TradingSystemException):
    """Raised when data import fails."""
    pass


class FileNotFoundError(DataImportError):
    """Raised when data file is not found."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        msg = f"Data file not found: {file_path}"
        super().__init__(msg)


class UnsupportedFileFormatError(DataImportError):
    """Raised when file format is not supported."""

    def __init__(self, file_path: str, supported_formats: List[str]):
        self.file_path = file_path
        self.supported_formats = supported_formats
        msg = f"Unsupported file format for '{file_path}'. Supported formats: {', '.join(supported_formats)}"
        super().__init__(msg)


class DateParsingError(DataImportError):
    """Raised when date parsing fails."""

    def __init__(self, date_string: str, expected_format: str):
        self.date_string = date_string
        self.expected_format = expected_format
        msg = f"Failed to parse date '{date_string}' with format '{expected_format}'"
        super().__init__(msg)


# Signal processing exceptions
class SignalError(TradingSystemException):
    """Raised when signal processing fails."""
    pass


class ConflictingSignalsError(SignalError):
    """Raised when agents produce conflicting signals that can't be resolved."""

    def __init__(self, signals: dict):
        self.signals = signals
        msg = f"Conflicting signals from agents: {signals}"
        super().__init__(msg)


class InsufficientSignalsError(SignalError):
    """Raised when not enough agents provide signals for consolidation."""

    def __init__(self, required: int, actual: int):
        self.required = required
        self.actual = actual
        msg = f"Insufficient signals for consolidation: need {required}, got {actual}"
        super().__init__(msg)
