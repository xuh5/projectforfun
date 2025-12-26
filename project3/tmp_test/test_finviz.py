"""
测试 Finviz Finance 获取科技股
运行: python tmp_test/test_finviz.py
"""

from finvizfinance.screener.overview import Overview


from finvizfinance.screener.overview import Overview

def get_tech_stocks():
    # 1. 初始化筛选器
    f_screener = Overview()
    
    # 2. 设置行业为 Technology
    # 根据 2025 最新文档，filter 的 key 为 'Sector'，value 为 'Technology'
    filters_dict = {'Sector': 'Technology'}
    f_screener.set_filter(filters_dict=filters_dict)
    
    # 3. 获取数据表
    # 注意：Finviz 有反爬，建议增加 sleep_sec 避免 IP 被封
    df = f_screener.screener_view()
    
    # 4. 提取 Ticker 列
    return df
    if not df.empty:
        return df['Ticker'].tolist()
    return []

# 测试输出
symbols = get_tech_stocks()
print(f"当前共抓取到 {len(symbols)} 只科技股。")
print(symbols)