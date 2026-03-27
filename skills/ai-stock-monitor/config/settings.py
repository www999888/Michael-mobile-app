"""
AI Stock Monitor - 股票监控分析系统
"""
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# ==================== 股票池配置 ====================
STOCK_POOL = {
    "A 股": ["000001.SZ", "600000.SH", "600030.SH", "000858.SZ"],  # 平安银行、浦发银行、中信证券、五粮液
    "ETF": ["510300.SH", "510500.SH"],  # 沪深 300ETF、中证 500ETF
    "自选": []  # 用户自定义
}

# 默认监控股票池
DEFAULT_STOCKS = [
    "000001.SZ", "600000.SH", "600030.SH", "000858.SZ",
    "601318.SH", "600519.SH", "000651.SZ", "600276.SH"
]

# ==================== Tushare 配置 ====================
TUSHARE_TOKEN = ""  # 从 https://tushare.pro 获取免费 token

# ==================== Ollama 配置 ====================
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2"  # 或 qwen2.5, mistral, gemma 等

# 支持的系统架构
SUPPORTED_ARCHITECTURES = {
    "llama3.2": "8B 参数，性能优秀",
    "qwen2.5": "7B 参数，中文优化",
    "mistral": "7B 参数，推理快速",
    "gemma": "2B/7B，轻量级",
    "phi3": "3.8B，微软出品"
}

# ==================== 技术分析参数 ====================
TECH_ANALYSIS_PARAMS = {
    "MA": {"short_period": 5, "medium_period": 10, "long_period": 20},
    "MACD": {"fast_period": 12, "slow_period": 26, "signal_period": 9},
    "KDJ": {"n_period": 9, "m1_period": 3, "m2_period": 3},
    "RSI": {"short_period": 6, "long_period": 12},
    "BOLL": {"period": 20, "mult": 2.0}
}

# ==================== 告警阈值 ====================
ALERT_THRESHOLDS = {
    "price_change_percent": 5.0,  # 涨跌幅超过 5% 触发告警
    "volume_increase": 2.0,       # 成交量放大 2 倍触发告警
    "min_price": 1.0,             # 最低价格阈值
    "max_price": None             # 最高价格阈值（无限制）
}

# ==================== 模拟交易配置 ====================
SIM_TRADING = {
    "initial_capital": 1000000,  # 初始资金 100 万
    "min_shares": 100,           # 最小交易单位 100 股
    "commission_rate": 0.0003,   # 佣金费率 0.03%
    "stamp_rate": 0.001,         # 印花税 0.1%
    "max_position_ratio": 0.8    # 最大仓位占比 80%
}

# ==================== UI 配置 ====================
STREAMLIT = {
    "theme": "dark",
    "layout": "wide",
    "refresh_interval": 60  # 刷新间隔（秒）
}

# ==================== 路径配置 ====================
DATA_DIR = BASE_DIR / "data_storage"
LOGS_DIR = BASE_DIR / "logs"
CACHE_DIR = DATA_DIR / "cache"

# ==================== 功能开关 ====================
FEATURES = {
    "realtime_monitor": True,   # 实时盯盘
    "ai_analysis": True,        # AI 分析
    "sim_trading": True,        # 模拟交易
    "alerts": True,             # 告警通知
    "auto_trade": False         # 自动交易（危险！建议先用模拟）
}

# ==================== 日志配置 ====================
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ==================== 其他配置 ====================
CACHE_EXPIRY_SECONDS = 300  # 数据缓存有效期
MAX_RETRY_TIMES = 3         # API 重试次数
TIMEOUT_SECONDS = 10        # API 请求超时
