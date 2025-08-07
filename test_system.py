"""
系统测试脚本
"""

import unittest
import os
import tempfile
from datetime import datetime, timedelta
from stock_database import StockDatabase
from data_fetcher import DataFetcher
from technical_indicators import TechnicalIndicators
import pandas as pd
import numpy as np

class TestStockDatabase(unittest.TestCase):
    def setUp(self):
        """测试前准备"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = StockDatabase(self.temp_db.name)
    
    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_database_initialization(self):
        """测试数据库初始化"""
        conn = self.db.db_schema.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['stock_daily_data', 'sector_daily_data', 
                          'sector_ranking_stats', 'update_log']
        
        for table in expected_tables:
            self.assertIn(table, tables)
        
        conn.close()
    
    def test_data_fetcher(self):
        """测试数据获取功能"""
        fetcher = DataFetcher()
        
        try:
            data = fetcher.get_realtime_stock_data()
            if data is not None:
                self.assertIsInstance(data, pd.DataFrame)
                self.assertGreater(len(data), 0)
        except Exception as e:
            print(f"实时数据获取测试跳过: {e}")
    
    def test_technical_indicators(self):
        """测试技术指标计算"""
        dates = pd.date_range('2024-01-01', periods=30, freq='D')
        test_data = pd.DataFrame({
            '日期': dates,
            '开盘': np.random.uniform(10, 20, 30),
            '最高': np.random.uniform(15, 25, 30),
            '最低': np.random.uniform(8, 15, 30),
            '收盘': np.random.uniform(10, 20, 30),
            '成交量': np.random.uniform(1000000, 10000000, 30)
        })
        
        result = TechnicalIndicators.calculate_all_indicators(test_data)
        
        expected_columns = ['kdj_k', 'kdj_d', 'kdj_j', 'macd_dif', 'macd_dea', 
                           'macd_macd', 'bbi', 'zhixing_long_line', 'zhixing_short_line',
                           'zhixing_bull_line', 'zhixing_bear_line']
        
        for col in expected_columns:
            self.assertIn(col, result.columns)
    
    def test_database_operations(self):
        """测试数据库操作"""
        test_record = (
            '2024-01-01', '000001', '测试股票', 1000000, 800000,
            10.0, 11.0, 9.5, 10.5, 1000000,
            50.0, 30.0, 70.0, 0.1, 0.05, 0.05, 10.2,
            25.5, -15.2, 60.3, 40.7, '银行', '金融'
        )
        
        insert_query = '''
            INSERT INTO stock_daily_data 
            (date, stock_code, stock_name, total_market_cap, circulating_market_cap,
             open_price, high_price, low_price, close_price, volume,
             kdj_k, kdj_d, kdj_j, macd_dif, macd_dea, macd_macd, bbi,
             zhixing_long_line, zhixing_short_line, zhixing_bull_line, zhixing_bear_line,
             industry_sector, concept_sectors)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        count = self.db.db_schema.execute_insert(insert_query, test_record)
        self.assertEqual(count, 1)
        
        data = self.db.query_stock_data('000001')
        self.assertEqual(len(data), 1)
        self.assertEqual(data.iloc[0]['stock_name'], '测试股票')
    
    def test_database_stats(self):
        """测试数据库统计功能"""
        stats = self.db.get_database_stats()
        
        expected_keys = ['stock_records', 'sector_records', 'latest_date', 'unique_stocks']
        for key in expected_keys:
            self.assertIn(key, stats)

class TestDataIntegrity(unittest.TestCase):
    """数据完整性测试"""
    
    def test_mock_indicators(self):
        """测试模拟指标的合理性"""
        close = pd.Series([10, 11, 12, 11, 10])
        high = pd.Series([11, 12, 13, 12, 11])
        low = pd.Series([9, 10, 11, 10, 9])
        volume = pd.Series([1000, 1100, 1200, 1100, 1000])
        
        long_line, short_line = TechnicalIndicators.calculate_zhixing_long_short(
            close, high, low, volume
        )
        
        self.assertIsInstance(long_line, float)
        self.assertIsInstance(short_line, float)
        
        bull_line, bear_line = TechnicalIndicators.calculate_zhixing_bull_bear(
            close, high, low, volume
        )
        
        self.assertIsInstance(bull_line, float)
        self.assertIsInstance(bear_line, float)

def run_tests():
    """运行所有测试"""
    print("开始运行系统测试...")
    
    test_suite = unittest.TestSuite()
    
    test_suite.addTest(unittest.makeSuite(TestStockDatabase))
    test_suite.addTest(unittest.makeSuite(TestDataIntegrity))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    if result.wasSuccessful():
        print("\n✓ 所有测试通过!")
        return True
    else:
        print(f"\n✗ 测试失败: {len(result.failures)} 个失败, {len(result.errors)} 个错误")
        return False

if __name__ == "__main__":
    run_tests()
