"""
AI Stock Monitor - 测试脚本
验证各模块功能是否正常
"""
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).resolve().parent))

from data.data_fetcher import MockDataGenerator, TushareFetcher
from data.data_storage import get_database, get_cache
from analyzer.tech_analyzer import get_analyzer
from analyzer.ai_analyzer import get_ai_analyzer
from monitor.stock_monitor import get_monitor
from trader.sim_trader import get_trader
from config.settings import DEFAULT_STOCKS

def test_data_fetcher():
    """测试数据获取"""
    print("\n[测试 1/6] 数据获取模块...")
    try:
        ts_code = DEFAULT_STOCKS[0]
        df = MockDataGenerator.generate_mock_daily_data(ts_code, 10)
        print(f"✅ 模拟数据生成成功：{ts_code}, {len(df)} 行数据")
        return True
    except Exception as e:
        print(f"❌ 数据获取失败：{e}")
        return False

def test_data_storage():
    """测试数据存储"""
    print("\n[测试 2/6] 数据存储模块...")
    try:
        db = get_database()
        print(f"✅ 数据库连接成功：{db.db_path}")
        
        # 测试缓存
        cache = get_cache()
        print(f"✅ 缓存系统就绪：{cache.cache_dir}")
        return True
    except Exception as e:
        print(f"❌ 数据存储失败：{e}")
        return False

def test_technical_analyzer():
    """测试技术分析"""
    print("\n[测试 3/6] 技术分析模块...")
    try:
        analyzer = get_analyzer()
        df = MockDataGenerator.generate_mock_daily_data(DEFAULT_STOCKS[0], 20)
        df_indicators = analyzer.calculate_all_indicators(df)
        
        print(f"✅ 指标计算完成：{len(df_indicators)} 行")
        print(f"   - MA: {'ma_short' in df_indicators.columns}")
        print(f"   - MACD: {'macd' in df_indicators.columns}")
        print(f"   - KDJ: {'kdj_k' in df_indicators.columns}")
        print(f"   - RSI: {'rsi_short' in df_indicators.columns}")
        print(f"   - BOLL: {'boll_upper' in df_indicators.columns}")
        
        # 生成信号
        signals = analyzer.get_signal(df_indicators, DEFAULT_STOCKS[0])
        print(f"✅ 交易信号：{signals['overall_signal']} (得分：{signals['score']})")
        return True
    except Exception as e:
        print(f"❌ 技术分析失败：{e}")
        return False

def test_ai_analyzer():
    """测试 AI 分析"""
    print("\n[测试 4/6] AI 分析模块...")
    try:
        ai_analyzer = get_ai_analyzer()
        available = ai_analyzer._check_model_available()
        
        if available:
            df = MockDataGenerator.generate_mock_daily_data(DEFAULT_STOCKS[0], 20)
            df_indicators = ai_analyzer.calculate_all_indicators(df)
            signals = ai_analyzer.get_signal(df_indicators, DEFAULT_STOCKS[0])
            
            result = ai_analyzer.analyze(DEFAULT_STOCKS[0], df_indicators, signals)
            print(f"✅ AI 分析成功：模型 {ai_analyzer.model}")
            return True
        else:
            print("⚠️  Ollama 模型未就绪，跳过 AI 分析测试")
            return True
    except Exception as e:
        print(f"❌ AI 分析失败：{e}")
        return False

def test_monitor():
    """测试监控模块"""
    print("\n[测试 5/6] 监控模块...")
    try:
        monitor = get_monitor()
        
        # 测试单个股票监控
        result = monitor.monitor_single_stock(DEFAULT_STOCKS[0])
        
        print(f"✅ 监控测试完成：{result['status']}")
        print(f"   - 股票：{result.get('ts_code')}")
        print(f"   - 价格：{result.get('current_price', 'N/A')}")
        print(f"   - 告警触发：{result.get('alert_triggered')}")
        return True
    except Exception as e:
        print(f"❌ 监控测试失败：{e}")
        return False

def test_trader():
    """测试交易模块"""
    print("\n[测试 6/6] 模拟交易模块...")
    try:
        trader = get_trader()
        
        # 获取当前资金
        portfolio = trader.get_portfolio()
        print(f"✅ 模拟交易器就绪")
        print(f"   - 初始资金：{portfolio['total_capital']:.2f}")
        print(f"   - 当前持仓：{portfolio['position_count']}只")
        
        # 获取持仓
        pos = trader.get_position(DEFAULT_STOCKS[0])
        print(f"   - {DEFAULT_STOCKS[0]} 持仓：{pos['volume']}股")
        return True
    except Exception as e:
        print(f"❌ 交易模块测试失败：{e}")
        return False

def main():
    """运行所有测试"""
    print("=" * 60)
    print("🧪 AI Stock Monitor - 功能测试")
    print("=" * 60)
    
    results = []
    results.append(("数据获取", test_data_fetcher()))
    results.append(("数据存储", test_data_storage()))
    results.append(("技术分析", test_technical_analyzer()))
    results.append(("AI 分析", test_ai_analyzer()))
    results.append(("监控模块", test_monitor()))
    results.append(("模拟交易", test_trader()))
    
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print("\n" + "-" * 60)
    print(f"通过：{passed}/{total}")
    
    if passed == total:
        print("\n🎉 所有测试通过！系统运行正常！")
        return 0
    else:
        print(f"\n⚠️ {total - passed}个测试失败，请检查配置")
        return 1

if __name__ == "__main__":
    sys.exit(main())
