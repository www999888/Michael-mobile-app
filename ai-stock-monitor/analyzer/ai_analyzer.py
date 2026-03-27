"""
AI 分析模块
使用 Ollama 本地大模型进行智能分析
"""

import requests
import json
from typing import Dict, List, Optional
from datetime import datetime
from config import OLLAMA_BASE_URL, DEFAULT_MODEL, logger

class AIAnalyzer:
    """AI 分析器 - 使用 Ollama 本地大模型"""
    
    def __init__(self, model: str = None):
        self.model = model or DEFAULT_MODEL
        self.base_url = OLLAMA_BASE_URL
        self.session = requests.Session()
    
    def _check_ollama_available(self) -> bool:
        """检查 Ollama 是否可用"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def analyze_stock(self, stock_code: str, analysis: Dict) -> Dict:
        """
        AI 分析股票
        返回：AI 的分析报告和建议
        """
        if not self._check_ollama_available():
            return {
                "stock_code": stock_code,
                "ai_analysis": "⚠️ Ollama 服务不可用，请确保 Ollama 已启动",
                "recommendation": "UNKNOWN",
                "confidence": 0.0
            }
        
        # 构建分析提示
        prompt = self._build_analysis_prompt(stock_code, analysis)
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            ai_response = result.get("response", "")
            
            # 解析 AI 回复
            return {
                "stock_code": stock_code,
                "ai_analysis": ai_response,
                "recommendation": self._extract_recommendation(ai_response),
                "confidence": self._calculate_confidence(ai_response),
                "model": self.model,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"AI 分析失败 {stock_code}: {e}")
            return {
                "stock_code": stock_code,
                "ai_analysis": f"❌ AI 分析失败：{str(e)}",
                "recommendation": "UNKNOWN",
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _build_analysis_prompt(self, stock_code: str, analysis: Dict) -> str:
        """构建分析提示词"""
        latest = analysis.get("latest", {})
        current_price = latest.get("current_price", 0)
        
        # 构建技术指标摘要
        tech_summary = ""
        if latest.get("MACD"):
            macd = latest["MACD"]
            tech_summary += f"- MACD: {macd.get('macd', 0):.4f} vs Signal: {macd.get('signal', 0):.4f}\n"
        
        if latest.get("KDJ"):
            kdj = latest["KDJ"]
            tech_summary += f"- KDJ: K={kdj.get('k', 0):.2f} D={kdj.get('d', 0):.2f} J={kdj.get('j', 0):.2f}\n"
        
        if latest.get("RSI"):
            rsi = latest["RSI"]
            tech_summary += f"- RSI(6): {rsi.get('RSI6', 0):.2f}\n"
        
        if latest.get("BOLL"):
            boll = latest["BOLL"]
            tech_summary += f"- BOLL: Upper={boll.get('upper', 0):.2f} Middle={boll.get('middle', 0):.2f} Lower={boll.get('lower', 0):.2f}\n"
        
        # 构建完整提示
        return f"""你是一位专业的股票分析师，请根据以下技术分析数据，对{stock_code}进行智能分析：

当前股价：{current_price:.2f}元

技术指标：
{tech_summary}

请分析：
1. 当前市场状态和趋势
2. 主要技术信号的含义
3. 给出明确的交易建议（买入/卖出/持有）
4. 说明理由和风险提示

要求：
- 分析简明扼要，不超过 200 字
- 给出明确的交易建议：BUY（买入）、SELL（卖出）或 HOLD（持有）
- 用中文回答
- 直接输出分析内容，不需要其他开场白"""
    
    def _extract_recommendation(self, text: str) -> str:
        """从 AI 回复中提取交易建议"""
        if "BUY" in text.upper() and "买入" in text:
            return "BUY"
        elif "SELL" in text.upper() and "卖出" in text:
            return "SELL"
        elif "HOLD" in text.upper() or "持有" in text or "观望" in text:
            return "HOLD"
        else:
            return "HOLD"
    
    def _calculate_confidence(self, text: str) -> float:
        """计算 AI 建议的置信度"""
        # 简单规则：根据文本长度和明确程度
        if len(text) > 50:
            return 0.7
        elif len(text) > 30:
            return 0.5
        else:
            return 0.3
