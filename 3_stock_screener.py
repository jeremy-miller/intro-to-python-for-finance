# Stock screener based on the "Trade Like a Stock Market Wizard" book by Mark Minervini.

from datetime import date, timedelta

import pandas as pd
import yfinance as yf

stock_spreadsheet_filepath = "3_stocks.xlsx"

stocks = pd.read_excel(stock_spreadsheet_filepath)
stocks = stocks.head()  # limit to first 5 rows for testing

end_date = date.today()
start_date = end_date - timedelta(days=365)
simple_moving_averages_used = [50, 150, 200]
final_df = pd.DataFrame(
    columns=[
        "Stock",
        "Relative Strength Rating",
        "50 Day MA",
        "150 Day MA",
        "200 Day MA",
        "52 Week Low",
        "52 Week High",
    ]
)

for i in stocks.index:
    stock = stocks["Symbol"][i]
    relative_strength_rating = stocks["RS Rating"][i]

    try:
        df = yf.download(stock, start=start_date, end=end_date)
    except Exception:
        print(f'No data for "{stock}"')
        continue

    for sma in simple_moving_averages_used:
        df[f"SMA_{sma}"] = round(df["Adj Close"].rolling(window=sma).mean(), 2)
    current_close = df["Adj Close"].iloc[-1]
    moving_average_50 = df["SMA_50"].iloc[-1]
    moving_average_150 = df["SMA_150"].iloc[-1]
    moving_average_200 = df["SMA_200"].iloc[-1]
    low_52_week = round(min(df["Adj Close"][-260:]), 2)  # 260 trading days in a year
    high_52_week = round(max(df["Adj Close"][-260:]), 2)  # 260 trading days in a year
    try:
        moving_average_200_20_days_ago = df["SMA_200"].iloc[-20]  # 20 trading days in a month
    except Exception:
        moving_average_200_20_days_ago = 0

    # Condition 1: Current Price > 150 SMA and > 200 SMA
    if current_close > moving_average_150 and current_close > moving_average_200:
        condition_1 = True
    else:
        condition_1 = False

    # Condition 2: 150 SMA > 200 SMA
    if moving_average_150 > moving_average_200:
        condition_2 = True
    else:
        condition_2 = False

    # Condition 3: 200 SMA trending up for at least 1 month (ideally 4-5 months)
    if moving_average_200 > moving_average_200_20_days_ago:
        condition_3 = True
    else:
        condition_3 = False

    # Condition 4: 50 SMA > 150 SMA and 50 SMA > 200 SMA
    if moving_average_50 > moving_average_150 and moving_average_50 > moving_average_200:
        condition_4 = True
    else:
        condition_4 = False

    # Condition 5: Current Price > 50 SMA
    if current_close > moving_average_50:
        condition_5 = True
    else:
        condition_5 = False

    # Condition 6: Current Price is at least 30% above 52 week low
    #   (Many of the best are up 100-300% before coming out of consolidation)
    if current_close > 1.3 * low_52_week:
        condition_6 = True
    else:
        condition_6 = False

    # Condition 7: Current Price is within 25% of 52 week high
    if current_close >= 0.75 * high_52_week:
        condition_7 = True
    else:
        condition_7 = False

    # Condition 8: Investor's Business Daily "Relative Strength" rating >70 and the higher the better
    if relative_strength_rating > 70:
        condition_8 = True
    else:
        condition_8 = False

    if (
        condition_1
        and condition_2
        and condition_3
        and condition_4
        and condition_5
        and condition_6
        and condition_7
        and condition_8
    ):
        final_df.loc[len(final_df)] = [
            stock,
            relative_strength_rating,
            moving_average_50,
            moving_average_150,
            moving_average_200,
            low_52_week,
            high_52_week,
        ]

print(f"\n{final_df}\n")
