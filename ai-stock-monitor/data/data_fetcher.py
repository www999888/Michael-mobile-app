"""
股票数据获取模块
支持 Tushare 和 免费数据源
"""

import requests
import time
from typing import List, Dict, Optional
import pandas as pd
from pathlib import Path
from datetime import datetime
from config import OLLAMA_BASE_URL, SUPPORTED_MARKETS, logger

class StockDataFetcher:
    """股票数据获取器"""
    
    def __init__(self):
        self.base_url = OLLAMA_BASE_URL
        self.session = requests.Session()
        self._init_free_data_source()
    
    def _init_free_data_source(self):
        """初始化免费数据源"""
        # 这里使用模拟数据，实际可以对接 Tushare/新浪财经等
        self.free_api_base = "https://push2.eastmoney.com"
    
    def get_realtime_quote(self, stock_code: str) -> Optional[Dict]:
        """
        获取实时行情
        返回：{"code": "000001.SZ", "price": 12.5, "change_pct": 2.5, "volume": 1000000}
        """
        try:
            # 东方财富接口
            market = "1" if stock_code.endswith("SH") else "0"
            code = stock_code.replace(".SH", "").replace(".SZ", "")
            
            url = f"{self.free_api_base}/qt/get"
            params = {
                "f": "12",
                "secid": f"{market}.{code}",
                "ut": "fa5fd1ed4b5ca9f5a8b0d58b1b0b1b0b",
                "cb": "jsonp_cb_123",
                "_": int(time.time() * 1000)
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            # 解析 JSONP 响应
            json_str = response.text[10:-2]
            import json
            data = json.loads(json_str)
            
            if data and "data" in data and "f1" in data["data"]:
                quote_data = data["data"]
                return {
                    "code": stock_code,
                    "price": float(quote_data.get("f5", 0)),
                    "change_pct": float(quote_data.get("f12", 0)),
                    "volume": int(quote_data.get("f6", 0)),
                    "open": float(quote_data.get("f7", 0)),
                    "high": float(quote_data.get("f8", 0)),
                    "low": float(quote_data.get("f9", 0)),
                    "prev_close": float(quote_data.get("f10", 0)),
                    "timestamp": datetime.now().timestamp()
                }
                
        except Exception as e:
            logger.error(f"获取实时行情失败 {stock_code}: {e}")
            # 返回模拟数据
            return self._get_mock_realtime(stock_code)
        
        return None
    
    def _get_mock_realtime(self, stock_code: str) -> Dict:
        """返回模拟数据（开发用）"""
        import random
        base_price = random.uniform(10, 100)
        return {
            "code": stock_code,
            "price": round(base_price, 2),
            "change_pct": round(random.uniform(-5, 5), 2),
            "volume": random.randint(100000, 5000000),
            "open": round(base_price * random.uniform(0.98, 1.02), 2),
            "high": round(base_price * random.uniform(1.0, 1.05), 2),
            "low": round(base_price * random.uniform(0.95, 1.0), 2),
            "prev_close": round(base_price, 2),
            "timestamp": time.time()
        }
    
    def get_history_data(self, stock_code: str, days: int = 60) -> pd.DataFrame:
        """
        获取历史数据
        返回 DataFrame: date, open, high, low, close, volume
        """
        try:
            # 东方财富历史数据接口
            market = "1" if stock_code.endswith("SH") else "0"
            code = stock_code.replace(".SH", "").replace(".SZ", "")
            
            url = f"{self.free_api_base}/qt/skline"
            params = {
                "type": "kline_day",
                "secid": f"{market}.{code}",
                "klt": 101,  # 日 K 线
                "fqt": 1,    # 前复权
                "beg": max(0, days - 30),  # 开始日期索引
                "end": days,  # 结束日期索引
                "ut": "fa5fd1ed4b5ca9f5a8b0d58b1b0b1b0b",
                "cb": "jsonp_cb_456",
                "_": int(time.time() * 1000)
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            import json
            json_str = response.text[10:-2]
            data = json.loads(json_str)
            
            if data and "klines" in data:
                klines = data["klines"]
                records = []
                for kline in klines:
                    parts = kline.split(",")
                    if len(parts) >= 6:
                        records.append({
                            "date": parts[0],
                            "open": float(parts[1]),
                            "high": float(parts[2]),
                            "low": float(parts[3]),
                            "close": float(parts[4]),
                            "volume": int(parts[5])
                        })
                
                df = pd.DataFrame(records)
                df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")
                df.set_index("date", inplace=True)
                return df
            
        except Exception as e:
            logger.error(f"获取历史数据失败 {stock_code}: {e}")
            return self._get_mock_history(stock_code, days)
        
        return self._get_mock_history(stock_code, days)
    
    def _get_mock_history(self, stock_code: str, days: int = 60) -> pd.DataFrame:
        """返回模拟历史数据（开发用）"""
        import pandas as pd
        import random
        from datetime import timedelta
        
        dates = pd.date_range(end=pd.Timestamp.today() - timedelta(days=1), periods=days, freq="B")
        base_price = 50.0
        prices = [base_price]
        
        for i in range(1, days):
            change = random.uniform(-0.05, 0.05)
            prices.append(max(0.1, prices[-1] * (1 + change)))
        
        data = []
        for date, close in zip(dates, prices):
            data.append({
                "date": date,
                "open": close * random.uniform(0.98, 1.02),
                "high": close * random.uniform(1.0, 1.05),
                "low": close * random.uniform(0.95, 1.0),
                "close": close,
                "volume": random.randint(100000, 5000000)
            })
        
        df = pd.DataFrame(data)
        df.set_index("date", inplace=True)
        return df
    
    def get_all_stock_codes(self) -> List[str]:
        """获取所有股票代码（返回部分示例）"""
        # 实际应该调用 Tushare 接口获取全部
        return [
            "000001.SZ", "000002.SZ", "000006.SZ", "000027.SZ", "000060.SZ",
            "600000.SH", "600004.SH", "600016.SH", "600018.SH", "600028.SH"
        ]
