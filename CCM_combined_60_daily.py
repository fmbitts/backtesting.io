#%%
import pandas as pd
from backtesting import Backtest, Strategy
from backtesting.lib import crossover, cross
from backtesting.test import SMA
import ta
from import_tools import get_data_from_profit
import multiprocessing
import matplotlib as plt
import numpy as np

#%%
multiprocessing.set_start_method("fork")

#%%
## Load both timeframes
data_60 = get_data_from_profit('CCM_60')
data_daily = get_data_from_profit('CCM_daily')

print("60-minute data shape:", data_60.shape)
print("Daily data shape:", data_daily.shape)

#%%
# Calculate daily HiLo signals
def calculate_hilo_signal(data, n):
    """
    Calculate HiLo signals for a given timeframe
    Returns: 1 for long, -1 for short, 0 for no signal
    """
    sma_high = data['High'].rolling(window=n).mean()
    sma_low = data['Low'].rolling(window=n).mean()

    # Create signal column
    signal = pd.Series(0, index=data.index)
    signal[data['Close'] > sma_high] = 1  # Long signal
    signal[data['Close'] < sma_low] = -1   # Short signal

    return signal

#%%
# Merge daily signals into 60-minute data
def prepare_combined_data(data_60min, data_daily, n_60=3, n_daily=3):
    """
    Prepare combined dataset with signals from both timeframes
    """
    # Calculate signals for both timeframes
    daily_signal = calculate_hilo_signal(data_daily, n_daily)
    daily_signal.name = 'Daily_Signal'

    # Merge daily signal into 60-minute data (forward fill to propagate daily signal)
    combined = data_60min.copy()
    combined = combined.join(daily_signal, how='left')
    combined['Daily_Signal'] = combined['Daily_Signal'].fillna(method='ffill')

    return combined

#%%
# Prepare the combined dataset
milho_combined = prepare_combined_data(data_60, data_daily, n_60=3, n_daily=3)
print("\nCombined data shape:", milho_combined.shape)
print(milho_combined[['Close', 'Daily_Signal']].tail(20))

#%%
class MultiTimeframeHiLoStrategy(Strategy):
    """
    Multi-timeframe HiLo Strategy
    - Trades on 60-minute bars
    - Requires confirmation from daily timeframe
    - Position sizing: 1 contract for 60min + 2 contracts for daily = 3x when both agree
    """
    n_60 = 3      # Period for 60-minute timeframe
    n_daily = 3   # Period for daily timeframe

    def init(self):
        # 60-minute indicators
        high = self.data.High
        low = self.data.Low
        self.smahigh_60 = self.I(SMA, high, self.n_60)
        self.smalow_60 = self.I(SMA, low, self.n_60)

        # Daily signal (already calculated and merged)
        self.daily_signal = self.data.Daily_Signal

    def next(self):
        close = self.data.Close[-1]

        # Get 60-minute signal
        signal_60 = 0
        if close > self.smahigh_60[-1]:
            signal_60 = 1  # Long on 60min
        elif close < self.smalow_60[-1]:
            signal_60 = -1  # Short on 60min

        # Get daily signal
        daily_sig = self.daily_signal[-1]

        # Only trade when both timeframes agree
        if signal_60 == 1 and daily_sig == 1:
            # Both bullish: buy with 3x size (1 contract 60min + 2 contracts daily)
            if self.position.is_short:
                self.position.close()
            if not self.position:
                self.buy(size=3)
            elif self.position.size < 3:
                # Add to position if not at full size
                self.buy(size=3 - self.position.size)

        elif signal_60 == -1 and daily_sig == -1:
            # Both bearish: sell with 3x size
            if self.position.is_long:
                self.position.close()
            if not self.position:
                self.sell(size=3)
            elif abs(self.position.size) < 3:
                # Add to position if not at full size
                self.sell(size=3 - abs(self.position.size))

        # If signals conflict, close any existing position
        elif self.position and signal_60 != 0 and daily_sig != 0 and signal_60 != daily_sig:
            self.position.close()

#%%
# Run backtest
bt = Backtest(milho_combined, MultiTimeframeHiLoStrategy, cash=10000, commission=0.0002)
stats = bt.run()
print("\n" + "="*50)
print("MULTI-TIMEFRAME STRATEGY RESULTS (60min + Daily)")
print("="*50)
print(stats)
bt.plot()

#%%
# Optimize both parameters
if __name__ == '__main__':
    stats, heatmap = bt.optimize(
        n_60=range(1, 30, 2),      # 60-minute period
        n_daily=range(1, 30, 2),    # Daily period
        maximize='Return [%]',
        max_tries=200,
        return_heatmap=True
    )
    print("\n" + "="*50)
    print("OPTIMIZED RESULTS")
    print("="*50)
    print(stats)
    print("\nOptimal parameters:")
    print(f"60-minute period (n_60): {stats._strategy.n_60}")
    print(f"Daily period (n_daily): {stats._strategy.n_daily}")

#%%
# Plot heatmap if optimization was run
# heatmap.plot()

# %%
