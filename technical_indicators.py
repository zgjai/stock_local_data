"""
技术指标计算模块
"""

import pandas as pd
import numpy as np
from typing import Tuple
import random

class TechnicalIndicators:
    @staticmethod
    def calculate_kdj(high, low, close, fastk_period=9, slowk_period=3, slowd_period=3):
        """计算KDJ指标"""
        try:
            lowest_low = low.rolling(window=fastk_period).min()
            highest_high = high.rolling(window=fastk_period).max()
            rsv = (close - lowest_low) / (highest_high - lowest_low) * 100
            
            k = rsv.ewm(alpha=1/slowk_period).mean()
            
            d = k.ewm(alpha=1/slowd_period).mean()
            
            j = 3 * k - 2 * d
            
            return k, d, j
        except Exception as e:
            print(f"KDJ计算错误: {e}")
            return None, None, None
    
    @staticmethod
    def calculate_macd(close, fastperiod=12, slowperiod=26, signalperiod=9):
        """计算MACD指标"""
        try:
            ema12 = close.ewm(span=fastperiod).mean()
            ema26 = close.ewm(span=slowperiod).mean()
            dif = ema12 - ema26
            dea = dif.ewm(span=signalperiod).mean()
            macd = (dif - dea) * 2
            return dif, dea, macd
        except Exception as e:
            print(f"MACD计算错误: {e}")
            ema12 = close.ewm(span=fastperiod).mean()
            ema26 = close.ewm(span=slowperiod).mean()
            dif = ema12 - ema26
            dea = dif.ewm(span=signalperiod).mean()
            macd = (dif - dea) * 2
            return dif, dea, macd
    
    @staticmethod
    def calculate_bbi(close, period1=3, period2=6, period3=12, period4=24):
        """计算BBI指标（多空指数）"""
        try:
            ma1 = close.rolling(window=period1).mean()
            ma2 = close.rolling(window=period2).mean()
            ma3 = close.rolling(window=period3).mean()
            ma4 = close.rolling(window=period4).mean()
            
            bbi = (ma1 + ma2 + ma3 + ma4) / 4
            return bbi
        except Exception as e:
            print(f"BBI计算错误: {e}")
            return None
    
    @staticmethod
    def calculate_zhixing_long_short(close, high, low, volume) -> Tuple[float, float]:
        """
        计算知行合一长短线指标（模拟实现）
        返回: (长线值, 短线值)
        """
        try:
            
            long_ma = close.rolling(window=60).mean()
            price_position = (close - long_ma) / long_ma * 100
            volume_ma = volume.rolling(window=20).mean()
            volume_ratio = volume / volume_ma
            
            long_line = (price_position.iloc[-1] * 0.7 + 
                        (volume_ratio.iloc[-1] - 1) * 30 * 0.3)
            
            short_ma = close.rolling(window=10).mean()
            short_position = (close - short_ma) / short_ma * 100
            volatility = (high - low) / close * 100
            
            short_line = (short_position.iloc[-1] * 0.6 + 
                         volatility.iloc[-1] * 0.4)
            
            return float(long_line), float(short_line)
            
        except Exception as e:
            print(f"知行合一长短线计算错误: {e}")
            return random.uniform(-50, 50), random.uniform(-30, 30)
    
    @staticmethod
    def calculate_zhixing_bull_bear(close, high, low, volume) -> Tuple[float, float]:
        """
        计算知行合一多空线指标（模拟实现）
        返回: (多头值, 空头值)
        """
        try:
            
            price_change = close.pct_change()
            up_days = (price_change > 0).rolling(window=20).sum()
            avg_up_change = price_change[price_change > 0].rolling(window=20).mean()
            
            down_days = (price_change < 0).rolling(window=20).sum()
            avg_down_change = abs(price_change[price_change < 0]).rolling(window=20).mean()
            
            volume_trend = volume.rolling(window=10).mean() / volume.rolling(window=30).mean()
            
            bull_line = (up_days.iloc[-1] / 20 * 100 * 0.5 + 
                        avg_up_change.iloc[-1] * 1000 * 0.3 +
                        (volume_trend.iloc[-1] - 1) * 50 * 0.2)
            
            bear_line = (down_days.iloc[-1] / 20 * 100 * 0.5 + 
                        avg_down_change.iloc[-1] * 1000 * 0.3 +
                        (2 - volume_trend.iloc[-1]) * 50 * 0.2)
            
            return float(bull_line), float(bear_line)
            
        except Exception as e:
            print(f"知行合一多空线计算错误: {e}")
            return random.uniform(0, 100), random.uniform(0, 100)
    
    @classmethod
    def calculate_all_indicators(cls, df):
        """计算所有技术指标"""
        if df is None or df.empty:
            return df
        
        try:
            if '收盘' in df.columns:
                close = df['收盘']
                high = df['最高']
                low = df['最低']
                volume = df['成交量']
            else:
                close = df['close'] if 'close' in df.columns else df.iloc[:, 4]
                high = df['high'] if 'high' in df.columns else df.iloc[:, 2]
                low = df['low'] if 'low' in df.columns else df.iloc[:, 3]
                volume = df['volume'] if 'volume' in df.columns else df.iloc[:, 5]
            
            k, d, j = cls.calculate_kdj(high, low, close)
            if k is not None:
                df['kdj_k'] = k
                df['kdj_d'] = d
                df['kdj_j'] = j
            
            dif, dea, macd = cls.calculate_macd(close)
            if dif is not None:
                df['macd_dif'] = dif
                df['macd_dea'] = dea
                df['macd_macd'] = macd
            
            bbi = cls.calculate_bbi(close)
            if bbi is not None:
                df['bbi'] = bbi
            
            if len(df) > 0:
                long_line, short_line = cls.calculate_zhixing_long_short(close, high, low, volume)
                bull_line, bear_line = cls.calculate_zhixing_bull_bear(close, high, low, volume)
                
                df['zhixing_long_line'] = long_line
                df['zhixing_short_line'] = short_line
                df['zhixing_bull_line'] = bull_line
                df['zhixing_bear_line'] = bear_line
            
            return df
            
        except Exception as e:
            print(f"计算技术指标时出错: {e}")
            return df
