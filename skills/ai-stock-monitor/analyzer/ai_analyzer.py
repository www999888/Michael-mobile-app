"""
AI Stock Monitor - AI 分析模块
集成 Ollama 本地大模型进行智能分析
"""
import requests
import json
from typing import Dict, Optional, List
from datetime import datetime
from config.settings import OLLAMA_BASE_URL, OLLAMA_MODEL, SUPPORTED_ARCHITECTURES
from config.logging_config import analyzer_logger
import pandas as pd

# ==================== Ollama AI 分析器类 ====================
class OllamaAnalyzer:
    """Ollama 本地 AI 分析器"""
    
    def __init__(self, base_url: str = None, model: str = None):
        """
        初始化 Ollama 分析器
        
        Args:
            base_url: Ollama 服务地址
            model: 使用的模型名称
        """
        self.base_url = base_url or OLLAMA_BASE_URL
        self.model = model or OLLAMA_MODEL
        self.api_url = f"{self.base_url}/api/generate"
        
        # 系统提示词
        self.system_prompt = """你是一位资深的股票分析师，精通技术分析、基本面分析和市场趋势研判。
请根据提供的股票数据和技术指标，给出专业、客观的分析建议。

分析要点：
1. 趋势判断 - 基于 MA、BOLL 等指标判断趋势方向
2. 动能分析 - 基于 MACD、RSI 等指标分析动能强弱
3. 买卖点建议 - 结合 KDJ 等指标给出具体买卖点
4. 风险评估 - 评估波动率和潜在风险
5. 操作建议 - 给出明确的买入/卖出/持有建议

请保持分析专业、客观，避免过度推测。
注意：所有分析基于历史数据，不构成投资建议，投资有风险。"""

    def _check_model_available(self) -> bool:
        """检查模型是否可用"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m['name'] for m in models]
                if self.model in model_names:
                    analyzer_logger.info(f"模型 {self.model} 已加载，版本：{self.model}")
                    return True
                else:
                    analyzer_logger.warning(f"模型 {self.model} 未找到，可用模型：{model_names}")
                    return False
            else:
                analyzer_logger.error(f"Ollama API 响应状态码：{response.status_code}")
                return False
        except Exception as e:
            analyzer_logger.error(f"检查 Ollama 模型失败：{e}")
            return False

    def _build_analysis_prompt(self, ts_code: str, df: pd.DataFrame,
                              signals: Dict, market_data: Dict = None) -> str:
        """
        构建 AI 分析提示词
        
        Args:
            ts_code: 股票代码
            df: 技术指标数据
            signals: 技术分析信号
            market_data: 市场数据
            
        Returns:
            提示词字符串
        """
        # 提取最新数据
        latest = df.iloc[-1]
        recent = df.tail(5)
        
        price_trend = "上涨" if latest['close'] > recent['close'].iloc[-1] else "下跌"
        price_change = ((latest['close'] - recent['close'].iloc[-1]) / recent['close'].iloc[-1] * 100)
        
        prompt = f"""
## 股票信息
- 代码：{ts_code}
- 当前价格：{latest['close']:.2f} 元
- 近期趋势：{price_trend} ({price_change:+.2f}%)

## 技术指标状态

### 移动平均线 (MA)
- 短期均线 (5 日): {latest.get('ma_short', 'N/A'):.2f}
- 中期均线 (10 日): {latest.get('ma_medium', 'N/A'):.2f}
- 长期均线 (20 日): {latest.get('ma_long', 'N/A'):.2f}

### MACD
- MACD: {latest.get('macd', 'N/A'):.4f}
- Signal: {latest.get('signal', 'N/A'):.4f}
- Histogram: {latest.get('histogram', 'N/A'):.4f}

### KDJ
- K: {latest.get('kdj_k', 'N/A'):.2f}
- D: {latest.get('kdj_d', 'N/A'):.2f}
- J: {latest.get('kdj_j', 'N/A'):.2f}

### RSI
- RSI(6): {latest.get('rsi_short', 'N/A'):.2f}
- RSI(12): {latest.get('rsi_long', 'N/A'):.2f}

### 布林带 (BOLL)
- 上轨：{latest.get('boll_upper', 'N/A'):.2f}
- 中轨：{latest.get('boll_mid', 'N/A'):.2f}
- 下轨：{latest.get('boll_lower', 'N/A'):.2f}
- 位置：%{latest.get('boll_percent', 'N/A'):.1f}

## 技术分析总结
- 综合信号：{signals.get('overall_signal', '无信号')}
- 得分：{signals.get('score', 0)} (范围 -10 到 10)
- 关键信号：
{chr(10).join(['  - ' + s for s in signals.get('signals', [])]) if signals.get('signals') else '  - 无明显信号'}
"""
        return prompt

    def analyze(self, ts_code: str, df: pd.DataFrame,
               signals: Dict = None, max_tokens: int = 500) -> Optional[Dict]:
        """
        调用 Ollama 进行 AI 分析
        
        Args:
            ts_code: 股票代码
            df: 技术指标数据 DataFrame
            signals: 技术分析信号
            max_tokens: 最大生成长度
            
        Returns:
            AI 分析结果
        """
        if df.empty:
            return {"error": "数据为空", "ts_code": ts_code}
        
        # 检查模型可用性
        if not self._check_model_available():
            return {"error": "Ollama 模型不可用", "ts_code": ts_code}
        
        # 构建提示词
        prompt = self._build_analysis_prompt(ts_code, df, signals or {})
        
        full_prompt = f"""{self.system_prompt}

## 当前分析任务

{prompt}

请根据以上数据，给出专业的股票分析和建议。"""

        try:
            # 调用 Ollama API
            payload = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": max_tokens
                }
            }
            
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            analysis_text = result.get('response', '')
            
            # 结构化分析结果
            analysis_result = {
                "ts_code": ts_code,
                "timestamp": datetime.now().isoformat(),
                "model": self.model,
                "raw_analysis": analysis_text,
                "status": "success"
            }
            
            analyzer_logger.info(f"AI 分析完成：{ts_code}")
            return analysis_result
            
        except requests.exceptions.Timeout:
            analyzer_logger.error(f"AI 分析超时：{ts_code}")
            return {"error": "AI 分析超时", "ts_code": ts_code}
        except Exception as e:
            analyzer_logger.error(f"AI 分析失败：{e}")
            return {"error": f"AI 分析失败：{str(e)}", "ts_code": ts_code}
    
    def analyze_rapid(self, ts_code: str, df: pd.DataFrame,
                     signals: Dict = None) -> Optional[Dict]:
        """
        快速 AI 分析（简化版）
        
        Args:
            ts_code: 股票代码
            df: 技术指标数据
            signals: 技术分析信号
            
        Returns:
            快速分析结果
        """
        if df.empty:
            return None
        
        latest = df.iloc[-1]
        
        # 基于技术信号的快速判断
        score = signals.get('score', 0) if signals else 0
        overall_signal = signals.get('overall_signal', '观望') if signals else '观望'
        
        # 构建简化的 AI 分析
        if score >= 5:
            ai_advice = "强烈推荐买入，各项技术指标显示强劲上涨信号"
        elif score >= 2:
            ai_advice = "建议买入，技术指标偏多"
        elif score <= -5:
            ai_advice = "强烈建议卖出，技术指标显示下跌风险"
        elif score <= -2:
            ai_advice = "建议卖出，注意下跌风险"
        else:
            ai_advice = "建议观望，等待更明确的信号"
        
        return {
            "ts_code": ts_code,
            "timestamp": datetime.now().isoformat(),
            "model": self.model,
            "ai_advice": ai_advice,
            "confidence": abs(score) / 10,
            "status": "quick"
        }
    
    def generate_trading_plan(self, ts_code: str, df: pd.DataFrame,
                             current_price: float,
                             current_position: float = 0) -> Dict:
        """
        生成交易计划
        
        Args:
            ts_code: 股票代码
            df: 技术指标数据
            current_price: 当前价格
            current_position: 当前持仓
            
        Returns:
            交易计划
        """
        if df.empty:
            return {"error": "数据不足", "ts_code": ts_code}
        
        latest = df.iloc[-1]
        
        # AI 决策逻辑
        should_buy = False
        should_sell = False
        action = "持有"
        
        # 买入条件
        if current_position == 0:
            if latest.get('rsi_short', 50) < 30 and latest.get('kdj_k', 50) < 30:
                should_buy = True
                action = "买入"
        
        # 卖出条件
        if current_position > 0:
            if latest.get('rsi_short', 50) > 70 or latest.get('kdj_k', 50) > 80:
                should_sell = True
                action = "卖出"
            elif latest['close'] < latest.get('boll_lower', latest['close']):
                should_sell = True
                action = "止损卖出"
        
        # 加仓条件
        if current_position > 0 and should_buy:
            if latest.get('kdj_k', 50) > latest.get('kdj_d', 50):
                action = "加仓"
        
        trading_plan = {
            "ts_code": ts_code,
            "timestamp": datetime.now().isoformat(),
            "current_price": current_price,
            "current_position": current_position,
            "signal": {
                "action": action,
                "should_buy": should_buy,
                "should_sell": should_sell,
                "confidence": abs(latest.get('rsi_short', 50) - latest.get('kdj_k', 50)) / 100
            },
            "price_targets": {
                "resistance": float(latest.get('boll_upper', current_price * 1.05)),
                "support": float(latest.get('boll_lower', current_price * 0.95)),
                "stop_loss": float(latest.get('boll_lower', current_price * 0.93))
            }
        }
        
        analyzer_logger.info(f"生成交易计划：{ts_code} -> {action}")
        return trading_plan

# ==================== 单例模式 ====================
_ai_analyzer_instance = None

def get_ai_analyzer() -> OllamaAnalyzer:
    """获取 AI 分析器实例"""
    global _ai_analyzer_instance
    if _ai_analyzer_instance is None:
        _ai_analyzer_instance = OllamaAnalyzer()
    return _ai_analyzer_instance
