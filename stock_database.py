"""
股票数据库主类 - 整合数据获取、存储和查询功能
"""

import pandas as pd
import json
from datetime import datetime, timedelta
import logging
from database_schema import DatabaseSchema
from data_fetcher import DataFetcher
from technical_indicators import TechnicalIndicators

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StockDatabase:
    def __init__(self, db_path="stock_market.db"):
        self.db_schema = DatabaseSchema(db_path)
        self.data_fetcher = DataFetcher()
        self.tech_indicators = TechnicalIndicators()
        
    def initialize_historical_data(self, days_back=365):
        """初始化历史数据（默认过去一年）"""
        logger.info(f"开始初始化过去 {days_back} 天的历史数据...")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        start_date_str = start_date.strftime('%Y%m%d')
        end_date_str = end_date.strftime('%Y%m%d')
        
        try:
            stock_list = self.data_fetcher.get_stock_list()
            if not stock_list:
                logger.error("无法获取股票列表")
                return False
            
            logger.info(f"获取到 {len(stock_list)} 只股票")
            
            historical_data = self.data_fetcher.batch_get_historical_data(
                stock_list,
                start_date_str, 
                end_date_str,
                batch_size=20
            )
            
            if historical_data is not None:
                processed_count = self._process_and_store_stock_data(historical_data)
                
                self._log_update('historical', 'success', processed_count)
                logger.info(f"历史数据初始化完成，处理了 {processed_count} 条记录")
                return True
            else:
                self._log_update('historical', 'failed', 0, "无法获取历史数据")
                return False
                
        except Exception as e:
            error_msg = f"历史数据初始化失败: {str(e)}"
            logger.error(error_msg)
            self._log_update('historical', 'failed', 0, error_msg)
            return False
    
    def daily_update(self):
        """日常数据更新"""
        logger.info("开始日常数据更新...")
        
        today = datetime.now().strftime('%Y-%m-%d')
        success_count = 0
        
        try:
            stock_success = self._update_daily_stock_data()
            if stock_success:
                success_count += 1
            
            sector_success = self._update_daily_sector_data()
            if sector_success:
                success_count += 1
            
            ranking_success = self._update_sector_rankings()
            if ranking_success:
                success_count += 1
            
            if success_count == 3:
                self._log_update('daily', 'success', success_count)
                logger.info("日常数据更新完成")
                return True
            else:
                self._log_update('daily', 'partial', success_count)
                logger.warning(f"日常数据更新部分成功，成功项目: {success_count}/3")
                return False
                
        except Exception as e:
            error_msg = f"日常数据更新失败: {str(e)}"
            logger.error(error_msg)
            self._log_update('daily', 'failed', 0, error_msg)
            return False
    
    def _update_daily_stock_data(self):
        """更新日常股票数据"""
        try:
            realtime_data = self.data_fetcher.get_realtime_stock_data()
            if realtime_data is None:
                return False
            
            processed_count = self._process_and_store_realtime_data(realtime_data)
            logger.info(f"更新了 {processed_count} 只股票的日常数据")
            return True
            
        except Exception as e:
            logger.error(f"更新日常股票数据失败: {str(e)}")
            return False
    
    def _update_daily_sector_data(self):
        """更新日常板块数据"""
        try:
            success_count = 0
            
            industry_data = self.data_fetcher.get_industry_sector_data()
            if industry_data is not None:
                industry_count = self._process_and_store_sector_data(industry_data, '行业')
                success_count += industry_count
            
            concept_data = self.data_fetcher.get_concept_sector_data()
            if concept_data is not None:
                concept_count = self._process_and_store_sector_data(concept_data, '概念')
                success_count += concept_count
            
            logger.info(f"更新了 {success_count} 个板块的数据")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"更新日常板块数据失败: {str(e)}")
            return False
    
    def _process_and_store_stock_data(self, data):
        """处理和存储股票数据"""
        if data is None or data.empty:
            return 0
        
        processed_records = []
        
        try:
            for stock_code in data['股票代码'].unique():
                stock_data = data[data['股票代码'] == stock_code].copy()
                stock_name = stock_data['股票名称'].iloc[0]
                
                stock_data = self.tech_indicators.calculate_all_indicators(stock_data)
                
                for _, row in stock_data.iterrows():
                    record = self._convert_to_db_record(row, stock_code, stock_name)
                    if record:
                        processed_records.append(record)
            
            if processed_records:
                insert_query = '''
                    INSERT OR REPLACE INTO stock_daily_data 
                    (date, stock_code, stock_name, total_market_cap, circulating_market_cap,
                     open_price, high_price, low_price, close_price, volume,
                     kdj_k, kdj_d, kdj_j, macd_dif, macd_dea, macd_macd, bbi,
                     zhixing_long_line, zhixing_short_line, zhixing_bull_line, zhixing_bear_line,
                     industry_sector, concept_sectors)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                '''
                
                self.db_schema.execute_insert(insert_query, processed_records)
                logger.info(f"成功存储 {len(processed_records)} 条股票数据记录")
                
            return len(processed_records)
            
        except Exception as e:
            logger.error(f"处理和存储股票数据失败: {str(e)}")
            return 0
    
    def _process_and_store_realtime_data(self, data):
        """处理和存储实时数据"""
        if data is None or data.empty:
            return 0
        
        today = datetime.now().strftime('%Y-%m-%d')
        processed_records = []
        
        try:
            for _, row in data.iterrows():
                stock_code = str(row['代码'])
                stock_name = str(row['名称'])
                
                long_line, short_line = self.tech_indicators.calculate_zhixing_long_short(
                    pd.Series([row['最新价']]), pd.Series([row['最高']]), 
                    pd.Series([row['最低']]), pd.Series([row['成交量']])
                )
                bull_line, bear_line = self.tech_indicators.calculate_zhixing_bull_bear(
                    pd.Series([row['最新价']]), pd.Series([row['最高']]), 
                    pd.Series([row['最低']]), pd.Series([row['成交量']])
                )
                
                record = (
                    today, stock_code, stock_name,
                    row.get('总市值', 0), row.get('流通市值', 0),
                    row.get('今开', 0), row.get('最高', 0), row.get('最低', 0), row.get('最新价', 0),
                    row.get('成交量', 0),
                    None, None, None,  # KDJ需要历史数据计算
                    None, None, None,  # MACD需要历史数据计算
                    None,  # BBI需要历史数据计算
                    long_line, short_line, bull_line, bear_line,
                    '', ''  # 行业和概念板块信息需要单独获取
                )
                
                processed_records.append(record)
            
            if processed_records:
                insert_query = '''
                    INSERT OR REPLACE INTO stock_daily_data 
                    (date, stock_code, stock_name, total_market_cap, circulating_market_cap,
                     open_price, high_price, low_price, close_price, volume,
                     kdj_k, kdj_d, kdj_j, macd_dif, macd_dea, macd_macd, bbi,
                     zhixing_long_line, zhixing_short_line, zhixing_bull_line, zhixing_bear_line,
                     industry_sector, concept_sectors)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                '''
                
                self.db_schema.execute_insert(insert_query, processed_records)
                
            return len(processed_records)
            
        except Exception as e:
            logger.error(f"处理和存储实时数据失败: {str(e)}")
            return 0
    
    def _process_and_store_sector_data(self, data, sector_type):
        """处理和存储板块数据"""
        if data is None or data.empty:
            return 0
        
        today = datetime.now().strftime('%Y-%m-%d')
        processed_records = []
        
        try:
            for _, row in data.iterrows():
                sector_code = row.get('板块代码', '')
                constituents = []
                
                if sector_code:
                    if sector_type == '行业':
                        const_data = self.data_fetcher.get_industry_constituents(sector_code)
                    else:
                        const_data = self.data_fetcher.get_concept_constituents(sector_code)
                    
                    if const_data is not None and not const_data.empty:
                        constituents = const_data['代码'].tolist()
                
                record = (
                    today,
                    sector_type,
                    row.get('板块名称', ''),
                    row.get('排名', 0),
                    row.get('涨跌幅', 0),
                    json.dumps(constituents)
                )
                
                processed_records.append(record)
            
            if processed_records:
                insert_query = '''
                    INSERT OR REPLACE INTO sector_daily_data 
                    (date, sector_type, sector_name, ranking, change_percent, constituent_stocks)
                    VALUES (?, ?, ?, ?, ?, ?)
                '''
                
                self.db_schema.execute_insert(insert_query, processed_records)
                
            return len(processed_records)
            
        except Exception as e:
            logger.error(f"处理和存储板块数据失败: {str(e)}")
            return 0
    
    def _convert_to_db_record(self, row, stock_code, stock_name):
        """将数据行转换为数据库记录格式"""
        try:
            if '日期' in row.index:
                date_str = str(row['日期'])
            else:
                date_str = datetime.now().strftime('%Y-%m-%d')
            
            if isinstance(date_str, str) and len(date_str) > 10:
                try:
                    date_obj = pd.to_datetime(date_str)
                    date_str = date_obj.strftime('%Y-%m-%d')
                except:
                    date_str = datetime.now().strftime('%Y-%m-%d')
            
            record = (
                date_str, stock_code, stock_name,
                row.get('总市值', 0), row.get('流通市值', 0),
                row.get('开盘', row.get('open', 0)), 
                row.get('最高', row.get('high', 0)), 
                row.get('最低', row.get('low', 0)), 
                row.get('收盘', row.get('close', 0)),
                row.get('成交量', row.get('volume', 0)),
                row.get('kdj_k'), row.get('kdj_d'), row.get('kdj_j'),
                row.get('macd_dif'), row.get('macd_dea'), row.get('macd_macd'),
                row.get('bbi'),
                row.get('zhixing_long_line'), row.get('zhixing_short_line'),
                row.get('zhixing_bull_line'), row.get('zhixing_bear_line'),
                '', ''  # 行业和概念板块信息
            )
            
            return record
            
        except Exception as e:
            logger.error(f"转换数据记录失败: {str(e)}")
            return None
    
    def _update_sector_rankings(self):
        """更新板块排名统计"""
        try:
            for period in [10, 15, 20]:
                self._calculate_sector_ranking_stats(period)
            return True
        except Exception as e:
            logger.error(f"更新板块排名统计失败: {str(e)}")
            return False
    
    def _calculate_sector_ranking_stats(self, period_days):
        """计算指定周期的板块排名统计"""
        try:
            query = '''
                SELECT sector_type, sector_name, ranking, date
                FROM sector_daily_data 
                WHERE date >= date('now', '-{} days')
                AND ranking <= 10
                ORDER BY date DESC
            '''.format(period_days)
            
            results = self.db_schema.execute_query(query)
            
            sector_stats = {}
            for sector_type, sector_name, ranking, date in results:
                key = (sector_type, sector_name)
                if key not in sector_stats:
                    sector_stats[key] = 0
                sector_stats[key] += 1
            
            for (sector_type, sector_name), count in sector_stats.items():
                update_query = '''
                    INSERT OR REPLACE INTO sector_ranking_stats 
                    (sector_type, sector_name, period_days, top10_appearances, last_updated)
                    VALUES (?, ?, ?, ?, ?)
                '''
                
                self.db_schema.execute_insert(update_query, (
                    sector_type, sector_name, period_days, count, 
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ))
            
        except Exception as e:
            logger.error(f"计算 {period_days} 天板块排名统计失败: {str(e)}")
    
    def _log_update(self, update_type, status, records_count, error_message=None):
        """记录更新日志"""
        try:
            insert_query = '''
                INSERT INTO update_log 
                (update_date, update_type, status, records_count, error_message)
                VALUES (?, ?, ?, ?, ?)
            '''
            
            self.db_schema.execute_insert(insert_query, (
                datetime.now().strftime('%Y-%m-%d'),
                update_type, status, records_count, error_message
            ))
            
        except Exception as e:
            logger.error(f"记录更新日志失败: {str(e)}")
    
    def query_stock_data(self, stock_code=None, start_date=None, end_date=None, limit=None):
        """查询个股数据"""
        query = "SELECT * FROM stock_daily_data WHERE 1=1"
        params = []
        
        if stock_code:
            query += " AND stock_code = ?"
            params.append(stock_code)
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        
        query += " ORDER BY date DESC"
        
        if limit:
            query += f" LIMIT {limit}"
        
        results = self.db_schema.execute_query(query, params)
        
        columns = [
            'id', 'date', 'stock_code', 'stock_name', 'total_market_cap', 'circulating_market_cap',
            'open_price', 'high_price', 'low_price', 'close_price', 'volume',
            'kdj_k', 'kdj_d', 'kdj_j', 'macd_dif', 'macd_dea', 'macd_macd', 'bbi',
            'zhixing_long_line', 'zhixing_short_line', 'zhixing_bull_line', 'zhixing_bear_line',
            'industry_sector', 'concept_sectors', 'created_at'
        ]
        
        return pd.DataFrame(results, columns=columns)
    
    def query_sector_data(self, sector_type=None, start_date=None, end_date=None, limit=None):
        """查询板块数据"""
        query = "SELECT * FROM sector_daily_data WHERE 1=1"
        params = []
        
        if sector_type:
            query += " AND sector_type = ?"
            params.append(sector_type)
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        
        query += " ORDER BY date DESC, ranking ASC"
        
        if limit:
            query += f" LIMIT {limit}"
        
        results = self.db_schema.execute_query(query, params)
        
        columns = ['id', 'date', 'sector_type', 'sector_name', 'ranking', 
                  'change_percent', 'constituent_stocks', 'created_at']
        
        return pd.DataFrame(results, columns=columns)
    
    def query_sector_rankings(self, period_days=None, min_appearances=1):
        """查询板块排名统计"""
        query = "SELECT * FROM sector_ranking_stats WHERE top10_appearances >= ?"
        params = [min_appearances]
        
        if period_days:
            query += " AND period_days = ?"
            params.append(period_days)
        
        query += " ORDER BY period_days, top10_appearances DESC"
        
        results = self.db_schema.execute_query(query, params)
        
        columns = ['id', 'sector_type', 'sector_name', 'period_days', 
                  'top10_appearances', 'last_updated']
        
        return pd.DataFrame(results, columns=columns)
    
    def get_database_stats(self):
        """获取数据库统计信息"""
        stats = {}
        
        stock_count = self.db_schema.execute_query("SELECT COUNT(*) FROM stock_daily_data")[0][0]
        stats['stock_records'] = stock_count
        
        sector_count = self.db_schema.execute_query("SELECT COUNT(*) FROM sector_daily_data")[0][0]
        stats['sector_records'] = sector_count
        
        latest_date = self.db_schema.execute_query(
            "SELECT MAX(date) FROM stock_daily_data"
        )[0][0]
        stats['latest_date'] = latest_date
        
        unique_stocks = self.db_schema.execute_query(
            "SELECT COUNT(DISTINCT stock_code) FROM stock_daily_data"
        )[0][0]
        stats['unique_stocks'] = unique_stocks
        
        return stats
    
    def clear_all_data(self):
        """清空所有数据库表"""
        try:
            tables = ['stock_daily_data', 'sector_daily_data', 'sector_ranking_stats', 'update_log']
            
            for table in tables:
                self.db_schema.execute_query(f"DELETE FROM {table}")
                print(f"✓ 已清空表: {table}")
            
            print("✓ 所有数据已清空")
            return True
        except Exception as e:
            print(f"✗ 清空数据失败: {e}")
            return False
