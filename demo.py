"""
系统演示脚本
"""

from stock_database import StockDatabase
import pandas as pd

def main():
    print('=== A股股票市场基础数据库系统演示 ===')
    print('初始化数据库...')
    db = StockDatabase()

    print('\n获取数据库统计信息:')
    stats = db.get_database_stats()
    for key, value in stats.items():
        print(f'{key}: {value}')

    print('\n测试获取少量实时数据...')
    success = db._update_daily_stock_data()
    print(f'实时数据更新: {"成功" if success else "失败"}')

    print('\n查询最新数据样例:')
    data = db.query_stock_data(limit=5)
    if not data.empty:
        print(data[['date', 'stock_code', 'stock_name', 'close_price', 'volume']].to_string())
    else:
        print('暂无数据')

    print('\n测试板块数据获取...')
    sector_success = db._update_daily_sector_data()
    print(f'板块数据更新: {"成功" if sector_success else "失败"}')

    print('\n查询板块数据样例:')
    sector_data = db.query_sector_data(limit=5)
    if not sector_data.empty:
        print(sector_data[['date', 'sector_type', 'sector_name', 'ranking', 'change_percent']].to_string())
    else:
        print('暂无板块数据')

    print('\n系统演示完成!')

if __name__ == "__main__":
    main()
