from backtesting import Backtest, Strategy
from backtesting.lib import crossover, resample_apply
import pandas as pd
import pandas_ta as ta
import numpy as np

last = pd.read_csv('data/last.csv').ffill()
volume = pd.read_csv('data/volume.csv')
mkt_cap = pd.read_csv('data/mkt_cap.csv')
sector = pd.read_csv('data/sector.csv')
tickers = last['ticker'].unique()
JT1332 = last.loc[last["ticker"] == "1332 JT"].drop(columns=['ticker'])
# JT1332["date"] = pd.to_datetime(JT1332["date"], format='%Y-%m-%d')
JT1332.set_index(pd.DatetimeIndex(JT1332["date"]), inplace=True)
JT1332.rename(columns={"last": "Close"}, errors="raise", inplace=True)
JT1332["Open"] = JT1332["Close"]
JT1332["High"] = JT1332["Close"]
JT1332["Low"] = JT1332["Close"]
# last["t_days"] = last.groupby("ticker")["date"].cumcount()

print(JT1332.head(10))


# JT1332.set_index("date", inplace=True)


class System(Strategy):
    d_rsi = 30  # Daily RSI lookback periods
    w_rsi = 30  # Weekly
    level = 70

    def init(self):
        self.price = self.data.Close
        # Compute moving averages the strategy demands
        self.ma10 = self.I(self.SMA, self.price, 10)
        self.ma20 = self.I(self.SMA, self.price, 20)
        self.ma50 = self.I(self.SMA, self.price, 50)
        self.ma100 = self.I(self.SMA, self.price, 100)

        # Compute daily RSI(30)
        self.daily_rsi = self.I(self.RSI, self.price, self.d_rsi)

        # To construct weekly RSI, we can use `resample_apply()`
        # helper function from the library
        self.weekly_rsi = resample_apply(
            'W-FRI', self.RSI, self.price, self.w_rsi)


    def next(self):
        price = self.data.Close[-1]

        # If we don't already have a position, and
        # if all conditions are satisfied, enter long.
        if (not self.position and
                self.daily_rsi[-1] > self.level and
                self.weekly_rsi[-1] > self.level and
                self.weekly_rsi[-1] > self.daily_rsi[-1] and
                self.ma100[-1] < self.ma50[-1] < self.ma20[-1] < self.ma10[-1] < price):

            # Buy at market price on next open, but do
            # set 8% fixed stop loss.
            self.buy(sl=.92 * price)

        # If the price closes 2% or more below 10-day MA
        # close the position, if any.
        elif price < .98 * self.ma10[-1]:
            self.position.close()

    # def SMA(self, n: int) -> pd.Series:
    #     """
    #     Returns `n`-period simple moving average of array `arr`.
    #     """
    #     # return ta.ema(self.close, n)
    #     print(self.close.head(10))
    #     return pd.Series(self.close).rolling(n).mean()
    #
    # def RSI(self, n: int) -> pd.Series:
    #     """
    #     Returns `n`-period simple moving average of array `arr`.
    #     """
    #     return ta.rsi(self.close, n)

    def SMA(self, array, n):
        """Simple moving average"""
        return pd.Series(array).rolling(n).mean()

    def RSI(self, array, n):
        """Relative strength index"""
        # Approximate; good enough
        gain = pd.Series(array).diff()
        loss = gain.copy()
        gain[gain < 0] = 0
        loss[loss > 0] = 0
        rs = gain.ewm(n).mean() / loss.abs().ewm(n).mean()
        return 100 - 100 / (1 + rs)


bt = Backtest(JT1332, System, commission=0.0,
              exclusive_orders=True)
stats = bt.run()
bt.plot()

# %%
