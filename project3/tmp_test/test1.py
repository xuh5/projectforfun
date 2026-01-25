import pandas as pd
from finvizfinance.quote import finvizfinance
import yfinance as yf
import time

def batch_fetch_split_sheets(tickers):
    fv_results = []
    yf_results = []
    
    for t in tickers:
        print(f"正在抓取 {t}...")
        
        # 1. 抓 Finviz
        try:
            fv_data = finvizfinance(t).ticker_fundament()
            fv_data['ticker'] = t # 保证两个表都有索引好对照
            fv_results.append(fv_data)
        except:
            print(f"Finviz 抓取 {t} 失败")

        # 2. 抓 yfinance
        try:
            yf_info = yf.Ticker(t).info
            yf_info['ticker'] = t
            yf_results.append(yf_info)
        except:
            print(f"yfinance 抓取 {t} 失败")
            
        time.sleep(1.5) # 爬虫安全间隔

    # 转换成 DataFrame
    df_fv = pd.DataFrame(fv_results).set_index('ticker')
    df_yf = pd.DataFrame(yf_results).set_index('ticker')

    # --- 核心逻辑：分 Sheet 写入 ---
    with pd.ExcelWriter("stock_factors_split.xlsx") as writer:
        df_fv.to_excel(writer, sheet_name="Finviz_Factors")
        df_yf.to_excel(writer, sheet_name="YFinance_Data")
    
    print("\n[搞定] Excel 已分 Sheet 生成：stock_factors_split.xlsx")

# 测试 10 家
tickers_list = ['AAPL', 'TSLA', 'NVDA', 'MSFT', 'GOOGL', 'AMZN', 'META', 'BRK-B', 'UNH', 'JNJ']
batch_fetch_split_sheets(tickers_list)