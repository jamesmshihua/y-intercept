from backtesting import Backtest, Strategy
from backtesting.lib import crossover, resample_apply
import pandas as pd
import pandas_ta as ta
import numpy as np
from matplotlib import pyplot as plt

last = pd.read_csv('data/last.csv').ffill()
volume = pd.read_csv('data/volume.csv')
mkt_cap = pd.read_csv('data/mkt_cap.csv')
sector = pd.read_csv('data/sector.csv')
last["t_days"] = last.groupby("ticker")["date"].cumcount()
tickers = last['ticker'].unique()

list_of_stocks = []
for ticker in tickers:
    instrument = last.loc[last["ticker"] == ticker].drop(columns=['ticker'])
    instrument.set_index(pd.DatetimeIndex(pd.to_datetime(instrument["date"])), inplace=True)
    instrument.rename(columns={"last": "Close"}, errors="raise", inplace=True)
    instrument["Open"] = instrument["Close"]
    instrument["High"] = instrument["Close"]
    instrument["Low"] = instrument["Close"]
    list_of_stocks.append(instrument)



class AdaMACDStrat(Strategy):
    # Define the two MA lags as *class variables*
    # for later optimization
    short_window = 12
    long_window = 26
    signal_window = 9
    adaptive_period = 30
    smoothing_factor = 0.5

    def init(self):
        # Precompute the two moving averages
        self.macd = self.I(self.AdaMACD, self.data["Close"],
                           self.short_window, self.long_window, self.adaptive_period, self.smoothing_factor
                           )
        self.signal = self.I(self.AdaMACDSig, self.macd, self.signal_window)

    def next(self):
        # If sma1 crosses above sma2, close any existing
        # short trades, and buy the asset
        if crossover(self.macd, self.signal):
            self.position.close()
            self.buy()

        # Else, if sma1 crosses below sma2, close any existing
        # long trades, and sell the asset
        elif crossover(self.signal, self.macd):
            self.position.close()
            self.sell()

    def AdaMACD(self, price, short_window=12, long_window=26, adaptive_period=30, smoothing_factor=0.5):
        # Ultimate MACD
        price = pd.Series(price)
        # macd = pd.Series(index=price.index).fillna(value=0)
        # a1 = 2 / (fast + 1)
        # a2 = 2 / (slow + 1)

        # # r2 = 0.5 * np.power(ta.CORREL(close, np.arange(len(close)), length), 2) + 0.5
        # r2 = 0.5 * np.power(price.rolling(length).corr(counter), 2) + 0.5
        # K = r2 * ((1 - a1) * (1 - a2)) + (1 - r2) * ((1 - a1) / (1 - a2))
        # K.fillna(value=0, inplace=True)

        # for i in range(2, len(macd)):
        #     macd.iloc[i] = (price.iloc[i] - price.iloc[i-1]) * (a1 - a2) + (-a2 - a1 + 2) * macd.iloc[i-1] - K.iloc[i] * macd.iloc[i-2]

        # return macd

        ema_short = ta.ema(price, short_window)
        ema_long = ta.ema(price, long_window)

        volatility = price.rolling(window=adaptive_period).std()

        macd_line = ema_short - ema_long
        adaptive_factor = 2.0 / (adaptive_period + 1)
        adaptive_macd_line = (
                smoothing_factor * macd_line +
                (1 - smoothing_factor) * adaptive_factor * macd_line / volatility
        )

        return adaptive_macd_line

    def AdaMACDSig(self, adaptive_macd_line, signal_window=9):
        adaptive_signal_line = ta.ema(pd.Series(adaptive_macd_line), signal_window)
        return adaptive_signal_line


stock_returns = pd.DataFrame(index=tickers, columns=['Strat Return', 'Hold Return'])
for ticker, stock in zip(tickers, list_of_stocks):
    bt = Backtest(stock, AdaMACDStrat, commission=0.0,
                  exclusive_orders=True, cash=1_000_000)
    stats = bt.run()
    stock_returns.loc[ticker] = (stats["Return [%]"], stats["Buy & Hold Return [%]"])
    # print(stats)
    # bt.plot()


print(stock_returns)
print("Average strat return:", stock_returns['Strat Return'].mean())
print("Average strat return:", stock_returns['Hold Return'].mean())

