"""
模拟交易模块
模拟买入、卖出、持仓管理、盈亏计算
"""

from typing import Dict, List
from datetime import datetime
from config import SIM_TRADING, logger

class SimTrader:
    """模拟交易者"""
    
    def __init__(self, initial_capital: float = None):
        self.capital = initial_capital or SIM_TRADING["initial_capital"]
        self.positions = {}  # stock_code -> {"shares": int, "avg_price": float}
        self.trade_history = []
        self.initial_capital = initial_capital or SIM_TRADING["initial_capital"]
    
    def buy(self, stock_code: str, price: float, shares: int) -> Dict:
        """
        买入股票
        返回：交易结果
        """
        if shares * price > self.capital * SIM_TRADING["max_position_pct"]:
            return {
                "success": False,
                "error": "超过最大持仓限制"
            }
        
        if shares * price > self.capital:
            return {
                "success": False,
                "error": "资金不足"
            }
        
        # 更新持仓
        if stock_code in self.positions:
            old_shares = self.positions[stock_code]["shares"]
            old_avg_price = self.positions[stock_code]["avg_price"]
            new_avg_price = (old_shares * old_avg_price + shares * price) / (old_shares + shares)
            self.positions[stock_code]["shares"] = old_shares + shares
            self.positions[stock_code]["avg_price"] = new_avg_price
        else:
            self.positions[stock_code] = {
                "shares": shares,
                "avg_price": price
            }
        
        # 扣除资金
        total_cost = shares * price
        self.capital -= total_cost
        
        # 记录交易
        trade = {
            "type": "BUY",
            "stock_code": stock_code,
            "shares": shares,
            "price": price,
            "total_cost": total_cost,
            "timestamp": datetime.now().isoformat()
        }
        self.trade_history.append(trade)
        
        logger.info(f"买入 {stock_code}: {shares}股 @ {price:.2f}元")
        
        return {
            "success": True,
            "trade": trade,
            "remaining_capital": self.capital
        }
    
    def sell(self, stock_code: str, price: float, shares: int) -> Dict:
        """
        卖出股票
        返回：交易结果
        """
        if stock_code not in self.positions:
            return {
                "success": False,
                "error": "无持仓"
            }
        
        current_shares = self.positions[stock_code]["shares"]
        if shares > current_shares:
            return {
                "success": False,
                "error": f"持仓不足，当前持有{current_shares}股"
            }
        
        # 更新持仓
        if shares == current_shares:
            del self.positions[stock_code]
        else:
            self.positions[stock_code]["shares"] -= shares
        
        # 增加资金
        total_revenue = shares * price
        self.capital += total_revenue
        
        # 计算盈亏
        avg_price = self.positions[stock_code].get("avg_price", price) if current_shares > 0 else price
        profit = (price - avg_price) * shares
        profit_pct = (profit / (avg_price * shares)) * 100 if avg_price > 0 else 0
        
        # 记录交易
        trade = {
            "type": "SELL",
            "stock_code": stock_code,
            "shares": shares,
            "price": price,
            "total_revenue": total_revenue,
            "profit": profit,
            "profit_pct": profit_pct,
            "timestamp": datetime.now().isoformat()
        }
        self.trade_history.append(trade)
        
        logger.info(f"卖出 {stock_code}: {shares}股 @ {price:.2f}元，盈亏：{profit:.2f}元 ({profit_pct:.2f}%)")
        
        return {
            "success": True,
            "trade": trade,
            "remaining_capital": self.capital,
            "profit": profit,
            "profit_pct": profit_pct
        }
    
    def get_positions(self) -> Dict:
        """获取当前持仓"""
        return self.positions.copy()
    
    def get_portfolio_value(self, stock_prices: Dict[str, float]) -> Dict:
        """
        获取组合价值
        :param stock_prices: 当前股票价格字典 {stock_code: price}
        """
        holdings_value = 0
        for stock_code, position in self.positions.items():
            price = stock_prices.get(stock_code, 0)
            holdings_value += price * position["shares"]
        
        total_value = self.capital + holdings_value
        total_profit = total_value - self.initial_capital
        profit_pct = (total_profit / self.initial_capital) * 100 if self.initial_capital > 0 else 0
        
        return {
            "cash": self.capital,
            "holdings_value": holdings_value,
            "total_value": total_value,
            "total_profit": total_profit,
            "profit_pct": profit_pct,
            "positions": self.positions,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_trade_report(self) -> List[Dict]:
        """获取交易报告"""
        return self.trade_history.copy()
    
    def get_performance_summary(self) -> Dict:
        """获取业绩摘要"""
        total_trades = len(self.trade_history)
        buy_trades = [t for t in self.trade_history if t["type"] == "BUY"]
        sell_trades = [t for t in self.trade_history if t["type"] == "SELL"]
        
        total_profit = sum(t.get("profit", 0) for t in sell_trades)
        profitable_trades = sum(1 for t in sell_trades if t.get("profit", 0) > 0)
        win_rate = (profitable_trades / len(sell_trades) * 100) if sell_trades else 0
        
        return {
            "total_trades": total_trades,
            "buy_count": len(buy_trades),
            "sell_count": len(sell_trades),
            "total_profit": total_profit,
            "win_rate": win_rate,
            "capital": self.capital,
            "initial_capital": self.initial_capital,
            "return_pct": ((self.capital - self.initial_capital) / self.initial_capital * 100) if self.initial_capital > 0 else 0
        }
    
    def clear(self):
        """清空所有数据"""
        self.capital = self.initial_capital
        self.positions.clear()
        self.trade_history.clear()
        logger.info("模拟账户已重置")
