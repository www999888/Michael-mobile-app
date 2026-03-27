"""
股票数据存储模块
处理数据缓存和持久化
"""

import json
import pickle
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import pandas as pd
from config import STOCK_DATA_DIR, HISTORY_DATA_DIR, DATA_CACHE_TTL, logger

class StockDataStorage:
    """股票数据存储与缓存"""
    
    def __init__(self):
        self.data_dir = STOCK_DATA_DIR
        self.history_dir = HISTORY_DATA_DIR
        self._init_dirs()
    
    def _init_dirs(self):
        """初始化目录"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.history_dir.mkdir(parents=True, exist_ok=True)
    
    def cache_realtime_quote(self, stock_code: str, data: Dict):
        """缓存实时行情"""
        cache_file = self.data_dir / f"{stock_code}_realtime.json"
        cache_data = {
            "stock_code": stock_code,
            "data": data,
            "cached_at": datetime.now().timestamp(),
            "ttl": DATA_CACHE_TTL
        }
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
    
    def get_cached_quote(self, stock_code: str) -> Optional[Dict]:
        """获取缓存的实时行情"""
        cache_file = self.data_dir / f"{stock_code}_realtime.json"
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cache_data = json.load(f)
            
            # 检查是否过期
            cached_at = cache_data.get("cached_at", 0)
            if datetime.now().timestamp() - cached_at > DATA_CACHE_TTL:
                cache_file.unlink()
                return None
            
            return cache_data.get("data")
            
        except Exception as e:
            logger.error(f"读取缓存失败 {stock_code}: {e}")
            return None
    
    def save_history_data(self, stock_code: str, df: pd.DataFrame):
        """保存历史数据"""
        # 转换为 pickle 格式
        file_path = self.history_dir / f"{stock_code}_history.pkl"
        df.to_pickle(file_path)
        logger.info(f"历史数据已保存 {stock_code}")
    
    def load_history_data(self, stock_code: str) -> Optional[pd.DataFrame]:
        """加载历史数据"""
        file_path = self.history_dir / f"{stock_code}_history.pkl"
        if not file_path.exists():
            return None
        
        try:
            return pd.read_pickle(file_path)
        except Exception as e:
            logger.error(f"读取历史数据失败 {stock_code}: {e}")
            return None
    
    def get_trade_history(self, stock_code: str) -> List[Dict]:
        """获取交易历史"""
        file_path = self.data_dir / f"{stock_code}_trades.json"
        if not file_path.exists():
            return []
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    
    def save_trade(self, stock_code: str, trade: Dict):
        """保存交易记录"""
        trades = self.get_trade_history(stock_code)
        trade["timestamp"] = datetime.now().isoformat()
        trades.append(trade)
        
        file_path = self.data_dir / f"{stock_code}_trades.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(trades, f, ensure_ascii=False, indent=2)
    
    def get_portfolio_summary(self) -> Dict:
        """获取持仓汇总"""
        total_capital = 0
        positions = []
        
        # 遍历所有交易记录
        for file in self.data_dir.glob("*_trades.json"):
            stock_code = file.stem.replace("_trades", "")
            trades = self.get_trade_history(stock_code)
            if trades:
                # 计算当前持仓价值
                current_price = self.get_cached_quote(stock_code)
                if current_price:
                    total_capital += current_price["price"] * sum(t.get("shares", 0) for t in trades)
                    positions.append({
                        "stock": stock_code,
                        "value": current_price["price"] * sum(t.get("shares", 0) for t in trades)
                    })
        
        return {
            "total_capital": total_capital,
            "positions": positions
        }
    
    def clear_expired_cache(self):
        """清理过期缓存"""
        now = datetime.now().timestamp()
        for file in self.data_dir.glob("*.json"):
            try:
                with open(file, "r") as f:
                    data = json.load(f)
                if now - data.get("cached_at", 0) > DATA_CACHE_TTL:
                    file.unlink()
                    logger.info(f"清理过期缓存：{file.name}")
            except:
                pass
