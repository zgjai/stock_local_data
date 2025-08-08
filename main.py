"""
主程序入口 - 演示系统功能
"""

import sys
import os
from datetime import datetime, timedelta
from stock_database import StockDatabase

def main():
    print("=== A股股票市场基础数据库系统 ===")
    print("初始化系统...")
    
    db = StockDatabase()
    
    while True:
        print("\n请选择操作:")
        print("1. 初始化历史数据（过去一年）")
        print("2. 日常数据更新")
        print("3. 查询个股数据")
        print("4. 查询板块数据")
        print("5. 查询板块排名统计")
        print("6. 查看数据库统计")
        print("7. 清空所有数据")
        print("8. 退出")
        
        choice = input("\n请输入选择 (1-8): ").strip()
        
        if choice == '1':
            print("\n开始初始化历史数据...")
            days = input("请输入要获取的历史天数 (默认365天): ").strip()
            days = int(days) if days.isdigit() else 365
            
            success = db.initialize_historical_data(days)
            if success:
                print("✓ 历史数据初始化完成")
            else:
                print("✗ 历史数据初始化失败")
        
        elif choice == '2':
            print("\n开始日常数据更新...")
            success = db.daily_update()
            if success:
                print("✓ 日常数据更新完成")
            else:
                print("✗ 日常数据更新失败")
        
        elif choice == '3':
            print("\n查询个股数据")
            stock_code = input("请输入股票代码 (如000001，留空查询所有): ").strip()
            start_date = input("请输入开始日期 (YYYY-MM-DD，留空不限制): ").strip()
            limit = input("请输入查询条数限制 (留空不限制): ").strip()
            
            stock_code = stock_code if stock_code else None
            start_date = start_date if start_date else None
            limit = int(limit) if limit.isdigit() else None
            
            data = db.query_stock_data(stock_code, start_date, limit=limit)
            
            if not data.empty:
                print(f"\n查询到 {len(data)} 条记录:")
                print(data[['date', 'stock_code', 'stock_name', 'close_price', 
                          'volume', 'zhixing_long_line', 'zhixing_short_line']].head(10))
            else:
                print("未查询到数据")
        
        elif choice == '4':
            print("\n查询板块数据")
            sector_type = input("请输入板块类型 (行业/概念，留空查询所有): ").strip()
            start_date = input("请输入开始日期 (YYYY-MM-DD，留空不限制): ").strip()
            limit = input("请输入查询条数限制 (留空不限制): ").strip()
            
            sector_type = sector_type if sector_type else None
            start_date = start_date if start_date else None
            limit = int(limit) if limit.isdigit() else None
            
            data = db.query_sector_data(sector_type, start_date, limit=limit)
            
            if not data.empty:
                print(f"\n查询到 {len(data)} 条记录:")
                print(data[['date', 'sector_type', 'sector_name', 'ranking', 'change_percent']].head(10))
            else:
                print("未查询到数据")
        
        elif choice == '5':
            print("\n查询板块排名统计")
            period = input("请输入统计周期 (10/15/20天，留空查询所有): ").strip()
            min_appearances = input("请输入最小出现次数 (默认1): ").strip()
            
            period = int(period) if period.isdigit() else None
            min_appearances = int(min_appearances) if min_appearances.isdigit() else 1
            
            data = db.query_sector_rankings(period, min_appearances)
            
            if not data.empty:
                print(f"\n查询到 {len(data)} 条记录:")
                print(data[['sector_type', 'sector_name', 'period_days', 'top10_appearances']].head(10))
            else:
                print("未查询到数据")
        
        elif choice == '6':
            print("\n数据库统计信息:")
            stats = db.get_database_stats()
            for key, value in stats.items():
                print(f"{key}: {value}")
        
        elif choice == '7':
            print("\n警告: 此操作将清空所有数据库数据!")
            confirm = input("确认清空所有数据? (输入 'YES' 确认): ").strip()
            if confirm == 'YES':
                success = db.clear_all_data()
                if success:
                    print("✓ 数据清空完成")
                else:
                    print("✗ 数据清空失败")
            else:
                print("操作已取消")
        
        elif choice == '8':
            print("退出系统")
            break
        
        else:
            print("无效选择，请重新输入")

if __name__ == "__main__":
    main()
