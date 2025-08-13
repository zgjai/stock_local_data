"""
测试板块数据更新和成分股获取分离功能
"""

from stock_database import StockDatabase
import logging

logging.basicConfig(level=logging.INFO)

def test_sector_data_separation():
    """测试板块数据分离功能"""
    db = StockDatabase("test_separation.db")
    
    print("=== 测试1: 日常板块数据更新（不包含成分股） ===")
    success = db._update_daily_sector_data()
    print(f"日常板块数据更新结果: {success}")
    
    sector_data = db.query_sector_data(limit=5)
    print(f"板块数据条数: {len(sector_data)}")
    if not sector_data.empty:
        print("成分股数据示例:")
        for _, row in sector_data.head(3).iterrows():
            constituents = row['constituent_stocks']
            print(f"  {row['sector_name']}: {constituents}")
    
    print("\n=== 测试2: 独立更新成分股数据 ===")
    success = db.update_sector_constituents(sector_type='行业')
    print(f"成分股更新结果: {success}")
    
    sector_data_after = db.query_sector_data(sector_type='行业', limit=3)
    if not sector_data_after.empty:
        print("更新后的成分股数据示例:")
        for _, row in sector_data_after.iterrows():
            constituents = row['constituent_stocks']
            print(f"  {row['sector_name']}: {constituents}")
    
    print("\n=== 测试3: 完整更新（包含成分股） ===")
    success = db.update_sector_data_with_constituents()
    print(f"完整更新结果: {success}")
    
    import os
    if os.path.exists("test_separation.db"):
        os.remove("test_separation.db")
    
    print("测试完成!")

if __name__ == "__main__":
    test_sector_data_separation()
