from backtesting import Backtest, Strategy
from backtesting.lib import crossover

from backtesting.test import SMA
import pandas as pd
import pandas_ta as ta
import numpy as np


last = pd.read_csv('data/last.csv').ffill()
volume = pd.read_csv('data/volume.csv')
mkt_cap = pd.read_csv('data/mkt_cap.csv')
sector = pd.read_csv('data/sector.csv')
tickers = last['ticker'].unique()
last["t_days"] = last.groupby("ticker")["date"].cumcount()
JT1332 = last.loc[last["ticker"] == "1332 JT"]
JT1332.set_index("date", inplace=True)


class SmaCross(Strategy):
    def init(self):
        price = self.data["last"]
        self.ma1 = self.I(SMA, price, 10)
        self.ma2 = self.I(SMA, price, 20)

    def next(self):
        if crossover(self.ma1, self.ma2):
            self.buy()
        elif crossover(self.ma2, self.ma1):
            self.sell()


bt = Backtest(JT1332, SmaCross, commission=0.0,
              exclusive_orders=True)
stats = bt.run()
bt.plot()
