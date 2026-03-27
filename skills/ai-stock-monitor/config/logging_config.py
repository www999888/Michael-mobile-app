"""
AI Stock Monitor - 日志配置
"""
import logging
import logging.handlers
from pathlib import Path
from config.settings import LOGS_DIR, LOG_LEVEL, LOG_FORMAT

# 确保日志目录存在
LOGS_DIR.mkdir(exist_ok=True)

# ==================== 日志配置函数 ====================
def setup_logger(name: str, log_file: str = None, level: str = None):
    """
    创建并配置日志记录器
    
    Args:
        name: 日志名称
        log_file: 日志文件名（可选）
        level: 日志级别
    
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(level or LOG_LEVEL)
    
    # 格式化器
    formatter = logging.Formatter(LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器（如果指定了文件）
    if log_file:
        log_path = LOGS_DIR / log_file
        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

# ==================== 创建标准日志记录器 ====================
# 主日志
main_logger = setup_logger("ai_stock_monitor", "monitor.log", "INFO")

# 数据日志
data_logger = setup_logger("data", "data.log", "DEBUG")

# 分析日志
analyzer_logger = setup_logger("analyzer", "analysis.log", "INFO")

# 交易日志
trader_logger = setup_logger("trader", "trading.log", "INFO")

# UI 日志
ui_logger = setup_logger("ui", "ui.log", "INFO")

# 工具函数
def log_system_status():
    """记录系统状态信息"""
    import os
    import platform
    import time
    
    main_logger.info("=" * 50)
    main_logger.info("AI Stock Monitor 系统状态")
    main_logger.info("=" * 50)
    main_logger.info(f"操作系统：{platform.system()} {platform.release()}")
    main_logger.info(f"Python 版本：{platform.python_version()}")
    main_logger.info(f"进程 ID: {os.getpid()}")
    main_logger.info(f"当前时间：{time.strftime('%Y-%m-%d %H:%M:%S')}")
    main_logger.info(f"数据目录：{DATA_DIR}")
    main_logger.info(f"日志目录：{LOGS_DIR}")
    main_logger.info("=" * 50)
