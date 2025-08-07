"""
数据获取模块 - 基于akshare库获取股票和板块数据
"""

import akshare as ak
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataFetcher:
    def __init__(self):
        self.retry_count = 3
        self.retry_delay = 1  # 秒
    
    def _retry_request(self, func, *args, **kwargs):
        """重试机制"""
        for attempt in range(self.retry_count):
            try:
                result = func(*args, **kwargs)
                if result is not None and not result.empty:
                    return result
            except Exception as e:
                logger.warning(f"请求失败 (尝试 {attempt + 1}/{self.retry_count}): {str(e)}")
                if attempt < self.retry_count - 1:
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"请求最终失败: {str(e)}")
                    raise e
        return None
    
    def get_realtime_stock_data(self):
        """获取实时股票数据"""
        logger.info("获取实时股票数据...")
        try:
            data = self._retry_request(ak.stock_zh_a_spot_em)
            if data is not None:
                logger.info(f"成功获取 {len(data)} 只股票的实时数据")
                return data
        except Exception as e:
            logger.error(f"获取实时股票数据失败: {str(e)}")
            return None
    
    def get_historical_stock_data(self, symbol, start_date, end_date=None, period="daily"):
        """获取历史股票数据"""
        if end_date is None:
            end_date = datetime.now().strftime('%Y%m%d')
        
        try:
            data = self._retry_request(
                ak.stock_zh_a_hist,
                symbol=symbol,
                period=period,
                start_date=start_date,
                end_date=end_date,
                adjust="qfq"
            )
            return data
        except Exception as e:
            logger.error(f"获取股票 {symbol} 历史数据失败: {str(e)}")
            return None
    
    def get_industry_sector_data(self):
        """获取行业板块数据"""
        logger.info("获取行业板块数据...")
        try:
            data = self._retry_request(ak.stock_board_industry_name_em)
            if data is not None:
                logger.info(f"成功获取 {len(data)} 个行业板块数据")
                return data
        except Exception as e:
            logger.error(f"获取行业板块数据失败: {str(e)}")
            return None
    
    def get_industry_constituents(self, symbol):
        """获取行业板块成分股"""
        try:
            data = self._retry_request(ak.stock_board_industry_cons_em, symbol=symbol)
            return data
        except Exception as e:
            logger.error(f"获取行业板块 {symbol} 成分股失败: {str(e)}")
            return None
    
    def get_concept_sector_data(self):
        """获取概念板块数据"""
        logger.info("获取概念板块数据...")
        try:
            data = self._retry_request(ak.stock_board_concept_name_em)
            if data is not None:
                logger.info(f"成功获取 {len(data)} 个概念板块数据")
                return data
        except Exception as e:
            logger.error(f"获取概念板块数据失败: {str(e)}")
            return None
    
    def get_concept_constituents(self, symbol):
        """获取概念板块成分股"""
        try:
            data = self._retry_request(ak.stock_board_concept_cons_em, symbol=symbol)
            return data
        except Exception as e:
            logger.error(f"获取概念板块 {symbol} 成分股失败: {str(e)}")
            return None
    
    def get_stock_list(self):
        """获取股票列表"""
        try:
            data = self.get_realtime_stock_data()
            if data is not None:
                return data[['代码', '名称']].values.tolist()
        except Exception as e:
            logger.error(f"获取股票列表失败: {str(e)}")
            return []
    
    def batch_get_historical_data(self, stock_list, start_date, end_date=None, batch_size=50):
        """批量获取历史数据"""
        logger.info(f"开始批量获取 {len(stock_list)} 只股票的历史数据...")
        
        all_data = []
        failed_stocks = []
        
        for i in range(0, len(stock_list), batch_size):
            batch = stock_list[i:i + batch_size]
            logger.info(f"处理批次 {i//batch_size + 1}/{(len(stock_list)-1)//batch_size + 1}")
            
            for stock_code, stock_name in batch:
                try:
                    data = self.get_historical_stock_data(stock_code, start_date, end_date)
                    if data is not None and not data.empty:
                        data['股票代码'] = stock_code
                        data['股票名称'] = stock_name
                        all_data.append(data)
                    else:
                        failed_stocks.append((stock_code, stock_name))
                    
                    time.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"获取股票 {stock_code} 数据失败: {str(e)}")
                    failed_stocks.append((stock_code, stock_name))
            
            time.sleep(1)
        
        if failed_stocks:
            logger.warning(f"有 {len(failed_stocks)} 只股票数据获取失败")
        
        if all_data:
            combined_data = pd.concat(all_data, ignore_index=True)
            logger.info(f"成功获取 {len(all_data)} 只股票的历史数据，共 {len(combined_data)} 条记录")
            return combined_data
        
        return None
