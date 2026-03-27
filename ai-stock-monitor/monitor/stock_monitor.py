"""
股票盯盘模块
实时监控股票价格、告警通知
"""

import time
from typing import List, Dict, Optional
from datetime import datetime
from config import MONITORING, ALERT_THRESHOLD, STOCK_POOLS, logger
from data import StockDataFetcher

class StockMonitor:
    """股票监控器"""
    
    def __init__(self):
        self.fetcher = StockDataFetcher()
        self.alert_callbacks = []  # 告警回调函数列表
        self.monitored_stocks = []
    
    def add_alert_callback(self, callback):
        """添加告警回调"""
        self.alert_callbacks.append(callback)
    
    def start_monitoring(self, stocks: List[str] = None, interval: int = 60):
        """
        启动监控
        :param stocks: 监控的股票列表
        :param interval: 检查间隔（秒）
        """
        self.monitored_stocks = stocks or STOCK_POOLS.get("沪深 A 股", [])
        logger.info(f"开始监控 {len(self.monitored_stocks)} 只股票，间隔 {interval} 秒")
        
        while MONITORING["alert_enabled"]:
            try:
                self._check_stocks()
                time.sleep(interval)
            except KeyboardInterrupt:
                logger.info("监控停止")
                break
            except Exception as e:
                logger.error(f"监控错误：{e}")
                time.sleep(60)
    
    def _check_stocks(self):
        """检查所有监控的股票"""
        for stock_code in self.monitored_stocks:
            try:
                # 获取实时数据
                data = self.fetcher.get_realtime_quote(stock_code)
                if not data:
                    continue
                
                # 检查告警条件
                alerts = self._check_alerts(stock_code, data)
                
                # 触发告警回调
                for alert in alerts:
                    for callback in self.alert_callbacks:
                        try:
                            callback(alert)
                        except Exception as e:
                            logger.error(f"告警回调失败：{e}")
            
            except Exception as e:
                logger.error(f"检查股票 {stock_code} 失败：{e}")
    
    def _check_alerts(self, stock_code: str, data: Dict) -> List[Dict]:
        """检查告警条件"""
        alerts = []
        
        # 涨跌幅告警
        change_pct = data.get("change_pct", 0)
        if abs(change_pct) > ALERT_THRESHOLD["price_change_pct"]:
            alerts.append({
                "type": "PRICE_CHANGE",
                "stock_code": stock_code,
                "message": f"{stock_code} 涨跌幅：{change_pct:.2f}%",
                "severity": "HIGH" if abs(change_pct) > 7 else "MEDIUM",
                "data": {"change_pct": change_pct}
            })
        
        # 成交量告警
        volume = data.get("volume", 0)
        # 这里需要对比历史成交量，简化处理
        
        # RSI 超买超卖告警
        # 需要技术分析数据，这里简化
        
        return alerts
    
    def get_current_status(self) -> List[Dict]:
        """获取当前所有监控股票的状态"""
        status_list = []
        for stock_code in self.monitored_stocks:
            data = self.fetcher.get_realtime_quote(stock_code)
            if data:
                status_list.append({
                    "stock_code": stock_code,
                    "price": data.get("price"),
                    "change_pct": data.get("change_pct"),
                    "volume": data.get("volume"),
                    "timestamp": datetime.fromtimestamp(data.get("timestamp", 0)).strftime("%H:%M:%S")
                })
        return status_list
    
    def stop_monitoring(self):
        """停止监控"""
        MONITORING["alert_enabled"] = False
        logger.info("监控已停止")
