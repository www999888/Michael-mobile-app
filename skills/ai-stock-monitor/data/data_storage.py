"""
AI Stock Monitor - 数据存储模块
本地 SQLite 数据库存储股票数据
"""
import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List
from config.settings import DATA_DIR, CACHE_DIR
from config.logging_config import data_logger

# ==================== 数据库配置 ====================
DB_NAME = "stock_data.db"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

class StockDatabase:
    """股票数据存储类"""
    
    def __init__(self, db_path: str = None):
        """
        初始化数据库连接
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path or str(DATA_DIR / DB_NAME)
        self.conn = None
        self._init_database()
    
    def _init_database(self):
        """初始化数据库表结构"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = self.conn.cursor()
        
        # 日线数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts_code TEXT NOT NULL,
                trade_date DATE NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                vol REAL,
                amount REAL,
                pct_chg REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(ts_code, trade_date)
            )
        ''')
        
        # 分钟线数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS minute_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts_code TEXT NOT NULL,
                trade_time TIMESTAMP NOT NULL,
                period TEXT,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                vol REAL,
                amount REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(ts_code, period, trade_time)
            )
        ''')
        
        # 指标数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS indicators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts_code TEXT NOT NULL,
                trade_date DATE NOT NULL,
                indicator_type TEXT NOT NULL,
                indicator_name TEXT NOT NULL,
                value REAL,
                signal TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(ts_code, trade_date, indicator_type, indicator_name)
            )
        ''')
        
        # 模拟交易记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts_code TEXT NOT NULL,
                trade_type TEXT NOT NULL,
                trade_time TIMESTAMP NOT NULL,
                price REAL,
                volume INTEGER,
                amount REAL,
                commission REAL,
                stamp REAL,
                balance_after REAL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 持仓表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts_code TEXT NOT NULL,
                volume INTEGER NOT NULL,
                avg_price REAL NOT NULL,
                current_price REAL,
                market_value REAL,
                cost REAL,
                profit REAL,
                profit_rate REAL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(ts_code)
            )
        ''')
        
        self.conn.commit()
        data_logger.info(f"数据库初始化完成：{self.db_path}")
    
    def store_daily_data(self, df: pd.DataFrame, ts_code: str, 
                        overwrite: bool = False) -> bool:
        """
        存储日线数据
        
        Args:
            df: 日线数据 DataFrame
            ts_code: 股票代码
            overwrite: 是否覆盖现有数据
            
        Returns:
            是否存储成功
        """
        if df.empty:
            data_logger.warning(f"{ts_code} 日线数据为空，跳过存储")
            return False
        
        try:
            cursor = self.conn.cursor()
            
            for _, row in df.iterrows():
                try:
                    if overwrite:
                        cursor.execute('''
                            INSERT OR REPLACE INTO daily_data 
                            (ts_code, trade_date, open, high, low, close, vol, amount, pct_chg)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            ts_code,
                            row['trade_date'].strftime('%Y-%m-%d'),
                            row['open'], row['high'], row['low'], row['close'],
                            row['vol'], row['amount'], row['pct_chg']
                        ))
                    else:
                        cursor.execute('''
                            INSERT OR IGNORE INTO daily_data 
                            (ts_code, trade_date, open, high, low, close, vol, amount, pct_chg)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            ts_code,
                            row['trade_date'].strftime('%Y-%m-%d'),
                            row['open'], row['high'], row['low'], row['close'],
                            row['vol'], row['amount'], row['pct_chg']
                        ))
                except sqlite3.IntegrityError:
                    data_logger.warning(f"{ts_code} 数据已存在，跳过：{row['trade_date']}")
            
            self.conn.commit()
            data_logger.info(f"存储 {ts_code} 日线数据完成，共{len(df)}条")
            return True
            
        except Exception as e:
            data_logger.error(f"存储 {ts_code} 日线数据失败：{e}")
            self.conn.rollback()
            return False
    
    def get_daily_data(self, ts_code: str, start_date: str = None, 
                      end_date: str = None, days: int = None) -> Optional[pd.DataFrame]:
        """
        获取日线数据
        
        Args:
            ts_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            days: 获取最近 N 天
            
        Returns:
            DataFrame: 日线数据
        """
        query = "SELECT * FROM daily_data WHERE ts_code = ?"
        params = [ts_code]
        
        if days:
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            query += f" AND trade_date >= '{start_date}'"
        elif start_date:
            query += f" AND trade_date >= '{start_date}'"
            if end_date:
                query += f" AND trade_date <= '{end_date}'"
        
        query += " ORDER BY trade_date DESC"
        
        try:
            df = pd.read_sql_query(query, self.conn, params=params)
            if not df.empty:
                df['trade_date'] = pd.to_datetime(df['trade_date'])
                df.set_index('trade_date', inplace=True)
                data_logger.info(f"从数据库读取 {ts_code} 日线数据：{len(df)}条")
            return df
        except Exception as e:
            data_logger.error(f"读取 {ts_code} 日线数据失败：{e}")
            return None
    
    def store_indicators(self, df: pd.DataFrame, ts_code: str) -> bool:
        """
        存储技术指标数据
        
        Args:
            df: 指标数据 DataFrame
            ts_code: 股票代码
            
        Returns:
            是否存储成功
        """
        if df.empty:
            return False
        
        try:
            cursor = self.conn.cursor()
            
            for _, row in df.iterrows():
                cursor.execute('''
                    INSERT OR REPLACE INTO indicators 
                    (ts_code, trade_date, indicator_type, indicator_name, value, signal)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    ts_code,
                    row['trade_date'].strftime('%Y-%m-%d'),
                    row['indicator_type'],
                    row['indicator_name'],
                    row['value'],
                    row.get('signal', '')
                ))
            
            self.conn.commit()
            data_logger.info(f"存储 {ts_code} 指标数据完成")
            return True
            
        except Exception as e:
            data_logger.error(f"存储指标数据失败：{e}")
            self.conn.rollback()
            return False
    
    def get_indicators(self, ts_code: str, start_date: str = None,
                      end_date: str = None, indicator_types: List[str] = None) -> pd.DataFrame:
        """
        获取技术指标数据
        
        Args:
            ts_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            indicator_types: 指标类型列表
            
        Returns:
            DataFrame: 指标数据
        """
        query = "SELECT * FROM indicators WHERE ts_code = ?"
        params = [ts_code]
        
        if start_date:
            query += f" AND trade_date >= '{start_date}'"
            if end_date:
                query += f" AND trade_date <= '{end_date}'"
        
        if indicator_types:
            placeholders = ','.join(['?' for _ in indicator_types])
            query += f" AND indicator_type IN ({placeholders})"
            params.extend(indicator_types)
        
        query += " ORDER BY trade_date DESC"
        
        try:
            df = pd.read_sql_query(query, self.conn, params=params)
            if not df.empty:
                df['trade_date'] = pd.to_datetime(df['trade_date'])
            return df
        except Exception as e:
            data_logger.error(f"读取指标数据失败：{e}")
            return pd.DataFrame()
    
    def store_trade(self, trade: dict) -> bool:
        """
        存储交易记录
        
        Args:
            trade: 交易记录字典
            
        Returns:
            是否存储成功
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO trades 
                (ts_code, trade_type, trade_time, price, volume, amount, 
                 commission, stamp, balance_after, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trade['ts_code'],
                trade['type'],
                trade['time'],
                trade['price'],
                trade['volume'],
                trade['amount'],
                trade.get('commission', 0),
                trade.get('stamp', 0),
                trade['balance_after'],
                trade.get('notes', '')
            ))
            self.conn.commit()
            data_logger.info(f"存储交易记录：{trade['type']} {trade['ts_code']}")
            return True
        except Exception as e:
            data_logger.error(f"存储交易记录失败：{e}")
            self.conn.rollback()
            return False
    
    def get_positions(self) -> pd.DataFrame:
        """获取当前持仓"""
        try:
            df = pd.read_sql_query(
                "SELECT * FROM positions WHERE volume > 0 ORDER BY market_value DESC",
                self.conn
            )
            return df
        except Exception as e:
            data_logger.error(f"获取持仓失败：{e}")
            return pd.DataFrame()
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            data_logger.info("数据库连接已关闭")

# ==================== 缓存管理 ====================
class DataCache:
    """数据缓存管理器"""
    
    def __init__(self, cache_dir: str = None):
        self.cache_dir = Path(cache_dir or CACHE_DIR)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def save_cache(self, ts_code: str, data: pd.DataFrame, 
                  cache_type: str = "daily", expiry_seconds: int = 300) -> str:
        """
        保存缓存数据
        
        Args:
            ts_code: 股票代码
            data: DataFrame 数据
            cache_type: 缓存类型
            expiry_seconds: 缓存有效期（秒）
            
        Returns:
            缓存文件路径
        """
        filename = f"{ts_code}_{cache_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = self.cache_dir / filename
        
        try:
            data.to_csv(filepath, encoding='utf-8-sig')
            
            # 创建过期时间文件
            expire_file = self.cache_dir / f"{ts_code}_{cache_type}.expire"
            expire_file.write_text(str(datetime.now().timestamp() + expiry_seconds))
            
            data_logger.info(f"缓存数据：{filename}")
            return str(filepath)
        except Exception as e:
            data_logger.error(f"缓存数据失败：{e}")
            return None
    
    def load_cache(self, ts_code: str, cache_type: str = "daily") -> Optional[pd.DataFrame]:
        """
        加载缓存数据
        
        Args:
            ts_code: 股票代码
            cache_type: 缓存类型
            
        Returns:
            DataFrame 数据或 None
        """
        expire_file = self.cache_dir / f"{ts_code}_{cache_type}.expire"
        
        if not expire_file.exists():
            return None
        
        try:
            expire_time = int(expire_file.read_text())
            if datetime.now().timestamp() > expire_time:
                data_logger.info(f"缓存已过期：{expire_file}")
                return None
            
            # 查找最近的缓存文件
            cache_files = list(self.cache_dir.glob(f"{ts_code}_{cache_type}_*.csv"))
            if not cache_files:
                return None
            
            latest_file = max(cache_files, key=lambda x: x.stat().st_mtime)
            df = pd.read_csv(latest_file, parse_dates=['trade_date'], index_col='trade_date')
            data_logger.info(f"加载缓存数据：{latest_file.name}")
            return df
        except Exception as e:
            data_logger.error(f"加载缓存数据失败：{e}")
            return None
    
    def clear_old_cache(self, max_age_hours: int = 24):
        """清理过期的缓存文件"""
        import os
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
        
        deleted = 0
        for cache_file in self.cache_dir.glob("*.csv"):
            if cache_file.stat().st_mtime < cutoff_time:
                try:
                    cache_file.unlink()
                    deleted += 1
                except Exception as e:
                    data_logger.warning(f"删除缓存文件失败 {cache_file}: {e}")
        
        if deleted > 0:
            data_logger.info(f"清理过期缓存文件：{deleted}个")

# ==================== 单例模式 ====================
_db_instance = None
_cache_instance = None

def get_database() -> StockDatabase:
    """获取数据库实例"""
    global _db_instance
    if _db_instance is None:
        _db_instance = StockDatabase()
    return _db_instance

def get_cache() -> DataCache:
    """获取缓存实例"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = DataCache()
    return _cache_instance
