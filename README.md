# A股股票市场基础数据库系统

本系统是一个完整的A股股票市场数据获取、存储和查询系统，支持日级别数据更新和历史数据初始化。

## 功能特性

### 数据获取更新模块
- 基于akshare库获取实时股票数据
- 获取历史股票数据（支持过去一年数据初始化）
- 获取行业板块和概念板块数据
- 计算技术指标（KDJ、MACD、BBI）
- 模拟特殊技术指标（知行合一长短线、知行合一多空线）

### 数据存储模块
- 基于SQLite数据库存储
- 个股数据表
- 板块数据表
- 板块排名数据表
- 提供数据写入更新和查询能力

## 数据结构

### 个股数据
- 日期、股票代码、股票名称
- 总市值、流通市值
- OHLC价格、成交量
- 技术指标（KDJ、MACD、BBI）
- 特殊技术指标（知行合一长短线、知行合一多空线）
- 行业板块、概念板块

### 板块数据
- 日期、板块类型（行业/概念）
- 板块名称、涨幅排名
- 板块内个股代码

### 板块排名数据
- 最近10/15/20个交易日中出现在TOP10涨幅的板块及次数

## 使用方法

```python
from stock_database import StockDatabase

# 初始化数据库
db = StockDatabase()

# 初始化历史数据（过去一年）
db.initialize_historical_data()

# 日常数据更新（不包含板块成分股）
db.daily_update()

# 独立更新板块成分股数据
db.update_sector_constituents()  # 更新所有板块成分股
db.update_sector_constituents(sector_type='行业')  # 只更新行业板块成分股
db.update_sector_constituents(sector_names=['银行', '保险'])  # 更新指定板块成分股

# 完整更新板块数据（包含成分股，用于初始化或完整同步）
db.update_sector_data_with_constituents()

# 查询个股数据
stock_data = db.query_stock_data('000001', start_date='2024-01-01')

# 查询板块数据
sector_data = db.query_sector_data('行业', start_date='2024-01-01')
```

## 数据源

本系统使用akshare库作为数据源，包括：
- 实时股票数据：stock_zh_a_spot_em
- 历史股票数据：stock_zh_a_hist
- 行业板块数据：stock_board_industry_name_em, stock_board_industry_cons_em
- 概念板块数据：stock_board_concept_name_em, stock_board_concept_cons_em
