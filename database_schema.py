"""
数据库表结构定义
"""

import sqlite3
from datetime import datetime
import os

class DatabaseSchema:
    def __init__(self, db_path="stock_market.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库和表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_daily_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                stock_code TEXT NOT NULL,
                stock_name TEXT NOT NULL,
                total_market_cap REAL,
                circulating_market_cap REAL,
                open_price REAL,
                high_price REAL,
                low_price REAL,
                close_price REAL,
                volume REAL,
                kdj_k REAL,
                kdj_d REAL,
                kdj_j REAL,
                macd_dif REAL,
                macd_dea REAL,
                macd_macd REAL,
                bbi REAL,
                zhixing_long_line REAL,
                zhixing_short_line REAL,
                zhixing_bull_line REAL,
                zhixing_bear_line REAL,
                industry_sector TEXT,
                concept_sectors TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date, stock_code)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sector_daily_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                sector_type TEXT NOT NULL,  -- '行业' or '概念'
                sector_name TEXT NOT NULL,
                ranking INTEGER,
                change_percent REAL,
                constituent_stocks TEXT,  -- JSON格式存储成分股代码
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date, sector_type, sector_name)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sector_ranking_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sector_type TEXT NOT NULL,
                sector_name TEXT NOT NULL,
                period_days INTEGER NOT NULL,  -- 10, 15, 20
                top10_appearances INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(sector_type, sector_name, period_days)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS update_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                update_date TEXT NOT NULL,
                update_type TEXT NOT NULL,  -- 'daily', 'historical', 'sector'
                status TEXT NOT NULL,  -- 'success', 'failed', 'partial'
                records_count INTEGER DEFAULT 0,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_stock_date_code ON stock_daily_data(date, stock_code)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sector_date_type ON sector_daily_data(date, sector_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ranking_stats ON sector_ranking_stats(sector_type, period_days)')
        
        conn.commit()
        conn.close()
        print(f"数据库初始化完成: {self.db_path}")
    
    def get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)
    
    def execute_query(self, query, params=None):
        """执行查询"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def execute_insert(self, query, params):
        """执行插入操作"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if isinstance(params[0], (list, tuple)):
                cursor.executemany(query, params)
            else:
                cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
