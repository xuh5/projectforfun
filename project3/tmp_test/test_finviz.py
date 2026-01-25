"""
测试 Finviz Finance 获取科技股
运行: python tmp_test/test_finviz.py
"""

from finvizfinance.screener.overview import Overview

import pandas as pd
from finvizfinance.screener.overview import Overview
import time

def export_tech_stocks_to_excel():
    print("正在初始化 Finviz 筛选器...")
    # 1. 初始化筛选器
    f_screener = Overview()
    
    # 2. 设置行业大类为 Technology
    # 如果你想把 Google/Meta 所在的 Communication Services 也加上，
    # 需要分两次抓取再合并，这里先按你的要求抓 Technology
    filters_dict = {'Sector': 'Technology'}
    f_screener.set_filter(filters_dict=filters_dict)
    
    try:
        print("正在抓取数据，请稍候（数据量较大时会自动处理分页）...")
        # 3. 抓取数据
        # screener_view() 会自动处理 Finviz 的分页逻辑
        df = f_screener.screener_view()
        
        if df is None or df.empty:
            print("未抓取到数据，请检查网络或 Finviz 是否更新了反爬机制。")
            return

        # 4. 数据清理：只保留核心列（可选）
        # 默认列包含：Ticker, Company, Sector, Industry, Country, Market Cap, P/E, Price, Change, Volume
        
        # 5. 输出到 Excel
        file_name = f"Tech_Stocks_{time.strftime('%Y%m%d')}.xlsx"
        df.to_excel(file_name, index=False)
        
        print(f"✅ 成功！已抓取 {len(df)} 只科技股。")
        print(f"📂 文件已保存至: {file_name}")
        
    except Exception as e:
        print(f"❌ 运行出错: {e}")

if __name__ == "__main__":
    export_tech_stocks_to_excel()