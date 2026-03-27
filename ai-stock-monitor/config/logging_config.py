# 日志配置
"""
日志系统配置
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from .settings import LOGGING

def setup_logging():
    """初始化日志系统"""
    log_dir = LOGGING["log_dir"]
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # 文件处理器（轮转）
    file_handler = RotatingFileHandler(
        str(log_dir / "ai_stock_monitor.log"),
        maxBytes=LOGGING["max_bytes"],
        backupCount=LOGGING["backup_count"]
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # 错误文件处理器
    error_handler = RotatingFileHandler(
        str(log_dir / "errors.log"),
        maxBytes=LOGGING["max_bytes"],
        backupCount=LOGGING["backup_count"]
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    
    # 根日志器
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    
    return logger

# 获取日志器
logger = setup_logging()
