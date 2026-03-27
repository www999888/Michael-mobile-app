"""
AI Stock Monitor - Web UI 界面
基于 Streamlit 的可视化界面
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from typing import Dict, List, Optional
from data.data_fetcher import TushareFetcher, MockDataGenerator
from data.data_storage import get_database
from analyzer.tech_analyzer import get_analyzer
from analyzer.ai_analyzer import get_ai_analyzer
from monitor.stock_monitor import get_monitor
from trader.sim_trader import get_trader
from config.settings import STOCK_POOL, DEFAULT_STOCKS, FEATURES, STREAMLIT

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="AI Stock Monitor",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== 侧边栏 ====================
st.sidebar.title("📊 AI Stock Monitor")
st.sidebar.markdown("---")

# 股票代码选择
selected_stock = st.sidebar.selectbox(
    "选择股票",
    DEFAULT_STOCKS,
    index=0
)

# 功能开关
st.sidebar.markdown("### 功能控制")
st.sidebar.checkbox("实时盯盘", value=FEATURES['realtime_monitor'], key='monitor')
st.sidebar.checkbox("AI 分析", value=FEATURES['ai_analysis'], key='ai')
st.sidebar.checkbox("模拟交易", value=FEATURES['sim_trading'], key='trading')
st.sidebar.checkbox("告警通知", value=FEATURES['alerts'], key='alerts')

# 监控按钮
if st.sidebar.button("▶️ 启动监控"):
    monitor = get_monitor()
    monitor.start_monitoring(interval=60)
    st.success("监控已启动！")

if st.sidebar.button("⏹️ 停止监控"):
    monitor = get_monitor()
    monitor.stop_monitoring()
    st.warning("监控已停止！")

st.sidebar.markdown("---")
st.sidebar.info("AI Stock Monitor v1.0")

# ==================== 页面内容 ====================
def render_home():
    """主页"""
    st.title("📈 AI Stock Monitor")
    st.markdown("""
    **本地 AI 股票盯盘分析系统**
    
    - ✅ 实时监控股票数据
    - ✅ 自动计算技术指标
    - ✅ Ollama 本地 AI 分析
    - ✅ 模拟交易和盈亏统计
    - ✅ 智能告警提醒
    
    请从左侧选择股票查看详细信息。
    """)

def render_stock_detail(ts_code: str):
    """股票详情页面"""
    st.title(f"📊 {ts_code}")
    
    # 获取数据
    df = MockDataGenerator.generate_mock_daily_data(ts_code, days=30)
    
    # 计算技术指标
    analyzer = get_analyzer()
    df_with_indicators = analyzer.calculate_all_indicators(df)
    
    # 获取交易信号
    signals = analyzer.get_signal(df_with_indicators, ts_code)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("当前价格", f"{df_with_indicators['close'].iloc[-1]:.2f}", "昨日")
    with col2:
        st.metric("涨跌幅", f"{df_with_indicators['pct_chg'].iloc[-1]:.2f}%", "较昨日")
    with col3:
        st.metric("成交量", f"{df_with_indicators['vol'].iloc[-1]:,.0f}")
    
    st.markdown("---")
    
    # 价格图表
    st.subheader("📈 价格走势")
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df_with_indicators.index,
        open=df_with_indicators['open'],
        high=df_with_indicators['high'],
        low=df_with_indicators['low'],
        close=df_with_indicators['close'],
        name='价格'
    ))
    fig.update_layout(
        height=400,
        xaxis_title='日期',
        yaxis_title='价格',
        template='plotly_dark',
        xaxis_rangeslider_visible=False
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 技术指标
    st.markdown("---")
    st.subheader("🔧 技术指标")
    
    tech_cols = st.columns(4)
    with tech_cols[0]:
        st.metric("MA 信号", signals.get('indicators', {}).get('ma_status', 'N/A'))
    with tech_cols[1]:
        st.metric("MACD 信号", signals.get('indicators', {}).get('macd_status', 'N/A'))
    with tech_cols[2]:
        st.metric("KDJ 状态", signals.get('indicators', {}).get('kdj_status', 'N/A'))
    with tech_cols[3]:
        st.metric("RSI 状态", signals.get('indicators', {}).get('rsi_status', 'N/A'))
    
    # 趋势图
    st.subheader("📊 指标趋势")
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=df_with_indicators.index,
        y=df_with_indicators['ma_short'],
        name='MA(5)',
        line=dict(color='blue')
    ))
    fig2.add_trace(go.Scatter(
        x=df_with_indicators.index,
        y=df_with_indicators['ma_medium'],
        name='MA(10)',
        line=dict(color='orange')
    ))
    fig2.add_trace(go.Scatter(
        x=df_with_indicators.index,
        y=df_with_indicators['ma_long'],
        name='MA(20)',
        line=dict(color='green')
    ))
    fig2.update_layout(
        height=300,
        xaxis_title='日期',
        yaxis_title='价格',
        template='plotly_dark'
    )
    st.plotly_chart(fig2, use_container_width=True)

def render_ai_analysis(ts_code: str):
    """AI 分析页面"""
    st.title(f"🤖 AI 分析 - {ts_code}")
    
    # 获取数据
    df = MockDataGenerator.generate_mock_daily_data(ts_code, days=30)
    analyzer = get_analyzer()
    df_with_indicators = analyzer.calculate_all_indicators(df)
    signals = analyzer.get_signal(df_with_indicators, ts_code)
    
    st.subheader("技术分析总结")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**综合信号:** {signals.get('overall_signal', 'N/A')}")
        st.metric("评分", f"{signals.get('score', 0)}", 
                 help="-10 到 10，负数偏空，正数偏多")
    with col2:
        st.warning(f"**置信度:** {abs(signals.get('score', 0)) / 10:.0%}")
        st.success(f"**数据来源:** {len(df_with_indicators)} 天")
    
    st.markdown("---")
    
    st.subheader("📝 AI 分析详情")
    
    if FEATURES['ai_analysis']:
        ai_analyzer = get_ai_analyzer()
        with st.spinner("正在调用本地 AI..."):
            ai_result = ai_analyzer.analyze(ts_code, df_with_indicators, signals)
        
        if ai_result and 'raw_analysis' in ai_result:
            st.markdown(ai_result['raw_analysis'])
        else:
            st.error(f"AI 分析失败：{ai_result.get('error', '未知错误')}")
    else:
        st.info("AI 分析功能已关闭")
    
    # 交易信号列表
    st.markdown("---")
    st.subheader("🎯 关键信号")
    
    if signals.get('signals'):
        for signal in signals['signals']:
            st.markdown(f"• {signal}")
    else:
        st.info("暂无明显信号")

def render_trading(ts_code: str):
    """模拟交易页面"""
    st.title(f"💼 模拟交易 - {ts_code}")
    
    trader = get_trader()
    
    # 获取持仓
    position = trader.get_position(ts_code)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("当前持仓")
        st.metric("持仓数量", f"{position['volume']} 股")
        st.metric("持仓成本", f"{position['avg_price']:.2f} 元")
    with col2:
        st.metric("当前价格", f"{position['current_price']:.2f} 元")
        st.metric("盈亏", f"{position['profit']:.2f} ({position['profit_rate']:.2f}%)")
    
    st.markdown("---")
    st.subheader("📝 交易操作")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        price = st.number_input("成交价格", value=position['current_price'], step=0.01)
    with col2:
        volume = st.number_input("交易数量", value=100, step=100, min_value=0)
    with col3:
        notes = st.text_input("备注", placeholder="交易备注")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🟢 买入"):
            if volume > 0 and price > 0:
                result = trader.buy(ts_code, price, volume, notes)
                if result:
                    st.success(f"✅ 买入成功！{volume}股 @ {price:.2f}元")
                else:
                    st.error("买入失败")
    with col2:
        if st.button("🔴 卖出"):
            if volume > 0 and price > 0:
                result = trader.sell(ts_code, price, volume, notes)
                if result:
                    st.success(f"✅ 卖出成功！{volume}股 @ {price:.2f}元")
                else:
                    st.error("卖出失败")
    
    st.markdown("---")
    st.subheader("📊 交易历史")
    
    trades = trader.get_trade_history(ts_code)
    if not trades.empty:
        st.dataframe(trades.style.format({
            'price': '{:.2f}',
            'volume': '{:,}',
            'amount': '{:.2f}',
            'commission': '{:.2f}',
            'stamp': '{:.2f}',
            'balance_after': '{:.2f}'
        }), use_container_width=True)
    else:
        st.info("暂无交易记录")
    
    # 绩效统计
    st.markdown("---")
    st.subheader("📈 绩效统计")
    
    perf = trader.get_performance_report()
    if 'stock_stats' in perf:
        for stock in perf['stock_stats']:
            st.markdown(f"### {stock['ts_code']}")
            st.metric("交易次数", stock['trades'])
            st.metric("总盈亏", f"{stock['profit']:.2f}", 
                     f"{stock['profit_rate']:.2f}%")
            st.progress(stock['profit_rate'] / 100)

def render_portfolio():
    """投资组合页面"""
    st.title("💰 投资组合")
    
    trader = get_trader()
    portfolio = trader.get_portfolio()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("总资产", f"{portfolio['total_capital']:.2f}")
    with col2:
        st.metric("持仓市值", f"{portfolio['market_value']:.2f}")
    with col3:
        st.metric("可用现金", f"{portfolio['cash']:.2f}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("总盈亏", f"{portfolio['total_profit']:.2f}")
    with col2:
        st.metric("收益率", f"{portfolio['total_profit_rate']:.2f}%")
    
    st.markdown("---")
    st.subheader("📊 当前持仓")
    
    if portfolio['positions']:
        positions_df = pd.DataFrame(portfolio['positions'])
        st.dataframe(positions_df.style.format({
            'avg_price': '{:.2f}',
            'current_price': '{:.2f}',
            'market_value': '{:.2f}',
            'cost': '{:.2f}',
            'profit': '{:.2f}',
            'profit_rate': '{:.2f}%'
        }), use_container_width=True)
    else:
        st.info("暂无持仓")
    
    # 资金分布
    st.markdown("---")
    st.subheader("💵 资金分布")
    
    fig = go.Figure(data=[go.Pie(
        labels=['持仓市值', '可用现金'],
        values=[portfolio['market_value'], portfolio['cash']],
        hole=0.3
    )])
    fig.update_layout(template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True)

# ==================== 路由逻辑 ====================
page = st.sidebar.radio("选择页面", ["首页", "股票详情", "AI 分析", "模拟交易", "投资组合"])

if page == "首页":
    render_home()
elif page == "股票详情":
    render_stock_detail(selected_stock)
elif page == "AI 分析":
    render_ai_analysis(selected_stock)
elif page == "模拟交易":
    render_trading(selected_stock)
elif page == "投资组合":
    render_portfolio()
