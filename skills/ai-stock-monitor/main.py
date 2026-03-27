"""
AI Stock Monitor - 项目入口
一键启动所有功能
"""
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config.settings import FEATURES
from config.logging_config import setup_logger, log_system_status
from data.data_storage import get_database
from monitor.stock_monitor import get_monitor
from ui.web_ui import render_home  # 用于测试

# 设置日志
logger = setup_logger("main")

def initialize():
    """初始化系统"""
    logger.info("🚀 AI Stock Monitor 初始化中...")
    
    # 检查功能开关
    if not any([FEATURES['realtime_monitor'], FEATURES['ai_analysis'], 
                FEATURES['sim_trading'], FEATURES['alerts']]):
        logger.warning("所有功能都已关闭！请检查配置")
    
    # 初始化数据库
    db = get_database()
    
    # 检查 Ollama 可用性
    if FEATURES['ai_analysis']:
        try:
            from analyzer.ai_analyzer import get_ai_analyzer
            ai = get_ai_analyzer()
            if ai._check_model_available():
                logger.info(f"✅ Ollama 模型 {ai.model} 已就绪")
            else:
                logger.warning("⚠️ Ollama 模型未就绪，AI 分析功能不可用")
        except Exception as e:
            logger.error(f"Ollama 初始化失败：{e}")
    
    log_system_status()
    logger.info("🎉 系统初始化完成！")

def run_web_ui():
    """运行 Web 界面"""
    try:
        from streamlit.web import cli as stcli
        from streamlit import config
        
        config.set_option('server.port', 8501)
        config.set_option('browser.serverAddress', '127.0.0.1')
        
        sys.argv = [
            "streamlit", 
            "run", 
            "ui/web_ui.py",
            "--server.headless=true"
        ]
        
        sys.exit(stcli.main())
    except Exception as e:
        logger.error(f"Web UI 启动失败：{e}")
        import traceback
        traceback.print_exc()

def run_monitor():
    """运行监控功能"""
    monitor = get_monitor()
    monitor.start_monitoring(interval=60, loop=True)
    
    try:
        while monitor.is_monitoring:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        monitor.stop_monitoring()

def run_quick_demo():
    """运行快速演示"""
    from analyzer.tech_analyzer import get_analyzer
    from data.data_fetcher import MockDataGenerator
    
    logger.info("🎬 运行快速演示...")
    
    ts_code = "000001.SZ"
    df = MockDataGenerator.generate_mock_daily_data(ts_code, 30)
    
    analyzer = get_analyzer()
    df_indicators = analyzer.calculate_all_indicators(df)
    
    signals = analyzer.get_signal(df_indicators, ts_code)
    
    logger.info(f"📊 股票：{ts_code}")
    logger.info(f"💰 当前价格：{signals['latest_price']:.2f}")
    logger.info(f"📈 综合信号：{signals['overall_signal']}")
    logger.info(f"🎯 评分：{signals['score']}")
    
    if signals.get('signals'):
        logger.info("🔍 关键信号:")
        for signal in signals['signals']:
            logger.info(f"  • {signal}")

def main():
    """主函数"""
    initialize()
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "demo":
            run_quick_demo()
        elif command == "web":
            run_web_ui()
        elif command == "monitor":
            run_monitor()
        else:
            logger.warning(f"未知命令：{command}")
            logger.info("可用命令：demo, web, monitor")
    else:
        # 默认运行演示
        logger.info("💡 提示：运行以下命令使用不同功能:")
        logger.info("  python main.py demo     - 快速演示")
        logger.info("  python main.py web      - 启动 Web 界面")
        logger.info("  python main.py monitor  - 启动监控")

if __name__ == "__main__":
    main()
