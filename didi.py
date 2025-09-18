from backtesting import Backtest, Strategy

import talib 
import yfinance as yf


def stop_loss_gain(price, stop_loss, take_profit, order_type: str):
    if order_type == 'buy':
        stop_loss = price - (price * stop_loss / 100) 
        take_profit = price + (price * take_profit / 100)
        return stop_loss, take_profit
    else:
        stop_loss = price + (price * stop_loss / 100) 
        take_profit = price - (price * take_profit / 100)
        return stop_loss, take_profit
        


def didi_index(close, slow=20, normal=8, fast=5):
    """
    DIDI Index 
    Return didi_fast & didi_slow
    """
    
    slow_ma = talib.SMA(close, slow)
    normal_ma = talib.SMA(close, normal)
    fast_ma = talib.SMA(close, fast)
    didi_fast = fast_ma - normal_ma
    didi_slow = slow_ma - normal_ma
    return  didi_fast, didi_slow


def adx_ind(data, period = 8):
    di_plus  = talib.PLUS_DI(data.High, data.Low, data.Close, timeperiod=period)
    di_minus = talib.MINUS_DI(data.High, data.Low, data.Close, timeperiod=period)
    adx = talib.ADX(data.High, data.Low, data.Close, timeperiod=period)
    
    return di_plus, di_minus, adx


def trix_indicator(close, period=9):
    """
    TRIX indicator - Triple Exponential Average rate of change
    """
    trix = talib.TRIX(close, timeperiod=period)
    return trix


def stochastic_indicator(data, k_period=8, d_period=3):
    """
    Stochastic Oscillator indicator
    Returns %K and %D lines
    """
    slowk, slowd = talib.STOCH(data.High, data.Low, data.Close, 
                               fastk_period=k_period, 
                               slowk_period=d_period, 
                               slowd_period=d_period)
    return slowk, slowd


def bollinger_indicator(close, period=8, std_dev=2):
    """
    Bollinger Bands indicator
    Returns upper band, middle band (SMA), and lower band
    """
    upper, middle, lower = talib.BBANDS(close, 
                                        timeperiod=period, 
                                        nbdevup=std_dev, 
                                        nbdevdn=std_dev)
    return upper, middle, lower

class StrategyAgulhada(Strategy):
    def init(self):
        self.di_plus, self.di_minus, self.adx  = self.I(adx_ind, self.data)
        close = self.data.Close
        
    def next(self):
        if(
            self.di_plus[-1] > self.di_minus[-1]
            
        ):
            self.position.close()
            self.buy()
    
ticker = yf.Ticker('BPAC11.SA')
data = ticker.history(period='10y', interval='1d')


bt = Backtest(data, StrategyAgulhada, cash=10000)
stats = bt.run()
print(stats)
bt.plot()

    
        