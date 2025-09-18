#%%
import pandas as pd
from backtesting import Backtest, Strategy
from backtesting.lib import crossover, cross
from backtesting.test import SMA
import ta
from import_tools import get_data_from_profit
import multiprocessing
import matplotlib as plt
#%%
multiprocessing.set_start_method("fork")




#%%
## Read the file to a Dataframe
milho = get_data_from_profit('CCM_240')
milho.info()


#%%



#%%
milho['HighMa15'] = milho['High'].rolling(20).mean()
milho['LowMa15'] = milho['Low'].rolling(20).mean()
milho['Compra'] = (milho['Close']) >= (milho['HighMa15'].shift(1))
milho['Venda'] = (milho['Close']) <= (milho['LowMa15'].shift(1))
milho.head(50)


# %%
class HiLoStrategy(Strategy):
    n = 3
    def init(self):
        high = self.data.High
        low = self.data.Low
        self.smahigh = self.I(SMA, high,self.n)
        self.smalow = self.I(SMA, low, self.n)
    def next(self):
        close = self.data.Close
           
        if close > self.smahigh :
            if self.position.is_short:
                self.position.close()
                self.buy()
            elif not self.position:
                self.buy()
           
        elif close < self.smalow:
            if self.position.is_long:
                self.position.close()
                self.sell()
            elif not self.position:
                self.sell()    
         
   
                
            
        
        
#%%
bt = Backtest(milho, HiLoStrategy, cash = 10000, commission=0.0002)
stats = bt.run()
print(stats)
bt.plot()

#%%
if __name__ == '__main__':
    stats, heatmap = bt.optimize(
    n = range(1,50,1),
    maximize='Profit Factor',
    max_tries= 100,
    return_heatmap= True
    ) 

#%%
bt.plot()
heatmap.plot()
print(stats)
    
    
    


# %%
