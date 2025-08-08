"""
技术指标计算模块
"""

import pandas as pd
import numpy as np
from typing import Tuple
import random

class TechnicalIndicators:
    @staticmethod
    def _format_decimal(value, decimals=3):
        """格式化小数位数，最多保留指定位数"""
        if value is None or pd.isna(value):
            return None
        return round(float(value), decimals)
    
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
            
            if len(k) > 0:
                return (TechnicalIndicators._format_decimal(k.iloc[-1]),
                        TechnicalIndicators._format_decimal(d.iloc[-1]),
                        TechnicalIndicators._format_decimal(j.iloc[-1]))
            else:
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
            if len(dif) > 0:
                return (TechnicalIndicators._format_decimal(dif.iloc[-1]),
                        TechnicalIndicators._format_decimal(dea.iloc[-1]),
                        TechnicalIndicators._format_decimal(macd.iloc[-1]))
            else:
                return dif, dea, macd
        except Exception as e:
            print(f"MACD计算错误: {e}")
            ema12 = close.ewm(span=fastperiod).mean()
            ema26 = close.ewm(span=slowperiod).mean()
            dif = ema12 - ema26
            dea = dif.ewm(span=signalperiod).mean()
            macd = (dif - dea) * 2
            if len(dif) > 0:
                return (TechnicalIndicators._format_decimal(dif.iloc[-1]),
                        TechnicalIndicators._format_decimal(dea.iloc[-1]),
                        TechnicalIndicators._format_decimal(macd.iloc[-1]))
            else:
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
            if len(bbi) > 0:
                return TechnicalIndicators._format_decimal(bbi.iloc[-1])
            else:
                return bbi
        except Exception as e:
            print(f"BBI计算错误: {e}")
            return None
    
    @staticmethod
    def calculate_zhixing_long_short(close, high, low, volume, n1=3, n2=21) -> Tuple[float, float]:
        """
        计算知行合一长短线指标
        短期:100*(C-LLV(L,N1))/(HHV(C,N1)-LLV(L,N1))
        长期:100*(C-LLV(L,N2))/(HHV(C,N2)-LLV(L,N2))
        返回: (长线值, 短线值)
        """
        try:
            effective_n1 = min(n1, len(close))
            effective_n2 = min(n2, len(close))
            
            llv_short = low.rolling(effective_n1).min()
            hhv_short = close.rolling(effective_n1).max()
            short_line = 100 * (close - llv_short) / (hhv_short - llv_short)
            
            llv_long = low.rolling(effective_n2).min()
            hhv_long = close.rolling(effective_n2).max()
            long_line = 100 * (close - llv_long) / (hhv_long - llv_long)
            
            long_val = long_line.iloc[-1] if not pd.isna(long_line.iloc[-1]) else 50.0
            short_val = short_line.iloc[-1] if not pd.isna(short_line.iloc[-1]) else 50.0
            
            return (TechnicalIndicators._format_decimal(long_val), 
                    TechnicalIndicators._format_decimal(short_val))
            
        except Exception as e:
            print(f"知行合一长短线计算错误: {e}")
            return TechnicalIndicators._format_decimal(50.0), TechnicalIndicators._format_decimal(50.0)
    
    @staticmethod
    def calculate_zhixing_bull_bear(close, high, low, volume) -> Tuple[float, float]:
        """
        计算知行合一多空线指标（基于通达信公式）
        白线: EMA(EMA(C,10),10) - 知行中期多空线
        黄线: MA(CLOSE,60) - MA1
        返回: (白线值, 黄线值)
        """
        try:
            ema10 = close.ewm(span=10).mean()
            white_line = ema10.ewm(span=10).mean()
            
            effective_window = min(60, len(close))
            yellow_line = close.rolling(window=effective_window).mean()
            
            white_val = white_line.iloc[-1] if not pd.isna(white_line.iloc[-1]) else close.iloc[-1]
            yellow_val = yellow_line.iloc[-1] if not pd.isna(yellow_line.iloc[-1]) else close.iloc[-1]
            
            return (TechnicalIndicators._format_decimal(white_val), 
                    TechnicalIndicators._format_decimal(yellow_val))
            
        except Exception as e:
            print(f"知行合一多空线计算错误: {e}")
            return TechnicalIndicators._format_decimal(50.0), TechnicalIndicators._format_decimal(50.0)
    
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
            
            indicator_columns = ['kdj_k', 'kdj_d', 'kdj_j', 'macd_dif', 'macd_dea', 'macd_macd', 'bbi']
            for col in indicator_columns:
                if col in df.columns:
                    df[col] = df[col].apply(lambda x: cls._format_decimal(x) if pd.notna(x) else x)
            
            if len(df) > 0:
                long_line, short_line = cls.calculate_zhixing_long_short(close, high, low, volume)
                bull_line, bear_line = cls.calculate_zhixing_bull_bear(close, high, low, volume)
                
                df['zhixing_long_line'] = cls._format_decimal(long_line)
                df['zhixing_short_line'] = cls._format_decimal(short_line)
                df['zhixing_bull_line'] = cls._format_decimal(bull_line)
                df['zhixing_bear_line'] = cls._format_decimal(bear_line)
            
            return df
            
        except Exception as e:
            print(f"计算技术指标时出错: {e}")
            return df
