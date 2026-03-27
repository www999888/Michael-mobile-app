"""
Web UI - Streamlit 界面
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from config import STOCK_POOLS, logger
from data import StockDataFetcher
from analyzer import TechAnalyzer, AIAnalyzer
from trader import SimTrader
from monitor import StockMonitor

# 初始化组件
@st.cache_resource
def init_components():
    return {
        "fetcher": StockDataFetcher(),
        "tech_analyzer": TechAnalyzer(),
        "ai_analyzer": AIAnalyzer(),
        "trader": SimTrader()
    }

st.set_page_config(
    page_title="AI Stock Monitor - AI 股票盯盘分析",
    page_icon="📈",
    layout="wide"
)

st.title("📈 AI Stock Monitor - AI 股票盯盘分析系统")
st.markdown("本地私有化 AI 股票分析工具 · 实时盯盘 · 技术分析 · AI 决策")

# 初始化组件
components = init_components()
fetcher = components["fetcher"]
tech_analyzer = components["tech_analyzer"]
ai_analyzer = components["ai_analyzer"]
trader = components["trader"]

# 侧边栏
st.sidebar.header("⚙️ 设置")
selected_pool = st.sidebar.selectbox("股票池", ["沪深 A 股", "自选股票"])
selected_model = st.sidebar.selectbox("AI 模型", ["qwen3.5:35b", "glm-4.7-flash", "llama4"])
ai_analyzer.model = selected_model

# 主界面
tabs = st.tabs(["📊 行情监控", "🤖 AI 分析", "💼 模拟交易", "📈 技术分析"])

# Tab 1: 行情监控
with tabs[0]:
    st.header("📊 实时行情")
    
    # 获取实时数据
    stock_list = STOCK_POOLS.get(selected_pool, [])
    cols = st.columns(min(4, len(stock_list)))
    
    for i, stock_code in enumerate(stock_list):
        with cols[i % 4]:
            data = fetcher.get_realtime_quote(stock_code)
            if data:
                color = "🟢" if data["change_pct"] >= 0 else "🔴"
                st.metric(
                    label=stock_code,
                    value=f"{data['price']:.2f}元",
                    delta=f"{data['change_pct']:+.2f}%"
                )
                if st.button(f"分析 {stock_code}", key=f"analyze_{stock_code}"):
                    st.session_state.selected_stock = stock_code

# Tab 2: AI 分析
with tabs[1]:
    st.header("🤖 AI 智能分析")
    
    if "selected_stock" in st.session_state:
        stock_code = st.session_state.selected_stock
        
        # 获取历史数据
        df = fetcher.get_history_data(stock_code)
        st.write(f"### {stock_code} 最新数据")
        
        # AI 分析
        if st.button("开始 AI 分析"):
            with st.spinner("AI 正在分析中..."):
                analysis = tech_analyzer.analyze_stock(stock_code, df)
                ai_result = ai_analyzer.analyze_stock(stock_code, analysis)
                
                st.success("✅ AI 分析完成！")
                st.markdown(f"**AI 建议**: {ai_result['recommendation']}")
                st.markdown(f"**置信度**: {ai_result['confidence']:.2f}")
                st.markdown("---")
                st.markdown(ai_result["ai_analysis"])
    else:
        st.write("请从行情监控页面选择要分析的股票")

# Tab 3: 模拟交易
with tabs[2]:
    st.header("💼 模拟交易")
    
    cols1, cols2 = st.columns(2)
    
    with cols1:
        st.subheader("📊 账户概览")
        portfolio = trader.get_portfolio_value({})
        st.metric("总资金", f"{portfolio['total_value']:,.2f}元")
        st.metric("可用资金", f"{portfolio['cash']:,.2f}元")
        st.metric("总盈亏", f"{portfolio['total_profit']:+.2f}元")
        st.metric("收益率", f"{portfolio['profit_pct']:.2f}%")
    
    with cols2:
        st.subheader("📋 交易记录")
        trades = trader.get_trade_report()
        if trades:
            trade_df = pd.DataFrame(trades)
            st.dataframe(trade_df.tail(10))
        else:
            st.write("暂无交易记录")

# Tab 4: 技术分析
with tabs[3]:
    st.header("📈 技术分析")
    
    stock_code = st.text_input("股票代码", "000001.SZ")
    
    if st.button("分析"):
        df = fetcher.get_history_data(stock_code)
        analysis = tech_analyzer.analyze_stock(stock_code, df)
        
        if "error" not in analysis:
            st.json(analysis)
            
            # 显示交易信号
            signals = TechAnalyzer.get_trade_signals(analysis)
            st.markdown(f"**交易信号**: {signals['overall_signal']}")
            
            # 技术指标图表
            if "latest" in analysis:
                latest = analysis["latest"]
                if latest.get("MACD"):
                    st.write("### MACD")
                    st.line_chart(latest["MACD"])
                if latest.get("KDJ"):
                    st.write("### KDJ")
                    st.line_chart(latest["KDJ"])

# 页脚
st.sidebar.markdown("""
---
**AI Stock Monitor**
- 本地运行
- 无云端依赖
- 实时分析
""")
