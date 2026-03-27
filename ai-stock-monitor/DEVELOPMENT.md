# AI Stock Monitor - 开发文档

## 📚 目录

1. [项目概述](#项目概述)
2. [技术架构](#技术架构)
3. [模块详解](#模块详解)
4. [配置说明](#配置说明)
5. [API 文档](#api-文档)
6. [扩展开发](#扩展开发)
7. [部署指南](#部署指南)

## 项目概述

### 核心功能

1. **实时盯盘**
   - 实时获取股票价格、涨跌幅、成交量
   - 支持沪深 A 股市场
   - 自定义监控股票池

2. **技术分析**
   - MA（移动平均线）
   - MACD（指数平滑异同移动平均线）
   - KDJ（随机指标）
   - RSI（相对强弱指标）
   - BOLL（布林带）

3. **AI 智能分析**
   - 本地 Ollama 大模型分析
   - 生成交易建议
   - 置信度评估

4. **模拟交易**
   - 模拟买入/卖出
   - 持仓管理
   - 盈亏统计

5. **告警系统**
   - 价格涨跌幅告警
   - 技术指标告警
   - 桌面通知

### 技术栈

- **语言**: Python 3.9+
- **数据源**: 东方财富接口 / Tushare
- **AI 引擎**: Ollama + 本地大模型
- **前端**: Streamlit
- **数据处理**: Pandas + NumPy
- **部署**: PyInstaller

## 技术架构

```
┌─────────────────────────────────────────────┐
│              Web UI (Streamlit)              │
│              http://localhost:8501           │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│             Analyzer Module                  │
│  ┌──────────────┬────────────────────┐      │
│  │ TechAnalyzer │    AIAnalyzer      │      │
│  │ (技术指标)   │  (AI 分析决策)     │      │
│  └──────────────┴────────────────────┘      │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│              Data Module                     │
│  ┌──────────────┬────────────────────┐      │
│  │ DataFetcher  │   DataStorage      │      │
│  │ (数据获取)   │  (数据存储缓存)    │      │
│  └──────────────┴────────────────────┘      │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│            Monitor Module                    │
│            StockMonitor                      │
│           (实时盯盘告警)                     │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│             Trader Module                    │
│            SimTrader                         │
│          (模拟交易)                          │
└─────────────────────────────────────────────┘
```

## 模块详解

### 1. 配置模块 (config/)

#### `settings.py`

核心配置文件，定义：

- **股票池配置**: 监控的股票列表
- **接口配置**: Ollama 地址、API Key
- **技术指标参数**: MA、MACD 等参数
- **告警阈值**: 价格变化、RSI 等阈值
- **模拟交易参数**: 初始资金、止损止盈比例

示例配置：

```python
STOCK_POOLS = {
    "沪深 A 股": ["000001.SZ", "600000.SH"],
}

TECH_INDICATOR_PARAMS = {
    "MA": {"periods": [5, 10, 20, 60]},
    "MACD": {"fast": 12, "slow": 26, "signal": 9},
}

ALERT_THRESHOLD = {
    "price_change_pct": 5.0,
    "rsi_overbought": 70,
}
```

#### `logging_config.py`

日志系统配置，使用 RotatingFileHandler 实现日志轮转。

### 2. 数据模块 (data/)

#### `data_fetcher.py` - StockDataFetcher

负责获取股票数据：

**核心方法**:

- `get_realtime_quote(stock_code)`: 获取实时行情
- `get_history_data(stock_code, days)`: 获取历史 K 线数据
- `get_all_stock_codes()`: 获取股票列表

数据格式：

```python
{
    "code": "000001.SZ",
    "price": 12.5,
    "change_pct": 2.5,
    "volume": 1000000,
    "timestamp": 1711234567
}
```

历史数据返回 Pandas DataFrame：

```
            open     high      low    close    volume
date                                                   
2024-03-20  12.3   12.8      12.2     12.5   1200000
```

#### `data_storage.py` - StockDataStorage

数据缓存和持久化：

**核心方法**:

- `cache_realtime_quote()`: 缓存实时数据
- `save_history_data()`: 保存历史数据
- `load_history_data()`: 加载历史数据
- `get_trade_history()`: 获取交易记录

### 3. 分析模块 (analyzer/)

#### `tech_analyzer.py` - TechAnalyzer

技术指标计算和分析：

**计算方法**:

```python
# 移动平均线
ma = TechAnalyzer.calculate_ma(df, periods=[5, 10, 20])

# MACD
macd = TechAnalyzer.calculate_macd(df, fast=12, slow=26, signal=9)

# KDJ
kdj = TechAnalyzer.calculate_kdj(df, period=9)

# RSI
rsi = TechAnalyzer.calculate_rsi(df, periods=[6, 12, 24])

# 布林带
boll = TechAnalyzer.calculate_boll(df, period=20, std_dev=2)
```

**综合分析和信号生成**:

```python
# 技术分析
analysis = TechAnalyzer.analyze_stock(stock_code, df)

# 生成交易信号
signals = TechAnalyzer.get_trade_signals(analysis)
# 返回：{"stock_code": "000001.SZ", "signals": [...], "overall_signal": "BUY"}
```

#### `ai_analyzer.py` - AIAnalyzer

AI 分析器，使用 Ollama 本地大模型：

**核心方法**:

- `analyze_stock(stock_code, analysis)`: AI 分析股票
- `_build_analysis_prompt()`: 构建分析提示词
- `_extract_recommendation()`: 提取交易建议
- `_calculate_confidence()`: 计算置信度

AI 分析返回：

```python
{
    "stock_code": "000001.SZ",
    "ai_analysis": "...",
    "recommendation": "BUY",
    "confidence": 0.75,
    "model": "qwen3.5:35b"
}
```

### 4. 盯盘模块 (monitor/)

#### `stock_monitor.py` - StockMonitor

实时监控和告警：

**核心方法**:

- `start_monitoring(stocks, interval)`: 启动监控
- `stop_monitoring()`: 停止监控
- `get_current_status()`: 获取当前状态

告警回调示例：

```python
def on_alert(alert):
    print(f"告警：{alert['message']}")

monitor = StockMonitor()
monitor.add_alert_callback(on_alert)
monitor.start_monitoring(stocks, interval=60)
```

### 5. 交易模块 (trader/)

#### `sim_trader.py` - SimTrader

模拟交易管理：

**核心方法**:

- `buy(stock_code, price, shares)`: 买入
- `sell(stock_code, price, shares)`: 卖出
- `get_positions()`: 获取持仓
- `get_portfolio_value(stock_prices)`: 获取组合价值
- `get_performance_summary()`: 获取业绩报告

交易结果示例：

```python
{
    "success": True,
    "trade": {
        "type": "BUY",
        "stock_code": "000001.SZ",
        "shares": 100,
        "price": 12.5,
        "total_cost": 1250
    },
    "remaining_capital": 98750
}
```

## API 文档

### StockDataFetcher

```python
fetcher = StockDataFetcher()

# 获取实时行情
quote = fetcher.get_realtime_quote("000001.SZ")

# 获取历史数据
df = fetcher.get_history_data("000001.SZ", days=60)
```

### TechAnalyzer

```python
analyzer = TechAnalyzer()

# 技术分析
analysis = analyzer.analyze_stock("000001.SZ", df)

# 生成信号
signals = analyzer.get_trade_signals(analysis)
```

### AIAnalyzer

```python
ai = AIAnalyzer(model="qwen3.5:35b")

# AI 分析
result = ai.analyze_stock("000001.SZ", analysis)
```

### SimTrader

```python
trader = SimTrader(initial_capital=1000000)

# 买入
trader.buy("000001.SZ", 12.5, 100)

# 卖出
trader.sell("000001.SZ", 13.0, 50)

# 获取持仓
positions = trader.get_positions()

# 获取业绩
summary = trader.get_performance_summary()
```

### StockMonitor

```python
monitor = StockMonitor()

# 添加告警回调
monitor.add_alert_callback(my_callback)

# 启动监控
monitor.start_monitoring(["000001.SZ", "600000.SH"], interval=30)
```

## 扩展开发

### 添加新的技术指标

在 `analyzer/tech_analyzer.py` 中添加新方法：

```python
@staticmethod
def calculate_new_indicator(df):
    # 计算逻辑
    return indicator_data
```

### 接入真实数据源

修改 `data/data_fetcher.py` 中的 `_get_mock_realtime()` 和 `_get_mock_history()`，替换为真实 API 调用：

```python
def get_realtime_quote(self, stock_code):
    import tushare as ts
    
    ts_api = ts.Token("your_api_key")
    data = ts_api.daily_pro(stock_code)
    return data
```

### 自定义 AI 提示词

修改 `analyzer/ai_analyzer.py` 中的 `_build_analysis_prompt()` 方法。

## 部署指南

### 本地开发环境

1. **安装 Python 3.9+**

2. **安装依赖**:
```bash
pip install -r requirements.txt
```

3. **配置 Ollama**:
```bash
ollama pull qwen3.5:35b
```

4. **启动应用**:
```bash
run.bat
# 或
streamlit run main.py
```

### Windows EXE 打包

1. **安装 PyInstaller**:
```bash
pip install pyinstaller
```

2. **运行打包脚本**:
```bash
build_exe.bat
```

3. **生成文件**:
- `dist\AI_Stock_Monitor.exe`

### Linux/Mac部署

1. **安装依赖**:
```bash
pip install -r requirements.txt
```

2. **启动**:
```bash
python main.py
```

### Docker 部署

创建 `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "main.py", "--server.port", "8501"]
```

构建和运行：

```bash
docker build -t ai-stock-monitor .
docker run -p 8501:8501 ai-stock-monitor
```

## 常见问题

### Q: Ollama 连接失败

A: 确保 Ollama 服务正在运行：
```bash
ollama serve
```

### Q: 数据获取失败

A: 检查网络连接，或使用模拟数据测试。

### Q: 指标计算不准确

A: 检查历史数据质量，确保数据完整。

## 开发计划

- [ ] 添加更多技术指标
- [ ] 支持更多市场（港股、美股）
- [ ] 集成真实交易接口
- [ ] 添加回测功能
- [ ] 移动端适配

---

**版本**: 1.0.0  
**更新日期**: 2024-03-25
