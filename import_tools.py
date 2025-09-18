#%%
import pandas as pd
import pyarrow
import os
import warnings
import time

#%%

def import_from_profit(file:str):
    """"
    This get the csv file from profit, gets the data clean and format to a datetime series
    """
    
    
    data = pd.read_csv(f'Data/{file}.csv', delimiter=';', encoding='latin-1')
    data.columns = ['Date', 'Open', 'High', 'Low', 'Close' ]
    data['Date'] = pd.to_datetime(data['Date'], dayfirst=True)
    data = data.set_index('Date')
    data.replace(',','.', regex=True, inplace=True)
    data['Open'] = data['Open'].astype(float)
    data['High'] = data['High'].astype(float)
    data['Low'] = data['Low'].astype(float)
    data['Close'] = data['Close'].astype(float)       
    data.info()
    data.to_parquet(f'Data/{file}.parquet', engine='pyarrow')
    return data



 #%%       
def get_data_from_profit(file:str):
    if os.path.exists(f'Data/{file}.parquet'):
        print('Parque file on the directory. Loading the parquet file...')
        data = pd.read_parquet(f'Data/{file}.parquet')
        data['Open'] = data['Open'].astype(float)
        data['High'] = data['High'].astype(float)
        data['Low'] = data['Low'].astype(float)
        data['Close'] = data['Close'].astype(float) 
        return data
    elif  os.path.exists(f'Data/{file}.csv'):
        print('Parquer file it´s not in the directory, so loading the CSV file...')
        data = import_from_profit(file)
        return data
         
    else:
        print('Either CSV or Parquet file does not exist.')
        raise TypeError(f'There is no Parquer or CSV {file} in Data directory')
    warnings.warn('No file', stacklevel=2)    

