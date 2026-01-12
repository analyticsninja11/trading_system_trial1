"""
Centralized configuration for the trading system.
All magic numbers and configurable parameters are defined here.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import os
import json


@dataclass
class MACDConfig:
    """Configuration for MACD (Moving Average Convergence Divergence) indicator."""
    fast_period: int = 12
    slow_period: int = 26
    signal_period: int = 9

    def validate(self) -> None:
        """Validate MACD configuration."""
        if self.fast_period >= self.slow_period:
            raise ValueError("MACD fast_period must be less than slow_period")
        if self.fast_period < 1 or self.slow_period < 1 or self.signal_period < 1:
            raise ValueError("MACD periods must be positive integers")


@dataclass
class RSIConfig:
    """Configuration for RSI (Relative Strength Index) indicator."""
    period: int = 14
    overbought_threshold: float = 70.0
    oversold_threshold: float = 30.0
    extreme_overbought: float = 90.0  # Used in ADK system
    extreme_oversold: float = 10.0

    def validate(self) -> None:
        """Validate RSI configuration."""
        if self.period < 1:
            raise ValueError("RSI period must be a positive integer")
        if not (0 <= self.oversold_threshold < self.overbought_threshold <= 100):
            raise ValueError("RSI thresholds must satisfy: 0 <= oversold < overbought <= 100")
        if not (0 <= self.extreme_oversold <= 100):
            raise ValueError("RSI extreme_oversold must be between 0 and 100")
        if not (0 <= self.extreme_overbought <= 100):
            raise ValueError("RSI extreme_overbought must be between 0 and 100")


@dataclass
class SMAConfig:
    """Configuration for SMA (Simple Moving Average) indicator."""
    short_period: int = 20
    long_period: int = 50

    def validate(self) -> None:
        """Validate SMA configuration."""
        if self.short_period >= self.long_period:
            raise ValueError("SMA short_period must be less than long_period")
        if self.short_period < 1 or self.long_period < 1:
            raise ValueError("SMA periods must be positive integers")


@dataclass
class SMADeltaConfig:
    """Configuration for SMA Delta (monthly change analysis)."""
    short_lookback_months: int = 6
    long_lookback_months: int = 12

    def validate(self) -> None:
        """Validate SMA Delta configuration."""
        if self.short_lookback_months < 1 or self.long_lookback_months < 1:
            raise ValueError("SMA Delta lookback periods must be positive integers")
        if self.short_lookback_months >= self.long_lookback_months:
            raise ValueError("SMA Delta short_lookback must be less than long_lookback")


@dataclass
class SupertrendConfig:
    """Configuration for Supertrend indicator."""
    atr_length: int = 10
    atr_multiplier: float = 3.0

    def validate(self) -> None:
        """Validate Supertrend configuration."""
        if self.atr_length < 1:
            raise ValueError("Supertrend ATR length must be a positive integer")
        if self.atr_multiplier <= 0:
            raise ValueError("Supertrend ATR multiplier must be positive")


@dataclass
class OrchestratorConfig:
    """Configuration for agent orchestration and signal consolidation."""
    # Signal consolidation
    min_buy_conditions: int = 2  # Out of 4 conditions in ADK system
    min_sell_conditions: int = 2
    use_weighted_voting: bool = False  # Future enhancement

    # Agent weights (for weighted voting)
    agent_weights: Dict[str, float] = field(default_factory=lambda: {
        "MACD": 1.0,
        "RSI": 1.0,
        "SMA": 1.0,
        "Supertrend": 1.0
    })

    # Execution
    default_execution_mode: str = "parallel"  # "parallel" or "sequential"
    max_workers: int = 4  # For parallel execution
    execution_timeout_seconds: int = 60

    def validate(self) -> None:
        """Validate Orchestrator configuration."""
        if self.min_buy_conditions < 0 or self.min_sell_conditions < 0:
            raise ValueError("Minimum conditions must be non-negative")
        if self.default_execution_mode not in ["parallel", "sequential"]:
            raise ValueError("Execution mode must be 'parallel' or 'sequential'")
        if self.max_workers < 1:
            raise ValueError("max_workers must be at least 1")
        if self.execution_timeout_seconds < 1:
            raise ValueError("execution_timeout_seconds must be positive")
        for agent, weight in self.agent_weights.items():
            if weight < 0:
                raise ValueError(f"Agent weight for {agent} must be non-negative")


@dataclass
class DataConfig:
    """Configuration for data handling and validation."""
    # Date format
    date_format: str = "%d/%m/%Y"  # UK format for user input
    internal_date_format: str = "%Y-%m-%d"  # ISO format for internal use

    # Data validation
    min_data_points: int = 50  # Minimum rows for meaningful analysis
    required_columns: list = field(default_factory=lambda: ["Open", "High", "Low", "Close"])
    optional_columns: list = field(default_factory=lambda: ["Volume"])

    # Data paths
    data_directory: str = "data"
    output_directory: str = "output"

    def validate(self) -> None:
        """Validate Data configuration."""
        if self.min_data_points < 1:
            raise ValueError("min_data_points must be at least 1")
        if not self.required_columns:
            raise ValueError("required_columns cannot be empty")


@dataclass
class LoggingConfig:
    """Configuration for logging."""
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_to_file: bool = False
    log_file_path: str = "logs/trading_system.log"

    def validate(self) -> None:
        """Validate Logging configuration."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level.upper() not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")


@dataclass
class TradingSystemConfig:
    """
    Master configuration for the entire trading system.
    Aggregates all sub-configurations.
    """
    macd: MACDConfig = field(default_factory=MACDConfig)
    rsi: RSIConfig = field(default_factory=RSIConfig)
    sma: SMAConfig = field(default_factory=SMAConfig)
    sma_delta: SMADeltaConfig = field(default_factory=SMADeltaConfig)
    supertrend: SupertrendConfig = field(default_factory=SupertrendConfig)
    orchestrator: OrchestratorConfig = field(default_factory=OrchestratorConfig)
    data: DataConfig = field(default_factory=DataConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    def validate(self) -> None:
        """Validate all sub-configurations."""
        self.macd.validate()
        self.rsi.validate()
        self.sma.validate()
        self.sma_delta.validate()
        self.supertrend.validate()
        self.orchestrator.validate()
        self.data.validate()
        self.logging.validate()

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "TradingSystemConfig":
        """
        Create configuration from dictionary.

        Args:
            config_dict: Dictionary with configuration values

        Returns:
            TradingSystemConfig instance
        """
        return cls(
            macd=MACDConfig(**config_dict.get("macd", {})),
            rsi=RSIConfig(**config_dict.get("rsi", {})),
            sma=SMAConfig(**config_dict.get("sma", {})),
            sma_delta=SMADeltaConfig(**config_dict.get("sma_delta", {})),
            supertrend=SupertrendConfig(**config_dict.get("supertrend", {})),
            orchestrator=OrchestratorConfig(**config_dict.get("orchestrator", {})),
            data=DataConfig(**config_dict.get("data", {})),
            logging=LoggingConfig(**config_dict.get("logging", {}))
        )

    @classmethod
    def from_json_file(cls, file_path: str) -> "TradingSystemConfig":
        """
        Load configuration from JSON file.

        Args:
            file_path: Path to JSON configuration file

        Returns:
            TradingSystemConfig instance
        """
        with open(file_path, 'r') as f:
            config_dict = json.load(f)
        return cls.from_dict(config_dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "macd": {
                "fast_period": self.macd.fast_period,
                "slow_period": self.macd.slow_period,
                "signal_period": self.macd.signal_period
            },
            "rsi": {
                "period": self.rsi.period,
                "overbought_threshold": self.rsi.overbought_threshold,
                "oversold_threshold": self.rsi.oversold_threshold,
                "extreme_overbought": self.rsi.extreme_overbought,
                "extreme_oversold": self.rsi.extreme_oversold
            },
            "sma": {
                "short_period": self.sma.short_period,
                "long_period": self.sma.long_period
            },
            "sma_delta": {
                "short_lookback_months": self.sma_delta.short_lookback_months,
                "long_lookback_months": self.sma_delta.long_lookback_months
            },
            "supertrend": {
                "atr_length": self.supertrend.atr_length,
                "atr_multiplier": self.supertrend.atr_multiplier
            },
            "orchestrator": {
                "min_buy_conditions": self.orchestrator.min_buy_conditions,
                "min_sell_conditions": self.orchestrator.min_sell_conditions,
                "use_weighted_voting": self.orchestrator.use_weighted_voting,
                "agent_weights": self.orchestrator.agent_weights,
                "default_execution_mode": self.orchestrator.default_execution_mode,
                "max_workers": self.orchestrator.max_workers,
                "execution_timeout_seconds": self.orchestrator.execution_timeout_seconds
            },
            "data": {
                "date_format": self.data.date_format,
                "internal_date_format": self.data.internal_date_format,
                "min_data_points": self.data.min_data_points,
                "required_columns": self.data.required_columns,
                "optional_columns": self.data.optional_columns,
                "data_directory": self.data.data_directory,
                "output_directory": self.data.output_directory
            },
            "logging": {
                "log_level": self.logging.log_level,
                "log_format": self.logging.log_format,
                "log_to_file": self.logging.log_to_file,
                "log_file_path": self.logging.log_file_path
            }
        }

    def to_json_file(self, file_path: str) -> None:
        """
        Save configuration to JSON file.

        Args:
            file_path: Path to save JSON configuration
        """
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def from_env(cls) -> "TradingSystemConfig":
        """
        Create configuration from environment variables.
        Environment variables should be prefixed with TRADING_

        Returns:
            TradingSystemConfig instance
        """
        config = cls()

        # MACD
        if os.getenv("TRADING_MACD_FAST_PERIOD"):
            config.macd.fast_period = int(os.getenv("TRADING_MACD_FAST_PERIOD"))
        if os.getenv("TRADING_MACD_SLOW_PERIOD"):
            config.macd.slow_period = int(os.getenv("TRADING_MACD_SLOW_PERIOD"))
        if os.getenv("TRADING_MACD_SIGNAL_PERIOD"):
            config.macd.signal_period = int(os.getenv("TRADING_MACD_SIGNAL_PERIOD"))

        # RSI
        if os.getenv("TRADING_RSI_PERIOD"):
            config.rsi.period = int(os.getenv("TRADING_RSI_PERIOD"))
        if os.getenv("TRADING_RSI_OVERBOUGHT"):
            config.rsi.overbought_threshold = float(os.getenv("TRADING_RSI_OVERBOUGHT"))
        if os.getenv("TRADING_RSI_OVERSOLD"):
            config.rsi.oversold_threshold = float(os.getenv("TRADING_RSI_OVERSOLD"))

        # Add more env var mappings as needed...

        return config


# Global default configuration instance
DEFAULT_CONFIG = TradingSystemConfig()

# Validate default configuration on module load
DEFAULT_CONFIG.validate()


def get_config() -> TradingSystemConfig:
    """
    Get the global configuration instance.
    Can be overridden by loading from file or environment.

    Returns:
        TradingSystemConfig instance
    """
    return DEFAULT_CONFIG


def load_config(config_path: Optional[str] = None) -> TradingSystemConfig:
    """
    Load configuration from file or environment.

    Args:
        config_path: Optional path to JSON config file

    Returns:
        TradingSystemConfig instance
    """
    if config_path and os.path.exists(config_path):
        config = TradingSystemConfig.from_json_file(config_path)
    else:
        # Try loading from environment
        config = TradingSystemConfig.from_env()

    config.validate()
    return config
