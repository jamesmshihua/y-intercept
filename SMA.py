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


class SMAStrat(Strategy):
    # Define the two MA lags as *class variables*
    # for later optimization
    n1 = 10
    n2 = 20
    
    def init(self):
        # Precompute the two moving averages
        self.sma1 = self.I(self.SMA, self.data.Close, self.n1)
        self.sma2 = self.I(self.SMA, self.data.Close, self.n2)
    
    def next(self):
        # If sma1 crosses above sma2, close any existing
        # short trades, and buy the asset
        if crossover(self.sma1, self.sma2):
            self.position.close()
            self.buy()

        # Else, if sma1 crosses below sma2, close any existing
        # long trades, and sell the asset
        elif crossover(self.sma2, self.sma1):
            self.position.close()
            self.sell()

    def SMA(self, array, n):
        """Simple moving average"""
        return pd.Series(array).rolling(n).mean()


bt = Backtest(JT1332, SMAStrat, commission=0.0,
              exclusive_orders=True)
stats = bt.run()
print("Before optimization")
print(stats)
print("\n\n")
bt.plot()

stats, heatmap = bt.optimize(n1=range(6,15), n2=range(15,25), 
                             constraint=lambda p: p.n1 < p.n2,
                             maximize="Return [%]", 
                             max_tries=500, random_state=0, return_heatmap=True)

print("After optimization")
print(stats)
print("Optimized strategy")
print(stats._strategy)

import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

# Convert multiindex series to dataframe
heatmap_df = heatmap.unstack()
plt.figure(figsize=(10, 8))
sns.heatmap(heatmap_df, annot=True, cmap='viridis', fmt='.0f')
plt.show()

# It seems that (11,20) is the best combination