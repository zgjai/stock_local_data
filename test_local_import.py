"""
测试本地JSON数据导入功能
"""

import json
import os
import tempfile
from stock_database import StockDatabase

def create_test_json_data():
    """创建测试用的JSON数据文件"""
    test_data = {
        "data": {
            "20231009": {
                "open": 12.77,
                "high": 13.08,
                "low": 12.2,
                "close": 12.68,
                "volume": 61386.0,
                "change_pct": 0.0,
                "kdj_j": 0,
                "macd": 0,
                "macd_histogram": 0,
                "bbi": 0,
                "bbi_angle": 0,
                "zhixing_short": 0,
                "zhixing_long": 0,
                "is_st": False,
                "is_windmill": False,
                "is_key_k": False,
                "highest": 13.08,
                "highest_date": "20231009",
                "second_highest": 13.08,
                "second_highest_date": "",
                "lowest": 12.2,
                "lowest_date": "20231009",
                "second_lowest": 12.2,
                "second_lowest_date": "",
                "highest_180": 13.08,
                "highest_date_180": "20231009",
                "second_highest_180": 13.08,
                "second_highest_date_180": "",
                "lowest_180": 12.2,
                "lowest_date_180": "20231009",
                "second_lowest_180": 12.2,
                "second_lowest_date_180": ""
            },
            "20231010": {
                "open": 12.73,
                "high": 12.81,
                "low": 12.52,
                "close": 12.75,
                "volume": 28842.0,
                "change_pct": 0.5520504731861222,
                "kdj_j": 0,
                "macd": 0,
                "macd_histogram": 0,
                "bbi": 0,
                "bbi_angle": 0,
                "zhixing_short": 0,
                "zhixing_long": 0,
                "is_st": False,
                "is_windmill": False,
                "is_key_k": False,
                "highest": 13.08,
                "highest_date": "20231009",
                "second_highest": 12.81,
                "second_highest_date": "20231010",
                "lowest": 12.2,
                "lowest_date": "20231009",
                "second_lowest": 12.52,
                "second_lowest_date": "20231010",
                "highest_180": 13.08,
                "highest_date_180": "20231009",
                "second_highest_180": 12.81,
                "second_highest_date_180": "20231010",
                "lowest_180": 12.2,
                "lowest_date_180": "20231009",
                "second_lowest_180": 12.52,
                "second_lowest_date_180": "20231010"
            }
        }
    }
    
    return test_data

def test_local_import():
    """测试本地数据导入功能"""
    print("=== 测试本地JSON数据导入功能 ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"创建临时测试目录: {temp_dir}")
        
        test_files = [
            ("000001_data.json", "000001"),
            ("000002_stock.json", "000002"),
            ("300001_info.json", "300001")
        ]
        
        test_data = create_test_json_data()
        
        for filename, stock_code in test_files:
            file_path = os.path.join(temp_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(test_data, f, ensure_ascii=False, indent=2)
            print(f"创建测试文件: {filename}")
        
        db = StockDatabase("test_local_import.db")
        
        print("\n开始导入测试数据...")
        success = db.import_local_data(temp_dir)
        print(f"导入结果: {success}")
        
        print("\n验证导入的数据:")
        for _, stock_code in test_files:
            stock_data = db.query_stock_data(stock_code, start_date='2023-10-01', end_date='2023-10-31')
            print(f"股票 {stock_code}: {len(stock_data)} 条记录")
            if not stock_data.empty:
                print(f"  日期范围: {stock_data['date'].min()} 到 {stock_data['date'].max()}")
                print(f"  价格范围: {stock_data['close_price'].min():.2f} - {stock_data['close_price'].max():.2f}")
        
        stats = db.get_database_stats()
        print(f"\n数据库统计: {stats}")
    
    if os.path.exists("test_local_import.db"):
        os.remove("test_local_import.db")
    
    print("\n测试完成!")

if __name__ == "__main__":
    test_local_import()
