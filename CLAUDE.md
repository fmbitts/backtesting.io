# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based algorithmic trading project focused on corn futures (CCM) analysis and backtesting. The codebase implements HILO indicator strategies for different timeframes (60min, 120min, 240min, daily) with optimization capabilities.

## Architecture

### Core Components

1. **Data Import System** (`import_tools.py`):
   - `get_data_from_profit()`: Primary function to load price data from CSV or Parquet files
   - `import_from_profit()`: Converts CSV files from Profit platform to clean DataFrames
   - Handles data cleaning, type conversion, and datetime indexing
   - Automatically converts CSV to Parquet for faster subsequent loads

2. **Strategy Implementation Files**:
   - `CCM_120.py`, `CCM_240.py`, `CCM_60.py`, `CCM_daily.py`: Timeframe-specific backtesting scripts
   - All use the `backtesting` library with `HiLoStrategy` class
   - Implement SMA-based high/low crossover strategies with position reversal logic

3. **Technical Indicators Library** (`didi.py`):
   - Comprehensive technical analysis functions using TAlib
   - Includes DIDI Index, ADX, TRIX, Stochastic, Bollinger Bands indicators
   - `StrategyAgulhada` class implementing ADX-based strategy for stock market data
   - Utility functions for stop-loss and take-profit calculations

### Data Structure

- **Data Directory**: Contains CSV and Parquet files for different timeframes
- **File Naming Convention**: `CCM_{timeframe}` (e.g., CCM_120, CCM_daily)
- **Required Columns**: Date, Open, High, Low, Close
- **Data Source**: Profit platform exports (semicolon-delimited, latin-1 encoded)

### Strategy Logic

**HiLoStrategy Pattern** (used across timeframe files):
- Calculate SMA of High and Low prices over n periods
- Long signal: Close > SMA(High)
- Short signal: Close < SMA(Low)
- Position reversal: Close existing position and enter opposite direction

**Advanced HILO Algorithm** (algo_claude.py):
- Uses moving averages of High/Low as dynamic support/resistance
- Pyramiding: Adds contracts when position shows 3%+ profit
- Transaction costs: Fixed cost (R$2 per contract per side) + percentage cost (0.06%)

## Common Development Tasks

### Running Backtests

Execute strategy files directly:
```python
python CCM_120.py
python CCM_daily.py
# etc.
```

### Data Loading

Use the import system:
```python
from import_tools import get_data_from_profit
data = get_data_from_profit('CCM_120')  # Loads 120-minute data
```

### Strategy Optimization

Most files include optimization blocks:
```python
if __name__ == '__main__':
    stats, heatmap = bt.optimize(
        n=range(1, 50, 1),
        maximize='Return [%]',  # or 'Calmar Ratio'
        max_tries=100,
        return_heatmap=True
    )
```

### Advanced Algorithm Usage

```python
from algo_claude import process_corn_futures_data
results = process_corn_futures_data('Data/CCM_daily.csv')
optimal_period = results['optimal_period']
```

## Development Environment

- **Python Libraries**: pandas, backtesting, ta, matplotlib, numpy, pyarrow
- **Multiprocessing**: Uses fork method (set in strategy files)
- **Data Format**: Jupyter notebook cells marked with `#%%` for interactive development
- **File Structure**: Flat structure with timeframe-specific strategy files

## Key Implementation Details

- All price data is loaded as float type after cleaning comma-separated decimals
- Duplicate timestamps are removed using `keep='first'`
- Parquet files are automatically generated for faster subsequent loads
- Commission set to 0.02% (0.0002) across backtesting implementations
- Default cash amount: R$10,000 for backtesting