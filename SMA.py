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
# tickers = ["1721 JT"]

list_of_stocks = []
for ticker in tickers:
    instrument = last.loc[last["ticker"] == ticker].drop(columns=['ticker'])
    instrument.set_index(pd.DatetimeIndex(pd.to_datetime(instrument["date"])), inplace=True)
    instrument.rename(columns={"last": "Close"}, errors="raise", inplace=True)
    instrument["Open"] = instrument["Close"]
    instrument["High"] = instrument["Close"]
    instrument["Low"] = instrument["Close"]
    list_of_stocks.append(instrument)


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


stock_returns = pd.DataFrame(index=tickers, columns=['Strat Return', 'Hold Return'])
for ticker, stock in zip(tickers, list_of_stocks):
    bt = Backtest(stock, SMAStrat, commission=0.0,
                  exclusive_orders=True, cash=1_000_000)
    stats = bt.run()
    stock_returns.loc[ticker] = (stats["Return [%]"], stats["Buy & Hold Return [%]"])
    # print(stats)
    # bt.plot()


print(stock_returns)
print("Average strat return:", stock_returns['Strat Return'].mean())
print("Average hold return:", stock_returns['Hold Return'].mean())


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