from backtesting.test import GOOG
import pandas as pd
from backtesting import Strategy
from backtesting.lib import crossover
from backtesting import Backtest
import yfinance as yf

GOOG.tail()
BTC = yf.download("BTC-USD", start="2022-06-05", end="2022-07-30", interval="5m")

def SMA(values, n):
    """
    Return simple moving average of `values`, at
    each step taking into account `n` previous values.
    """
    return pd.Series(values).rolling(n).mean()


def EMA(values, n):
    """
    Return exponential moving average of `values`, at
    each step taking into account `n` previous values.
    """
    return pd.Series(values).ewm(span=n, min_periods=n).mean()


def BollingerBands(values, n):
    """
    Return Bollinger Bands of `values`, at
    each step taking into account `n` previous values.
    """
    sma = SMA(values, n)
    std = pd.Series(values).rolling(n).std()
    upper_band = sma + (2 * std)
    lower_band = sma - (2 * std)
    return upper_band, lower_band, sma


def RSI(values, n):
    """
    Return Relative Strength Index of `values`, at
    each step taking into account `n` previous values.
    """
    delta = pd.Series(values).diff()
    dUp, dDown = delta.copy(), delta.copy()
    dUp[dUp < 0] = 0
    dDown[dDown > 0] = 0
    RollingUp = dUp.rolling(n).mean()
    RollingDown = dDown.abs().rolling(n).mean()
    RS = RollingUp / RollingDown
    RSI = 100 - (100 / (1 + RS))
    return RSI




class SmaCross(Strategy):
    # Define the two MA lags as *class variables*
    # for later optimization
    n1 = 30
    n2 = 70
    n3 = 10
    n4 = 200

    def init(self):
        # Precompute the two moving averages
        self.sma1 = self.I(SMA, self.data.Close, self.n4)
        self.sma2 = self.I(EMA, self.data.Close, self.n2)
        self.bb = self.I(BollingerBands, self.data.Close, self.n1)
        self.rsi = self.I(RSI, self.data.Close, self.n3)

    def next(self):
        # If sma1 crosses above sma2, close any existing
        # short trades, and buy the asset
        pass
        if self.rsi < self.n1 and self.sma1<self.data.Close and self.position.size == 0:
            self.buy()

        # Else, if sma1 crosses below sma2, close any existing
        # long trades, and sell the asset
        elif self.rsi > self.n2 and self.data.Close < self.sma1 and self.position.size == 0:
            self.sell()

        elif 40 < self.rsi < 60 :
            self.position.close()



bt = Backtest(BTC, SmaCross, cash=100_000, commission=.002)
stats = bt.run()
print(stats)

stats = bt.optimize(n1=range(5, 30, 5),
                    n2=range(70, 95, 5),
                    n4=range(100, 200, 10),
                    maximize='Equity Final [$]')
print(stats, stats._strategy)



