import requests
import pandas as pd

def get_nasdaq_tech_list():
    # 这是 Nasdaq 官网 Screener 的后台下载接口
    url = "https://api.nasdaq.com/api/screener/stocks?tableonly=true&limit=0&download=true"
    
    # ⚠️ 关键：必须模拟浏览器 Headers，否则会返回 403
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        json_data = response.json()
        # 提取 rows 列表
        rows = json_data['data']['rows']
        df = pd.DataFrame(rows)
        
        # 筛选行业（Nasdaq 的字段名为 sector）
        tech_df = df[df['sector'].str.contains("Technology", na=False, case=False)]
        return tech_df['symbol'].tolist()
    else:
        print(f"请求失败，错误码：{response.status_code}")
        return []

# 测试
tech_symbols = get_nasdaq_tech_list()
print(tech_symbols[:10])
print(len(tech_symbols))