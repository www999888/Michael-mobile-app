"""
技术指标分析模块
计算 MA、MACD、KDJ、RSI、BOLL 等技术指标
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from config import TECH_INDICATOR_PARAMS, logger

class TechAnalyzer:
    """技术指标分析器"""
    
    @staticmethod
    def calculate_ma(df: pd.DataFrame, periods: List[int] = [5, 10, 20, 60]) -> Dict[str, pd.Series]:
        """计算移动平均线"""
        ma_data = {}
        for period in periods:
            ma_name = f"MA{period}"
            ma_data[ma_name] = df["close"].rolling(window=period).mean()
        return ma_data
    
    @staticmethod
    def calculate_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
        """计算 MACD 指标"""
        exp1 = df["close"].ewm(span=fast, adjust=False).mean()
        exp2 = df["close"].ewm(span=slow, adjust=False).mean()
        
        macd_line = exp1 - exp2
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return {
            "macd": macd_line,
            "signal": signal_line,
            "histogram": histogram
        }
    
    @staticmethod
    def calculate_kdj(df: pd.DataFrame, period: int = 9, smooth: int = 3) -> Dict:
        """计算 KDJ 指标"""
        low_min = df["low"].rolling(window=period).min()
        high_max = df["high"].rolling(window=period).max()
        
        rsv = (df["close"] - low_min) / (high_max - low_min) * 100
        k = rsv.ewm(ignore_na=False, alpha=1/smooth, min_periods=period).mean()
        d = k.ewm(ignore_na=False, alpha=1/smooth, min_periods=period).mean()
        j = 3 * k - 2 * d
        
        return {
            "k": k,
            "d": d,
            "j": j
        }
    
    @staticmethod
    def calculate_rsi(df: pd.DataFrame, periods: List[int] = [6, 12, 24]) -> Dict[str, pd.Series]:
        """计算 RSI 指标"""
        rsi_data = {}
        for period in periods:
            delta = df["close"].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            rs = gain / loss if loss.any() else pd.Series(0)
            rsi_data[f"RSI{period}"] = 100 - (100 / (1 + rs))
        
        return rsi_data
    
    @staticmethod
    def calculate_boll(df: pd.DataFrame, period: int = 20, std_dev: float = 2) -> Dict:
        """计算布林带"""
        middle = df["close"].rolling(window=period).mean()
        std = df["close"].rolling(window=period).std()
        
        upper = middle + std_dev * std
        lower = middle - std_dev * std
        
        return {
            "upper": upper,
            "middle": middle,
            "lower": lower,
            "width": (upper - lower) / middle * 100,
            "percent_b": (df["close"] - lower) / (upper - lower)
        }
    
    @staticmethod
    def analyze_stock(stock_code: str, df: pd.DataFrame) -> Dict:
        """综合分析一只股票的技术指标"""
        try:
            analysis = {
                "stock_code": stock_code,
                "current_price": float(df["close"].iloc[-1]),
                "timestamp": df.index[-1],
                "indicators": {}
            }
            
            # 计算所有指标
            analysis["indicators"]["MA"] = TechAnalyzer.calculate_ma(df)
            analysis["indicators"]["MACD"] = TechAnalyzer.calculate_macd(df)
            analysis["indicators"]["KDJ"] = TechAnalyzer.calculate_kdj(df)
            analysis["indicators"]["RSI"] = TechAnalyzer.calculate_rsi(df)
            analysis["indicators"]["BOLL"] = TechAnalyzer.calculate_boll(df)
            
            # 获取最新值
            latest = {}
            for indicator_type, indicator_data in analysis["indicators"].items():
                latest[indicator_type] = {}
                if isinstance(indicator_data, dict):
                    for key, value in indicator_data.items():
                        if hasattr(value, 'iloc'):
                            latest[indicator_type][key] = float(value.iloc[-1]) if not pd.isna(value.iloc[-1]) else None
                        else:
                            latest[indicator_type][key] = value
                else:
                    latest[indicator_type] = float(indicator_data.iloc[-1]) if hasattr(indicator_data, 'iloc') else None
            
            analysis["latest"] = latest
            
            return analysis
            
        except Exception as e:
            logger.error(f"技术分析失败 {stock_code}: {e}")
            return {
                "stock_code": stock_code,
                "error": str(e)
            }
    
    @staticmethod
    def get_trade_signals(analysis: Dict) -> Dict:
        """根据技术指标生成交易信号"""
        signals = {
            "stock_code": analysis.get("stock_code"),
            "signals": [],
            "overall_signal": "HOLD"
        }
        
        latest = analysis.get("latest", {})
        indicators = analysis.get("indicators", {})
        
        # MACD 信号
        macd = latest.get("MACD", {})
        if macd.get("macd") and macd.get("signal"):
            if macd["macd"] > macd["signal"]:
                signals["signals"].append({"type": "MACD_GOLDEN", "strength": "BUY"})
            elif macd["macd"] < macd["signal"]:
                signals["signals"].append({"type": "MACD_DEATH", "strength": "SELL"})
        
        # KDJ 信号
        kdj = latest.get("KDJ", {})
        if kdj.get("k") and kdj.get("d"):
            if kdj["k"] < 20 and kdj["k"] < kdj["d"]:
                signals["signals"].append({"type": "KDJ_OVERSOLD", "strength": "BUY"})
            elif kdj["k"] > 80 and kdj["k"] > kdj["d"]:
                signals["signals"].append({"type": "KDJ_OVERBOUGHT", "strength": "SELL"})
        
        # RSI 信号
        rsi = latest.get("RSI", {})
        if rsi.get("RSI6"):
            if rsi["RSI6"] > 70:
                signals["signals"].append({"type": "RSI_OVERBOUGHT", "strength": "SELL"})
            elif rsi["RSI6"] < 30:
                signals["signals"].append({"type": "RSI_OVERSOLD", "strength": "BUY"})
        
        # BOLL 信号
        boll = latest.get("BOLL", {})
        if boll.get("current_price") and boll.get("lower"):
            if boll["current_price"] < boll["lower"]:
                signals["signals"].append({"type": "BOLL_BREAKDOWN", "strength": "BUY"})
            elif boll["current_price"] > boll["upper"]:
                signals["signals"].append({"type": "BOLL_BREAKOUT", "strength": "SELL"})
        
        # 综合信号
        buy_count = sum(1 for s in signals["signals"] if s["strength"] == "BUY")
        sell_count = sum(1 for s in signals["signals"] if s["strength"] == "SELL")
        
        if buy_count > sell_count:
            signals["overall_signal"] = "BUY"
        elif sell_count > buy_count:
            signals["overall_signal"] = "SELL"
        
        return signals
