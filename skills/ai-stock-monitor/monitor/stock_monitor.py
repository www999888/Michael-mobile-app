"""
AI Stock Monitor - 实时监控模块
股票盯盘、价格告警、异常检测
"""
import time
import threading
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Callable, Optional
from data.data_fetcher import TushareFetcher, MockDataGenerator
from data.data_storage import get_database, get_cache
from analyzer.tech_analyzer import get_analyzer
from config.settings import STOCK_POOL, DEFAULT_STOCKS, ALERT_THRESHOLDS, FEATURES
from config.logging_config import main_logger, analyzer_logger

# ==================== 股票监控器类 ====================
class StockMonitor:
    """股票实时监控器"""
    
    def __init__(self, stock_pool: List[str] = None, alert_callbacks: List[Callable] = None):
        """
        初始化监控器
        
        Args:
            stock_pool: 监控股票池
            alert_callbacks: 告警回调函数列表
        """
        self.stock_pool = stock_pool or DEFAULT_STOCKS
        self.alert_callbacks = alert_callbacks or []
        
        self.fetcher = TushareFetcher()
        self.db = get_database()
        self.analyzer = get_analyzer()
        self.cache = get_cache()
        
        self.is_monitoring = False
        self.monitor_thread = None
        self.current_quotes = {}
        self.price_history = {}
        self.volume_history = {}
        
        # 告警状态追踪
        self.alert_cooldown = {}
        self.alert_cooldown_seconds = 300  # 同一股票 5 分钟内不重复告警
    
    def _validate_stock_pool(self) -> List[str]:
        """验证股票池"""
        valid_stocks = []
        for stock in self.stock_pool:
            if '.' in stock:  # 有效格式
                valid_stocks.append(stock)
            else:
                main_logger.warning(f"无效的股票代码：{stock}")
        return valid_stocks
    
    def update_stocks(self, stocks: List[str]):
        """更新监控股票列表"""
        self.stock_pool = self._validate_stock_pool()
        main_logger.info(f"更新监控股票池：{len(self.stock_pool)}只")
    
    def get_realtime_data(self, ts_code: str) -> Optional[pd.DataFrame]:
        """
        获取实时数据
        
        Args:
            ts_code: 股票代码
            
        Returns:
            实时数据或 None
        """
        # 尝试从缓存加载
        cached_data = self.cache.load_cache(ts_code, "minute")
        if cached_data is not None and not cached_data.empty:
            main_logger.info(f"使用缓存数据：{ts_code}")
            return cached_data
        
        # 尝试获取实时行情
        quote = self.fetcher.get_realtime_quote(ts_code)
        if quote is not None and not quote.empty:
            return quote
        
        # 使用模拟数据
        main_logger.info(f"获取模拟数据：{ts_code}")
        return MockDataGenerator.generate_mock_daily_data(ts_code, days=1)
    
    def check_price_alert(self, ts_code: str, current_price: float,
                         previous_price: float) -> Optional[Dict]:
        """
        检查价格告警
        
        Args:
            ts_code: 股票代码
            current_price: 当前价格
            previous_price: 之前价格
            
        Returns:
            告警信息或 None
        """
        if ts_code in self.alert_cooldown:
            last_alert = self.alert_cooldown[ts_code]
            if time.time() - last_alert < self.alert_cooldown_seconds:
                return None
        
        pct_change = ((current_price - previous_price) / previous_price * 100)
        
        alert = None
        
        # 涨跌幅告警
        if abs(pct_change) >= ALERT_THRESHOLDS['price_change_percent']:
            alert = {
                "type": "price_change",
                "ts_code": ts_code,
                "message": f"⚠️ {ts_code} 涨跌幅 {pct_change:+.2f}%",
                "price": current_price,
                "change": pct_change,
                "severity": "high" if abs(pct_change) >= 10 else "medium"
            }
        
        # 价格阈值告警
        if ALERT_THRESHOLDS['min_price'] and current_price < ALERT_THRESHOLDS['min_price']:
            alert = {
                "type": "price_min",
                "ts_code": ts_code,
                "message": f"⚠️ {ts_code} 价格触及下限 {current_price:.2f}",
                "price": current_price,
                "threshold": ALERT_THRESHOLDS['min_price'],
                "severity": "critical"
            }
        
        if alert:
            self.alert_cooldown[ts_code] = time.time()
            main_logger.warning(f"价格告警触发：{alert['message']}")
            return alert
        
        return None
    
    def check_volume_alert(self, ts_code: str, current_volume: float,
                          avg_volume: float) -> Optional[Dict]:
        """
        检查成交量告警
        
        Args:
            ts_code: 股票代码
            current_volume: 当前成交量
            avg_volume: 平均成交量
            
        Returns:
            告警信息或 None
        """
        if ts_code in self.alert_cooldown:
            return None
        
        if avg_volume == 0:
            return None
        
        volume_ratio = current_volume / avg_volume
        
        if volume_ratio >= ALERT_THRESHOLDS['volume_increase']:
            alert = {
                "type": "volume",
                "ts_code": ts_code,
                "message": f"📈 {ts_code} 成交量放大 {volume_ratio:.2f}倍",
                "current_volume": current_volume,
                "avg_volume": avg_volume,
                "ratio": volume_ratio,
                "severity": "high" if volume_ratio >= 5 else "medium"
            }
            
            self.alert_cooldown[ts_code] = time.time()
            main_logger.warning(f"成交量告警触发：{alert['message']}")
            return alert
        
        return None
    
    def check_trend_alert(self, ts_code: str, df: pd.DataFrame,
                         signals: Dict) -> Optional[Dict]:
        """
        检查趋势告警
        
        Args:
            ts_code: 股票代码
            df: 技术指标数据
            signals: 技术分析信号
            
        Returns:
            告警信息或 None
        """
        if ts_code in self.alert_cooldown:
            return None
        
        if signals.get('score', 0) <= -5:
            alert = {
                "type": "trend_down",
                "ts_code": ts_code,
                "message": f"📉 {ts_code} 下跌趋势强烈 (信号：{signals.get('overall_signal', 'N/A')})",
                "signal": signals.get('overall_signal'),
                "score": signals.get('score'),
                "severity": "high"
            }
            
            self.alert_cooldown[ts_code] = time.time()
            main_logger.warning(f"趋势告警触发：{alert['message']}")
            return alert
        
        if signals.get('score', 0) >= 5:
            alert = {
                "type": "trend_up",
                "ts_code": ts_code,
                "message": f"📈 {ts_code} 上涨趋势强烈 (信号：{signals.get('overall_signal', 'N/A')})",
                "signal": signals.get('overall_signal'),
                "score": signals.get('score'),
                "severity": "medium"
            }
            
            self.alert_cooldown[ts_code] = time.time()
            main_logger.info(f"趋势告警触发：{alert['message']}")
            return alert
        
        return None
    
    def process_alerts(self, alert: Dict):
        """
        处理告警
        
        Args:
            alert: 告警信息
        """
        if not FEATURES['alerts']:
            return
        
        main_logger.warning(f"触发告警：{alert['message']}")
        
        # 调用所有回调函数
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                main_logger.error(f"告警回调执行失败：{e}")
        
        # 发送到控制台
        print(f"\n{'='*60}")
        print(f"⚠️ {alert['message']}")
        print(f"{'='*60}\n")
    
    def monitor_single_stock(self, ts_code: str) -> Dict:
        """
        监控单只股票
        
        Args:
            ts_code: 股票代码
            
        Returns:
            监控结果
        """
        result = {
            "ts_code": ts_code,
            "status": "success",
            "alert_triggered": False
        }
        
        try:
            # 获取数据
            df = self.get_realtime_data(ts_code)
            if df is None or df.empty:
                result["status"] = "no_data"
                return result
            
            # 计算技术指标
            df_with_indicators = self.analyzer.calculate_all_indicators(df)
            
            # 获取交易信号
            signals = self.analyzer.get_signal(df_with_indicators, ts_code)
            
            # 最新价格
            current_price = float(df_with_indicators['close'].iloc[-1])
            
            # 价格历史
            if ts_code not in self.price_history:
                self.price_history[ts_code] = current_price
            previous_price = self.price_history[ts_code]
            
            # 检查价格告警
            price_alert = self.check_price_alert(ts_code, current_price, previous_price)
            if price_alert:
                self.process_alerts(price_alert)
                result["alert_triggered"] = True
            
            self.price_history[ts_code] = current_price
            
            # 成交量历史
            if ts_code not in self.volume_history:
                self.volume_history[ts_code] = df_with_indicators['vol'].iloc[-1]
            current_volume = float(df_with_indicators['vol'].iloc[-1])
            avg_volume = sum(list(self.volume_history[ts_code].values())) / len(self.volume_history[ts_code])
            
            # 检查成交量告警
            volume_alert = self.check_volume_alert(ts_code, current_volume, avg_volume)
            if volume_alert:
                self.process_alerts(volume_alert)
                result["alert_triggered"] = True
            
            # 检查趋势告警
            trend_alert = self.check_trend_alert(ts_code, df_with_indicators, signals)
            if trend_alert:
                self.process_alerts(trend_alert)
                result["alert_triggered"] = True
            
            result.update({
                "current_price": current_price,
                "signals": signals,
                "indicators": signals.get('indicators', {}),
                "data_length": len(df_with_indicators)
            })
            
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            main_logger.error(f"监控 {ts_code} 失败：{e}")
        
        return result
    
    def monitor_all_stocks(self, loop: bool = False, interval: int = 60) -> List[Dict]:
        """
        监控所有股票
        
        Args:
            loop: 是否循环监控
            interval: 监控间隔（秒）
            
        Returns:
            监控结果列表
        """
        results = []
        
        for ts_code in self.stock_pool:
            try:
                result = self.monitor_single_stock(ts_code)
                results.append(result)
            except Exception as e:
                main_logger.error(f"监控 {ts_code} 异常：{e}")
        
        return results
    
    def start_monitoring(self, interval: int = 60, loop: bool = True):
        """
        启动监控
        
        Args:
            interval: 监控间隔（秒）
            loop: 是否循环监控
        """
        if self.is_monitoring:
            main_logger.warning("监控已经在运行中")
            return
        
        self.is_monitoring = True
        main_logger.info(f"开始监控，间隔 {interval} 秒")
        
        def monitoring_loop():
            iteration = 0
            while self.is_monitoring:
                iteration += 1
                main_logger.info(f"监控周期 {iteration} 开始...")
                
                try:
                    results = self.monitor_all_stocks()
                    
                    # 统计告警情况
                    alerts = sum(1 for r in results if r.get('alert_triggered'))
                    if alerts > 0:
                        main_logger.warning(f"本轮发现 {alerts} 个告警")
                    
                except Exception as e:
                    main_logger.error(f"监控循环异常：{e}")
                
                if not loop:
                    break
                
                # 等待下一个周期
                for _ in range(interval):
                    if not self.is_monitoring:
                        break
                    time.sleep(1)
            
            main_logger.info("监控循环结束")
        
        self.monitor_thread = threading.Thread(target=monitoring_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
            self.monitor_thread = None
        main_logger.info("监控已停止")
    
    def get_status(self) -> Dict:
        """获取监控状态"""
        return {
            "is_monitoring": self.is_monitoring,
            "stock_count": len(self.stock_pool),
            "stocks": self.stock_pool,
            "current_quotes": len(self.current_quotes),
            "alert_cooldown_stocks": len(self.alert_cooldown)
        }

# ==================== 单例模式 ====================
_monitor_instance = None

def get_monitor(stock_pool: List[str] = None) -> StockMonitor:
    """获取监控器实例"""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = StockMonitor(stock_pool=stock_pool)
    return _monitor_instance
