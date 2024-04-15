from datetime import datetime

import numpy as np
import pandas as pd
import yfinance as yf

stock = input("Enter a stock ticker symbol: ")

start_year = 2024
start_month = 1
start_day = 1
start_date = datetime(start_year, start_month, start_day)
end_date = datetime.now()

df = yf.download(stock, start=start_date, end=end_date)

moving_average_window = 50  # days
simple_moving_average = f"SMA_{moving_average_window}"
df[simple_moving_average] = df["Adj Close"].rolling(window=moving_average_window).mean()
df.dropna(inplace=True)  # drop first {moving_average_window} days

num_higher = 0
num_lower = 0
for i in df.index:
    if df["Adj Close"][i] > df[simple_moving_average][i]:
        num_higher += 1
    else:
        num_lower += 1
print(f"num_higher: {num_higher}, num_lower: {num_lower}")
