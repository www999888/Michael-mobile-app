"""
AI Stock Monitor - 数据获取模块
基于 Tushare API 获取股票数据
"""
import pandas as pd
import requests
import time
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from config.settings import TUSHARE_TOKEN, STOCK_POOL, TIMEOUT_SECONDS
from config.logging_config import data_logger

# ==================== Tushare 数据获取类 ====================
class TushareFetcher:
    """Tushare 股票数据获取器"""
    
    def __init__(self, token: str = None):
        """
        初始化 Tushare 获取器
        
        Args:
            token: Tushare API token
        """
        self.token = token or TUSHARE_TOKEN
        self.base_url = "http://api.tushare.pro"
        
    def _make_request(self, api_name: str, params: Dict = None) -> Optional[Dict]:
        """
        发送 API 请求
        
        Args:
            api_name: API 名称
            params: 请求参数
            
        Returns:
            API 响应数据或 None
        """
        if not self.token:
            data_logger.warning("Tushare token 未配置，无法获取数据")
            return None
            
        headers = {"Authorization": f"token {self.token}"}
        payload = {"api_name": api_name, "params": params or {}}
        
        try:
            response = requests.post(
                self.base_url,
                json=payload,
                headers=headers,
                timeout=TIMEOUT_SECONDS
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            data_logger.error(f"Tushare API 请求失败：{e}")
            return None
    
    def get_daily_data(self, ts_code: str, start_date: str = None, 
                      end_date: str = None, days: int = 30) -> Optional[pd.DataFrame]:
        """
        获取日线数据
        
        Args:
            ts_code: 股票代码
            start_date: 开始日期 YYYYMMDD
            end_date: 结束日期 YYYYMMDD
            days: 获取最近 N 天数据（可选）
            
        Returns:
            DataFrame: 日线数据
        """
        # 自动计算日期
        if not start_date and not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")
        elif not start_date:
            start_date = (datetime.now() - timedelta(days=60)).strftime("%Y%m%d")
        elif not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        
        params = {
            "ts_code": ts_code,
            "start_date": start_date,
            "end_date": end_date
        }
        
        data = self._make_request("daily", params)
        
        if data and data.get('code') == 20001:
            df = pd.DataFrame(data['data']['items'])
            if not df.empty:
                df['trade_date'] = pd.to_datetime(df['trade_date'])
                df.set_index('trade_date', inplace=True)
                data_logger.info(f"获取 {ts_code} 日线数据完成，共{len(df)}条")
                return df.sort_index(ascending=False)
        return None
    
    def get_min_data(self, ts_code: str, period: str = '1min', 
                    start_time: str = None, end_time: str = None,
                    days: int = 1) -> Optional[pd.DataFrame]:
        """
        获取分钟线数据
        
        Args:
            ts_code: 股票代码
            period: 周期 (1/5/15/30/60min)
            start_time: 开始时间
            end_time: 结束时间
            days: 获取最近 N 天数据
            
        Returns:
            DataFrame: 分钟线数据
        """
        if not start_time and not end_time:
            end_time = datetime.now().strftime("%Y%m%d%H%M%S")
            start_time = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d%H%M%S")
        
        params = {
            "ts_code": ts_code,
            "period": period,
            "start_time": start_time,
            "end_time": end_time
        }
        
        data = self._make_request("mins", params)
        
        if data and data.get('code') == 20001:
            df = pd.DataFrame(data['data']['items'])
            if not df.empty:
                df['trade_time'] = pd.to_datetime(df['trade_time'])
                df.set_index('trade_time', inplace=True)
                data_logger.info(f"获取 {ts_code} {period} 数据完成，共{len(df)}条")
                return df.sort_index(ascending=False)
        return None
    
    def get_realtime_quote(self, ts_code: str = None, 
                          symbols: List[str] = None) -> Optional[pd.DataFrame]:
        """
        获取实时行情
        
        Args:
            ts_code: 单个股票代码
            symbols: 股票代码列表
            
        Returns:
            DataFrame: 实时行情数据
        """
        if not symbols and ts_code:
            symbols = [ts_code]
        
        params = {"ts_code": ",".join(symbols)} if symbols else {}
        
        data = self._make_request("quote", params)
        
        if data and data.get('code') == 20001:
            df = pd.DataFrame(data['data']['items'])
            data_logger.info(f"获取实时行情完成，共{len(df)}条数据")
            return df
        return None
    
    def get_basic_info(self, ts_code: str = None) -> Optional[pd.DataFrame]:
        """
        获取股票基本信息
        
        Args:
            ts_code: 单个股票代码
            
        Returns:
            DataFrame: 基本信息
        """
        params = {"ts_code": ts_code} if ts_code else {}
        
        data = self._make_request("pro_name", params)
        
        if data and data.get('code') == 20001:
            df = pd.DataFrame(data['data']['items'])
            data_logger.info(f"获取基本信息完成，共{len(df)}条数据")
            return df
        return None
    
    def get_balance_sheet(self, ts_code: str, start_date: str = None,
                         end_date: str = None) -> Optional[pd.DataFrame]:
        """
        获取财务报表 - 资产负债表
        
        Args:
            ts_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            DataFrame: 资产负债表数据
        """
        params = {"ts_code": ts_code}
        if start_date and end_date:
            params["start_date"] = start_date
            params["end_date"] = end_date
        
        data = self._make_request("balances", params)
        
        if data and data.get('code') == 20001:
            df = pd.DataFrame(data['data']['items'])
            if not df.empty:
                df['end_date'] = pd.to_datetime(df['end_date'])
                df.set_index('end_date', inplace=True)
                return df.sort_index(ascending=False)
        return None

# ==================== 模拟数据生成器 ====================
class MockDataGenerator:
    """
    模拟数据生成器 - 用于演示和测试
    当 Tushare token 未配置时使用
    """
    
    @staticmethod
    def generate_mock_daily_data(ts_code: str, days: int = 30) -> pd.DataFrame:
        """生成模拟日线数据"""
        import numpy as np
        
        np.random.seed(hash(ts_code) % 2**32)
        dates = pd.date_range(end=datetime.now(), periods=days, freq='B')
        
        base_price = np.random.uniform(5, 100)
        returns = np.random.normal(0.001, 0.02, days)
        prices = base_price * np.cumprod(1 + returns)
        
        data = {
            'ts_code': ts_code,
            'trade_date': dates,
            'open': prices * (1 + np.random.uniform(-0.01, 0.01, days)),
            'high': prices * (1 + np.random.uniform(0, 0.02, days)),
            'low': prices * (1 - np.random.uniform(0, 0.02, days)),
            'close': prices,
            'vol': np.random.randint(10000, 1000000, days),
            'amount': prices * np.random.randint(10000, 1000000, days),
            'pct_chg': (prices / prices.shift(1) - 1) * 100
        }
        
        df = pd.DataFrame(data)
        df = df.dropna()
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        df.set_index('trade_date', inplace=True)
        
        return df.sort_index(ascending=False)
