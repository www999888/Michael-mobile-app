# 全局配置文件
"""
AI Stock Monitor - 股票盯盘交易分析系统
本地私有化 AI 股票分析工具
"""

import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent.parent

# ==================== 股票池配置 ====================
STOCK_POOLS = {
    "沪深 A 股": ["000001.SZ", "600000.SH", "600519.SH", "000858.SZ", "300750.SZ"],
    "自选股票": [],  # 用户可自定义
    "全部股票": []    # 留空表示获取全部
}

# 支持的股票类型
SUPPORTED_MARKETS = ["SH", "SZ"]

# ==================== 接口配置 ====================
TUSHARE_API_KEY = os.getenv("TUSHARE_API_KEY", "")  # 可选：免费接口无需 API Key

# Ollama 配置
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "qwen3.5:35b"  # 推荐使用 qwen3.5:35b 或 glm-4.7-flash
AVAILABLE_MODELS = ["qwen3.5:35b", "glm-4.7-flash", "llama4"]

# ==================== 技术指标参数 ====================
TECH_INDICATOR_PARAMS = {
    "MA": {"periods": [5, 10, 20, 60]},
    "MACD": {"fast": 12, "slow": 26, "signal": 9},
    "KDJ": {"period": 9, "smooth": 3},
    "RSI": {"periods": [6, 12, 24]},
    "BOLL": {"period": 20, "std_dev": 2}
}

# ==================== 告警阈值 ====================
ALERT_THRESHOLD = {
    "price_change_pct": 5.0,      # 涨跌幅超过 5% 告警
    "volume_change_pct": 100.0,   # 成交量变化超过 100% 告警
    "rsi_overbought": 70,         # RSI 超买
    "rsi_oversold": 30,           # RSI 超卖
    "macd_cross": True            # 开启 MACD 金叉/死叉告警
}

# ==================== 模拟交易配置 ====================
SIM_TRADING = {
    "initial_capital": 1000000,   # 初始资金 100 万
    "min_shares": 100,            # 最小交易单位
    "max_position_pct": 0.8,      # 单只股票最大持仓比例
    "stop_loss_pct": 5.0,         # 止损比例
    "take_profit_pct": 10.0       # 止盈比例
}

# ==================== 监控配置 ====================
MONITORING = {
    "refresh_interval": 60,       # 刷新间隔（秒）
    "check_interval": 300,        # 技术分析间隔（秒）
    "alert_enabled": True,        # 是否开启告警
    "sound_alert": True,          # 声音告警
    "desktop_notification": True  # 桌面通知
}

# ==================== 日志配置 ====================
LOGGING = {
    "log_dir": BASE_DIR / "logs",
    "max_bytes": 10 * 1024 * 1024,  # 10MB
    "backup_count": 5,              # 保留 5 个备份文件
    "level": "INFO"
}

# ==================== 其他配置 ====================
DATA_CACHE_TTL = 300  # 数据缓存过期时间（秒）
STOCK_DATA_DIR = BASE_DIR / "data" / "stock_data"
HISTORY_DATA_DIR = BASE_DIR / "data" / "history"
