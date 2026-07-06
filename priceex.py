import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os
import openpyxl

tickers = [
    'AAPL',
    'NVDA',
    'NDX',
    'NQ=F',
    'EURUSD=X']

end_date = datetime.today()
print(end_date)

start_date = end_date - timedelta(days = 3*365)
print(start_date)

close_df = pd.DataFrame()

for ticker in tickers:
    data = yf.download(ticker, start = start_date, end = end_date)
    close_df[ticker] = data['Close']
    print(close_df)

output_folder = r"C:\Users\Rezqy\Documents\8. Projects\am"
output_file = os.path.join(output_folder, 'stock_prices.xlsx')
close_df.to_excel(output_file)
