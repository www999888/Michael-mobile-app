"""
AI Stock Monitor - 技术指标分析模块
支持 MA, MACD, KDJ, RSI, BOLL 等技术指标
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
from config.settings import TECH_ANALYSIS_PARAMS
from config.logging_config import analyzer_logger

# ==================== 技术分析器类 ====================
class TechnicalAnalyzer:
    """技术指标分析器"""
    
    def __init__(self, params: Dict = None):
        """
        初始化技术分析器
        
        Args:
            params: 技术指标参数配置
        """
        self.params = params or TECH_ANALYSIS_PARAMS
        self.indicators_data = {}
    
    def calculate_ma(self, df: pd.DataFrame, 
                    periods: Dict[str, int] = None) -> pd.DataFrame:
        """
        计算移动平均线 (MA)
        
        Args:
            df: 价格数据 DataFrame
            periods: 周期配置
            
        Returns:
            DataFrame: 包含 MA 指标的数据
        """
        if periods is None:
            periods = self.params.get("MA", {})
        
        df = df.copy()
        
        for name, period in periods.items():
            col_name = f'ma_{name}'
            df[col_name] = df['close'].rolling(window=period).mean()
        
        analyzer_logger.info(f"计算 MA 指标完成：{periods}")
        return df
    
    def calculate_macd(self, df: pd.DataFrame, 
                      params: Dict = None) -> Tuple[pd.DataFrame, Dict]:
        """
        计算 MACD 指标
        
        Args:
            df: 价格数据 DataFrame
            params: MACD 参数配置
            
        Returns:
            DataFrame: 包含 MACD 指标的数据
            Dict: MACD 详细计算结果
        """
        if params is None:
            params = self.params.get("MACD", {})
        
        df = df.copy()
        fast_period = params.get('fast_period', 12)
        slow_period = params.get('slow_period', 26)
        signal_period = params.get('signal_period', 9)
        
        # 计算 EMA
        ema_fast = df['close'].ewm(span=fast_period, adjust=False).mean()
        ema_slow = df['close'].ewm(span=slow_period, adjust=False).mean()
        
        # 计算 MACD
        df['macd'] = ema_fast - ema_slow
        df['signal'] = df['macd'].ewm(span=signal_period, adjust=False).mean()
        df['histogram'] = df['macd'] - df['signal']
        
        result = {
            'fast_ema': fast_period,
            'slow_ema': slow_period,
            'signal_period': signal_period
        }
        
        analyzer_logger.info(f"计算 MACD 指标完成")
        return df, result
    
    def calculate_kdj(self, df: pd.DataFrame,
                     params: Dict = None) -> pd.DataFrame:
        """
        计算 KDJ 指标
        
        Args:
            df: 价格数据 DataFrame
            params: KDJ 参数配置
            
        Returns:
            DataFrame: 包含 KDJ 指标的数据
        """
        if params is None:
            params = self.params.get("KDJ", {})
        
        df = df.copy()
        n = params.get('n_period', 9)
        m1 = params.get('m1_period', 3)
        m2 = params.get('m2_period', 3)
        
        # 计算 RSV
        lowest_low = df['low'].rolling(window=n).min()
        highest_high = df['high'].rolling(window=n).max()
        
        rsv = (df['close'] - lowest_low) / (highest_high - lowest_low) * 100
        df['kdj_k'] = rsv.ewm(span=m1, adjust=False).mean()
        df['kdj_d'] = df['kdj_k'].ewm(span=m2, adjust=False).mean()
        df['kdj_j'] = 3 * df['kdj_k'] - 2 * df['kdj_d']
        
        analyzer_logger.info(f"计算 KDJ 指标完成")
        return df
    
    def calculate_rsi(self, df: pd.DataFrame,
                     params: Dict = None) -> pd.DataFrame:
        """
        计算 RSI 指标
        
        Args:
            df: 价格数据 DataFrame
            params: RSI 参数配置
            
        Returns:
            DataFrame: 包含 RSI 指标的数据
        """
        if params is None:
            params = self.params.get("RSI", {})
        
        df = df.copy()
        short_period = params.get('short_period', 6)
        long_period = params.get('long_period', 12)
        
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=short_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=short_period).mean()
        
        rs = gain / loss
        df['rsi_short'] = 100 - (100 / (1 + rs))
        
        loss_long = (-delta.where(delta < 0, 0)).rolling(window=long_period).mean()
        rs_long = gain / loss_long
        df['rsi_long'] = 100 - (100 / (1 + rs_long))
        
        analyzer_logger.info(f"计算 RSI 指标完成")
        return df
    
    def calculate_boll(self, df: pd.DataFrame,
                      params: Dict = None) -> pd.DataFrame:
        """
        计算布林带 (BOLL) 指标
        
        Args:
            df: 价格数据 DataFrame
            params: BOLL 参数配置
            
        Returns:
            DataFrame: 包含 BOLL 指标的数据
        """
        if params is None:
            params = self.params.get("BOLL", {})
        
        df = df.copy()
        period = params.get('period', 20)
        mult = params.get('mult', 2.0)
        
        # 计算中轨
        df['boll_mid'] = df['close'].rolling(window=period).mean()
        
        # 计算标准差
        std = df['close'].rolling(window=period).std()
        
        # 计算上下轨
        df['boll_upper'] = df['boll_mid'] + (std * mult)
        df['boll_lower'] = df['boll_mid'] - (std * mult)
        
        # 带宽和百分比位置
        df['boll_bandwidth'] = (df['boll_upper'] - df['boll_lower']) / df['boll_mid'] * 100
        df['boll_percent'] = (df['close'] - df['boll_lower']) / (df['boll_upper'] - df['boll_lower']) * 100
        
        analyzer_logger.info(f"计算 BOLL 指标完成")
        return df
    
    def calculate_all_indicators(self, df: pd.DataFrame,
                                include_macd: bool = True,
                                include_kdj: bool = True,
                                include_rsi: bool = True,
                                include_boll: bool = True) -> pd.DataFrame:
        """
        计算所有技术指标
        
        Args:
            df: 价格数据 DataFrame
            include_macd: 是否计算 MACD
            include_kdj: 是否计算 KDJ
            include_rsi: 是否计算 RSI
            include_boll: 是否计算 BOLL
            
        Returns:
            DataFrame: 包含所有指标的数据
        """
        analyzer_logger.info("开始计算所有技术指标")
        
        # 计算 MA
        df = self.calculate_ma(df)
        
        if include_macd:
            df, _ = self.calculate_macd(df)
        if include_kdj:
            df = self.calculate_kdj(df)
        if include_rsi:
            df = self.calculate_rsi(df)
        if include_boll:
            df = self.calculate_boll(df)
        
        # 移除 NaN 值
        df = df.dropna()
        
        return df
    
    def get_signal(self, df: pd.DataFrame, ts_code: str,
                  ma_threshold: float = 0.02,
                  rsi_oversold: float = 30.0,
                  rsi_overbought: float = 70.0) -> Dict:
        """
        生成交易信号
        
        Args:
            df: 包含指标的数据
            ts_code: 股票代码
            ma_threshold: MA 趋势判断阈值
            rsi_oversold: RSI 超卖阈值
            rsi_overbought: RSI 超买阈值
            
        Returns:
            Dict: 交易信号和状态
        """
        if df.empty:
            return {"error": "数据为空", "ts_code": ts_code}
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        signals = []
        score = 0  # -10 到 10，负数偏空，正数偏多
        
        # MA 信号
        if 'ma_short' in latest and 'ma_medium' in latest:
            if latest['ma_short'] > latest['ma_medium']:
                signals.append("MA 金叉 - 多头信号")
                score += 2
            elif latest['ma_short'] < latest['ma_medium']:
                signals.append("MA 死叉 - 空头信号")
                score -= 2
        
        # MACD 信号
        if 'macd' in latest:
            if latest['macd'] > 0 and latest['macd'] > latest['signal']:
                signals.append("MACD 多头 - 上涨趋势")
                score += 2
            elif latest['macd'] < 0 and latest['macd'] < latest['signal']:
                signals.append("MACD 空头 - 下跌趋势")
                score -= 2
        
        # KDJ 信号
        if 'kdj_k' in latest:
            if latest['kdj_k'] < 20 and latest['kdj_k'] > latest['kdj_d']:
                signals.append("KDJ 超卖金叉 - 买入信号")
                score += 2
            elif latest['kdj_k'] > 80 and latest['kdj_k'] < latest['kdj_d']:
                signals.append("KDJ 超卖死叉 - 卖出信号")
                score -= 2
        
        # RSI 信号
        if 'rsi_short' in latest:
            if latest['rsi_short'] < rsi_oversold:
                signals.append("RSI 超卖 - 可能反弹")
                score += 1
            elif latest['rsi_short'] > rsi_overbought:
                signals.append("RSI 超买 - 可能回调")
                score -= 1
        
        # BOLL 信号
        if 'boll_percent' in latest:
            if latest['boll_percent'] < 0.1:
                signals.append("BOLL 触及下轨 - 支撑位")
                score += 1
            elif latest['boll_percent'] > 0.9:
                signals.append("BOLL 触及上轨 - 压力位")
                score -= 1
        
        # 综合判断
        overall_signal = "观望"
        if score >= 5:
            overall_signal = "强烈买入"
        elif score >= 2:
            overall_signal = "买入"
        elif score <= -5:
            overall_signal = "强烈卖出"
        elif score <= -2:
            overall_signal = "卖出"
        elif score >= 0:
            overall_signal = "持有"
        
        result = {
            "ts_code": ts_code,
            "timestamp": pd.Timestamp.now(),
            "overall_signal": overall_signal,
            "score": score,
            "signals": signals,
            "latest_price": float(latest['close']),
            "indicators": {
                "ma_status": self._get_ma_status(df) if 'ma_short' in latest else None,
                "macd_status": self._get_macd_status(latest, prev) if 'macd' in latest else None,
                "kdj_status": self._get_kdj_status(latest) if 'kdj_k' in latest else None,
                "rsi_status": self._get_rsi_status(latest) if 'rsi_short' in latest else None,
                "boll_status": self._get_boll_status(latest) if 'boll_percent' in latest else None
            }
        }
        
        analyzer_logger.info(f"生成交易信号：{ts_code} -> {overall_signal}")
        return result
    
    def _get_ma_status(self, df: pd.DataFrame) -> Dict:
        """获取 MA 状态"""
        latest = df.iloc[-1]
        return {
            "short_vs_medium": "金叉" if latest['ma_short'] > latest['ma_medium'] else "死叉",
            "medium_vs_long": "金叉" if latest['ma_medium'] > latest['ma_long'] else "死叉"
        }
    
    def _get_macd_status(self, latest: pd.Series, prev: pd.Series) -> Dict:
        """获取 MACD 状态"""
        return {
            "macd_signal": "金叉" if (latest['macd'] > 0 and latest['macd'] > latest['signal']) else 
                          "死叉" if (latest['macd'] < 0 and latest['macd'] < latest['signal']) else "盘整",
            "histogram": float(latest['histogram'])
        }
    
    def _get_kdj_status(self, latest: pd.Series) -> Dict:
        """获取 KDJ 状态"""
        return {
            "kdj_k": float(latest['kdj_k']),
            "kdj_d": float(latest['kdj_d']),
            "kdj_j": float(latest['kdj_j']),
            "state": "超卖" if latest['kdj_k'] < 20 else 
                    "超买" if latest['kdj_k'] > 80 else "中性"
        }
    
    def _get_rsi_status(self, latest: pd.Series) -> Dict:
        """获取 RSI 状态"""
        return {
            "rsi_short": float(latest['rsi_short']),
            "rsi_long": float(latest['rsi_long']),
            "state": "超卖" if latest['rsi_short'] < 30 else 
                    "超买" if latest['rsi_short'] > 70 else "中性"
        }
    
    def _get_boll_status(self, latest: pd.Series) -> Dict:
        """获取 BOLL 状态"""
        return {
            "boll_percent": float(latest['boll_percent']),
            "bandwidth": float(latest['boll_bandwidth']),
            "position": "下轨" if latest['boll_percent'] < 0.1 else 
                       "上轨" if latest['boll_percent'] > 0.9 else "中轨附近",
            "width_state": "收缩" if latest['boll_bandwidth'] < 5 else "扩张"
        }

# ==================== 单例模式 ====================
_analyzer_instance = None

def get_analyzer() -> TechnicalAnalyzer:
    """获取技术分析器实例"""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = TechnicalAnalyzer()
    return _analyzer_instance
