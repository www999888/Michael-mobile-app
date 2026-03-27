"""
AI Stock Monitor - 模拟交易模块
虚拟资金模拟买卖，盈亏计算
"""
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
from data.data_storage import get_database
from config.settings import SIM_TRADING
from config.logging_config import trader_logger

# ==================== 模拟交易器类 ====================
class SimulatedTrader:
    """模拟交易器"""
    
    def __init__(self, initial_capital: float = None, commission_rate: float = None):
        """
        初始化模拟交易器
        
        Args:
            initial_capital: 初始资金
            commission_rate: 佣金费率
        """
        self.db = get_database()
        self.initial_capital = initial_capital or SIM_TRADING['initial_capital']
        self.commission_rate = commission_rate or SIM_TRADING['commission_rate']
        self.stamp_rate = SIM_TRADING['stamp_rate']
        self.min_shares = SIM_TRADING['min_shares']
        self.max_position_ratio = SIM_TRADING['max_position_ratio']
        
        self.capital = self.initial_capital
        self.trades = []
    
    def get_position(self, ts_code: str) -> Dict:
        """
        获取当前持仓
        
        Args:
            ts_code: 股票代码
            
        Returns:
            持仓信息
        """
        positions = self.db.get_positions()
        if not positions.empty and ts_code in positions['ts_code'].values:
            pos = positions[positions['ts_code'] == ts_code].iloc[0]
            return {
                "ts_code": ts_code,
                "volume": int(pos['volume']),
                "avg_price": float(pos['avg_price']),
                "current_price": float(pos['current_price']),
                "market_value": float(pos['market_value']),
                "cost": float(pos['cost']),
                "profit": float(pos['profit']),
                "profit_rate": float(pos['profit_rate'])
            }
        return {
            "ts_code": ts_code,
            "volume": 0,
            "avg_price": 0,
            "current_price": 0,
            "market_value": 0,
            "cost": 0,
            "profit": 0,
            "profit_rate": 0
        }
    
    def calculate_max_buy_amount(self, ts_code: str, current_price: float) -> float:
        """
        计算最大可买数量
        
        Args:
            ts_code: 股票代码
            current_price: 当前价格
            
        Returns:
            最大可买股数
        """
        max_invest = self.capital * self.max_position_ratio
        shares = int(max_invest / current_price)
        
        # 确保是 100 的倍数
        shares = (shares // self.min_shares) * self.min_shares
        
        return max(shares, 0)
    
    def buy(self, ts_code: str, price: float, volume: int, 
           notes: str = "") -> Optional[Dict]:
        """
        买入操作
        
        Args:
            ts_code: 股票代码
            price: 买入价格
            volume: 买入数量
            notes: 备注
            
        Returns:
            交易记录或 None
        """
        if volume == 0:
            trader_logger.warning(f"{ts_code} 买入数量不能为 0")
            return None
        
        current_pos = self.get_position(ts_code)
        if current_pos['volume'] > 0:
            trader_logger.warning(f"{ts_code} 已有持仓，请先平仓")
            return None
        
        # 计算最大可买数量
        max_buy = self.calculate_max_buy_amount(ts_code, price)
        if volume > max_buy:
            trader_logger.warning(f"{ts_code} 买入数量超出，最大可买 {max_buy} 股")
            volume = max_buy
        
        if volume < self.min_shares:
            trader_logger.warning(f"{ts_code} 买入数量不能小于 {self.min_shares} 股")
            return None
        
        # 计算费用
        amount = price * volume
        commission = amount * self.commission_rate
        total_cost = amount + commission
        
        # 检查资金
        if total_cost > self.capital:
            trader_logger.warning(f"{ts_code} 资金不足：需要{total_cost:.2f}，可用{self.capital:.2f}")
            return None
        
        # 执行买入
        try:
            # 更新资金
            self.capital -= total_cost
            
            # 记录交易
            trade = {
                "ts_code": ts_code,
                "type": "BUY",
                "time": datetime.now(),
                "price": price,
                "volume": volume,
                "amount": amount,
                "commission": commission,
                "stamp": 0,  # 买入不收印花税
                "balance_after": self.capital,
                "notes": notes
            }
            
            self.trades.append(trade)
            
            # 存储到数据库
            self.db.store_trade(trade)
            
            # 更新持仓
            self._update_position(ts_code, volume, price, commission)
            
            trader_logger.info(f"✅ 买入 {ts_code} {volume}股 @ {price:.2f}")
            return trade
            
        except Exception as e:
            trader_logger.error(f"{ts_code} 买入失败：{e}")
            self.capital += total_cost
            return None
    
    def sell(self, ts_code: str, price: float, volume: int,
            notes: str = "") -> Optional[Dict]:
        """
        卖出操作
        
        Args:
            ts_code: 股票代码
            price: 卖出价格
            volume: 卖出数量
            notes: 备注
            
        Returns:
            交易记录或 None
        """
        if volume == 0:
            trader_logger.warning(f"{ts_code} 卖出数量不能为 0")
            return None
        
        current_pos = self.get_position(ts_code)
        if current_pos['volume'] == 0:
            trader_logger.warning(f"{ts_code} 无持仓，无法卖出")
            return None
        
        if volume > current_pos['volume']:
            trader_logger.warning(f"{ts_code} 卖出数量超出持仓")
            return None
        
        # 计算费用
        amount = price * volume
        commission = amount * self.commission_rate
        stamp = amount * self.stamp_rate
        total_return = amount - commission - stamp
        
        # 执行卖出
        try:
            # 更新资金
            self.capital += total_return
            
            # 记录交易
            trade = {
                "ts_code": ts_code,
                "type": "SELL",
                "time": datetime.now(),
                "price": price,
                "volume": volume,
                "amount": amount,
                "commission": commission,
                "stamp": stamp,
                "balance_after": self.capital,
                "notes": notes
            }
            
            self.trades.append(trade)
            
            # 存储到数据库
            self.db.store_trade(trade)
            
            # 更新持仓
            self._update_position(ts_code, -volume, price, commission + stamp)
            
            trader_logger.info(f"✅ 卖出 {ts_code} {volume}股 @ {price:.2f}")
            return trade
            
        except Exception as e:
            trader_logger.error(f"{ts_code} 卖出失败：{e}")
            self.capital -= total_return
            return None
    
    def _update_position(self, ts_code: str, volume_change: int, 
                        trade_price: float, fees: float):
        """
        更新持仓
        
        Args:
            ts_code: 股票代码
            volume_change: 数量变化
            trade_price: 交易价格
            fees: 费用
        """
        try:
            cursor = self.db.conn.cursor()
            
            # 检查是否已有持仓
            cursor.execute("SELECT * FROM positions WHERE ts_code = ?", (ts_code,))
            existing = cursor.fetchone()
            
            if existing:
                existing_volume = existing[3]
                existing_avg_price = existing[4]
                existing_cost = existing[5]
                
                if volume_change > 0:
                    # 加仓
                    new_volume = existing_volume + volume_change
                    new_cost = existing_cost + (trade_price * volume_change) + fees
                    new_avg_price = new_cost / new_volume
                else:
                    # 减仓
                    new_volume = existing_volume + volume_change
                    new_cost = existing_cost + (trade_price * volume_change) + fees
                    new_avg_price = new_cost / new_volume if new_volume > 0 else 0
            else:
                # 新建持仓
                new_volume = volume_change
                new_cost = abs(trade_price * volume_change) + fees
                new_avg_price = trade_price
            
            # 获取最新价格
            cursor.execute("SELECT close FROM daily_data WHERE ts_code = ? ORDER BY trade_date DESC LIMIT 1", 
                         (ts_code,))
            result = cursor.fetchone()
            current_price = result[0] if result else 0
            
            market_value = new_volume * current_price
            profit = market_value - new_cost
            profit_rate = (profit / new_cost * 100) if new_cost > 0 else 0
            
            # 保存或更新持仓
            if new_volume > 0:
                if existing:
                    cursor.execute('''
                        UPDATE positions SET volume=?, avg_price=?, current_price=?, 
                                           market_value=?, cost=?, profit=?, profit_rate=?, 
                                           updated_at=CURRENT_TIMESTAMP
                        WHERE ts_code=?
                    ''', (new_volume, new_avg_price, current_price, market_value, 
                          new_cost, profit, profit_rate, ts_code))
                else:
                    cursor.execute('''
                        INSERT INTO positions (ts_code, volume, avg_price, current_price, 
                                              market_value, cost, profit, profit_rate, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ''', (ts_code, new_volume, new_avg_price, current_price, 
                          market_value, new_cost, profit, profit_rate))
            else:
                # 清仓
                cursor.execute("DELETE FROM positions WHERE ts_code = ?", (ts_code,))
            
            self.db.conn.commit()
            
        except Exception as e:
            self.db.conn.rollback()
            trader_logger.error(f"更新 {ts_code} 持仓失败：{e}")
    
    def get_portfolio(self) -> Dict:
        """
        获取投资组合
        
        Returns:
            投资组合信息
        """
        positions = self.db.get_positions()
        
        # 获取所有持仓的最新价格
        for ts_code in positions['ts_code'].values:
            df = self.db.get_daily_data(ts_code, days=1)
            if df is not None and not df.empty:
                current_price = float(df['close'].iloc[-1])
                positions.loc[position['ts_code'] == ts_code, 'current_price'] = current_price
                positions.loc[position['ts_code'] == ts_code, 'market_value'] = \
                    positions.loc[positions['ts_code'] == ts_code, 'volume'] * current_price
                positions.loc[positions['ts_code'] == ts_code, 'profit'] = \
                    positions.loc[positions['ts_code'] == ts_code, 'market_value'] - \
                    positions.loc[positions['ts_code'] == ts_code, 'cost']
                positions.loc[positions['ts_code'] == ts_code, 'profit_rate'] = \
                    (positions.loc[positions['ts_code'] == ts_code, 'profit'] / 
                     positions.loc[positions['ts_code'] == ts_code, 'cost'] * 100)
        
        total_market_value = positions['market_value'].sum()
        total_cost = positions['cost'].sum()
        total_profit = total_market_value - total_cost
        total_profit_rate = (total_profit / total_cost * 100) if total_cost > 0 else 0
        
        portfolio = {
            "total_capital": self.capital + total_market_value,
            "cash": self.capital,
            "market_value": total_market_value,
            "total_cost": total_cost,
            "total_profit": total_profit,
            "total_profit_rate": total_profit_rate,
            "positions": positions.to_dict('records'),
            "position_count": len(positions)
        }
        
        return portfolio
    
    def get_trade_history(self, ts_code: str = None, 
                         start_date: str = None,
                         end_date: str = None) -> pd.DataFrame:
        """
        获取交易历史
        
        Args:
            ts_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            交易历史 DataFrame
        """
        if not ts_code:
            df = pd.read_sql_query("SELECT * FROM trades ORDER BY trade_time DESC", self.db.conn)
        else:
            query = "SELECT * FROM trades WHERE ts_code = ?"
            params = [ts_code]
            
            if start_date:
                query += " AND trade_time >= ?"
                params.append(start_date)
            if end_date:
                query += " AND trade_time <= ?"
                params.append(end_date)
            
            query += " ORDER BY trade_time DESC"
            df = pd.read_sql_query(query, self.db.conn, params=params)
        
        return df
    
    def get_performance_report(self, start_date: str = None,
                              end_date: str = None) -> Dict:
        """
        获取绩效报告
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            绩效报告
        """
        trades = self.get_trade_history(start_date, end_date)
        
        if trades.empty:
            return {"error": "无交易记录"}
        
        # 统计分析
        buy_trades = trades[trades['trade_type'] == 'BUY']
        sell_trades = trades[trades['trade_type'] == 'SELL']
        
        total_fees = trades['commission'].sum() + trades['stamp'].sum()
        total_bought = len(buy_trades)
        total_sold = len(sell_trades)
        
        # 计算每只股票的盈亏
        stock_stats = []
        for ts_code in set(trades['ts_code'].unique()):
            stock_trades = trades[trades['ts_code'] == ts_code]
            net_volume = (stock_trades[stock_trades['trade_type'] == 'BUY']['volume'].sum() -
                         stock_trades[stock_trades['trade_type'] == 'SELL']['volume'].sum())
            
            if net_volume == 0:
                # 已平仓，计算总盈亏
                buy_amount = stock_trades[stock_trades['trade_type'] == 'BUY']['amount'].sum()
                sell_amount = stock_trades[stock_trades['trade_type'] == 'SELL']['amount'].sum()
                fees = stock_trades[['commission', 'stamp']].sum().sum()
                profit = sell_amount - buy_amount - fees
                
                stock_stats.append({
                    "ts_code": ts_code,
                    "trades": len(stock_trades),
                    "buy_amount": buy_amount,
                    "sell_amount": sell_amount,
                    "fees": fees,
                    "profit": profit,
                    "profit_rate": (profit / buy_amount * 100) if buy_amount > 0 else 0
                })
        
        # 按盈亏排序
        stock_stats.sort(key=lambda x: x['profit'], reverse=True)
        
        return {
            "start_date": start_date,
            "end_date": end_date,
            "total_trades": len(trades),
            "total_bought": total_bought,
            "total_sold": total_sold,
            "total_fees": total_fees,
            "current_capital": self.capital,
            "stock_stats": stock_stats
        }

# ==================== 单例模式 ====================
_trader_instance = None

def get_trader() -> SimulatedTrader:
    """获取交易器实例"""
    global _trader_instance
    if _trader_instance is None:
        _trader_instance = SimulatedTrader()
    return _trader_instance
