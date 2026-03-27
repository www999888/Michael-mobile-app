# config/__init__.py
from .settings import *
from .logging_config import logger

__all__ = [
    "STOCK_POOLS",
    "SUPPORTED_MARKETS",
    "OLLAMA_BASE_URL",
    "DEFAULT_MODEL",
    "AVAILABLE_MODELS",
    "TECH_INDICATOR_PARAMS",
    "ALERT_THRESHOLD",
    "SIM_TRADING",
    "MONITORING",
    "LOGGING",
    "logger"
]
