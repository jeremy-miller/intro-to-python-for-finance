from datetime import date, timedelta

import yfinance as yf

stock = input("Enter a stock ticker symbol: ")
print()

end_date = date.today()
start_date = end_date - timedelta(days=365)

df = yf.download(stock, start=start_date, end=end_date)
print()

exponential_moving_averages = [3, 5, 8, 10, 12, 15, 30, 35, 40, 45, 50, 60]

for ema in exponential_moving_averages:
    df[f"EMA_{ema}"] = round(df["Adj Close"].ewm(span=ema, adjust=False).mean(), 2)

entered_position = False
row = 0
percent_change = []
for i in df.index:
    short_term_ema_min = min(
        df["EMA_3"][i],
        df["EMA_5"][i],
        df["EMA_8"][i],
        df["EMA_10"][i],
        df["EMA_12"][i],
        df["EMA_15"][i],
    )
    long_term_ema_max = max(
        df["EMA_30"][i],
        df["EMA_35"][i],
        df["EMA_40"][i],
        df["EMA_45"][i],
        df["EMA_50"][i],
        df["EMA_60"][i],
    )
    close = df["Adj Close"][i]

    if short_term_ema_min > long_term_ema_max:
        if not entered_position:
            buy_price = close
            entered_position = True
            print(f"Buying at: ${round(buy_price, 2)}")
    elif short_term_ema_min < long_term_ema_max:
        if entered_position:
            sell_price = close
            entered_position = False
            print(f"Selling at: ${round(sell_price, 2)}")
            percent = (sell_price / buy_price - 1) * 100
            percent_change.append(percent)
    # sell at end of data if still have position
    if row == df["Adj Close"].count() - 1 and entered_position:
        sell_price = close
        entered_position = False
        print(f"Selling at: ${round(sell_price, 2)}")
        percent = (sell_price / buy_price - 1) * 100
        percent_change.append(percent)
    row += 1


gains = 0
num_gains = 0
losses = 0
num_losses = 0
total_return = 1
for i in percent_change:
    if i > 0:
        gains += i
        num_gains += 1
    else:
        losses += i
        num_losses += 1
    total_return = total_return * ((i / 100) + 1)

total_return = round((total_return - 1) * 100, 2)

if num_gains > 0:
    average_gain = gains / num_gains
    max_gain = max(percent_change)
else:
    average_gain = 0
    max_gain = 0

if num_losses > 0:
    average_loss = losses / num_losses
    max_loss = min(percent_change)
    ratio = -average_gain / average_loss
else:
    average_loss = 0
    max_loss = 0
    ratio = "inf"

if num_gains > 0 or num_losses > 0:
    success_rate = num_gains / (num_gains + num_losses)
else:
    success_rate = 0

print(
    f'\nResults for "{stock}" from {df.index[0].strftime("%m/%d/%y")} - '
    f'{df.index[-1].strftime("%m/%d/%y")}, Sample Size: {num_gains + num_losses} Trades'
)
print(f"Exponential Moving Averages Used: {', '.join(str(n) for n in exponential_moving_averages)}")
print(f"Success Rate: {round(success_rate * 100, 2)}%")
print(f"Gain/loss Ratio: {round(ratio, 2) if isinstance(ratio, float) else ratio}")
print(f"Average Gain: {round(average_gain, 2)}%")
print(f"Max Gain: {round(max_gain, 2)}%")
print(f"Average Loss: {round(average_loss, 2)}%")
print(f"Max Loss: {round(max_loss, 2)}%")
print(f"Total Return Over {num_gains + num_losses} Trades: {total_return}%\n")
