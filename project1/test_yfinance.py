
import yfinance as yf

try:
    ticker = yf.Ticker("AAPL")
    print("Fast Info keys:", ticker.fast_info.keys())
    # fast_info doesn't usually have name.
    # Let's check info
    print("Info name:", ticker.info.get('longName'))
except Exception as e:
    print(e)

