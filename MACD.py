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
JT1332.set_index(pd.DatetimeIndex(pd.to_datetime(JT1332["date"])), inplace=True)
JT1332.rename(columns={"last": "Close"}, errors="raise", inplace=True)
JT1332["Open"] = JT1332["Close"]
JT1332["High"] = JT1332["Close"]
JT1332["Low"] = JT1332["Close"]
# last["t_days"] = last.groupby("ticker")["date"].cumcount()

# print(JT1332.head(10))


class MACDStrat(Strategy):
    # Define the two MA lags as *class variables*
    # for later optimization
    n1 = 12
    n2 = 26
    n3 = 9

    def init(self):
        # Precompute the two moving averages
        self.price = self.data.Close
        self.macd = self.I(self.MACD, self.price, self.n1, self.n2)
        self.signal = self.I(self.SIG, self.macd, self.n3)

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

    def MACD(self, price, short_window=12, long_window=26):
        # Calculate the short-term exponential moving average (EMA)
        ema_short = ta.ema(pd.Series(price), short_window)

        # Calculate the long-term exponential moving average (EMA)
        ema_long = ta.ema(pd.Series(price), long_window)

        # Calculate the MACD line
        macd_line = ema_short - ema_long

        return macd_line
    
    def SIG(self, macd_line, signal_window=9):
        # Calculate the signal line (EMA of MACD line)
        signal_line = ta.ema(pd.Series(macd_line), signal_window)
        
        return signal_line


# class SMAStrat(Strategy):
#     # Define the two MA lags as *class variables*
#     # for later optimization
#     n1 = 10
#     n2 = 20
    
#     def init(self):
#         # Precompute the two moving averages
#         self.sma1 = self.I(self.SMA, self.data.Close, self.n1)
#         self.sma2 = self.I(self.SMA, self.data.Close, self.n2)
    
#     def next(self):
#         # If sma1 crosses above sma2, close any existing
#         # short trades, and buy the asset
#         if crossover(self.sma1, self.sma2):
#             self.position.close()
#             self.buy()

#         # Else, if sma1 crosses below sma2, close any existing
#         # long trades, and sell the asset
#         elif crossover(self.sma2, self.sma1):
#             self.position.close()
#             self.sell()

#     def SMA(self, array, n):
#         """Simple moving average"""
#         return pd.Series(array).rolling(n).mean()


bt = Backtest(JT1332, MACDStrat, commission=0.0,
              exclusive_orders=True)
stats = bt.run()
print(stats)
bt.plot()

#%%
