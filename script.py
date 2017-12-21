
# Libs ----------------------------------------------------------------

pip install krakenex
pip install plotly==2.0.11 
pip install dash==0.17.5 
pip install dash_renderer 
pip install dash_core_components 
pip install dash_html_components 
pip install pandas_datareader

import krakenex
import time
import pandas as pd
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
from pandas_datareader import data as web
from datetime import datetime as dt

# Authentication

kraken = krakenex.API()
kraken.load_key('<your_path>\kraken.key.txt') # to download on Kraken


# Collecting data - all cryptocurrencies

interval_in_minutes = '1440'
result_ohlc = pd.DataFrame(columns=['asset','time', 'open_price','close_price','volume'])

print(time.strftime('%Y-%m-%d %H:%M:%S')+ ' : ' + 'starting to collect data from Kraken')


ret = 0
while ret == 0: 
    try :
        print(time.strftime('%Y-%m-%d %H:%M:%S')+ ' : ' + 'trying to collect the list of asset pairs')
        assetPairs = kraken.query_public('AssetPairs',{'info':'leverage'})
        ret = 1
    except ValueError:
        print(time.strftime('%Y-%m-%d %H:%M:%S')+ ' : ' + 'Kraken not available - retry after 5 sec')
        ret = 0
        time.sleep(5)
assetPairs = assetPairs['result'].keys()
assets = []
print(time.strftime('%Y-%m-%d %H:%M:%S')+ ' : ' + 'list of asset pairs collected')


for k in range(0,len(assetPairs)):
    asset_k = assetPairs[k]
    result_ohlc_asset_k = pd.DataFrame(columns=['asset','time', 'open_price','close_price','volume'])
    
    ret = 0
    while ret == 0: 
        try :
            query_ohlc_k = kraken.query_public('OHLC', {'pair' : asset_k,'interval':interval_in_minutes})
            ret = 1
        except ValueError:
            print(time.strftime('%Y-%m-%d %H:%M:%S')+ ' : ' + 'Kraken not available ' + '- retry after 5 sec') 
            ret = 0
            time.sleep(5)
    print(time.strftime('%Y-%m-%d %H:%M:%S')+ ' : '+ 'trying to collect data for asset ' + asset_k)
    
    try :
        error = query_ohlc_k['error'][0]
    except :
        error = 'No error'
        
    if error == 'No error':
        assets.append(asset_k)
        data_ohlc_asset_k = query_ohlc_k['result'][asset_k] 
        for i in range(0,len(data_ohlc_asset_k)):
            asset_i = asset_k                                                           #asset
            time_i = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data_ohlc_asset_k[i][0]))#period 
            open_price_i = data_ohlc_asset_k[i][1]                                      #price at the beginning of the period
            close_price_i = data_ohlc_asset_k[i][4]                                     #price at the end of the period
            volume_i = data_ohlc_asset_k[i][6]                                          #number of shares traded
            result_ohlc_asset_k.loc[i] = [asset_i,time_i,open_price_i,close_price_i,volume_i]
        print(time.strftime('%Y-%m-%d %H:%M:%S')+ ' : '+'data collected for asset '+ asset_k + \
              ' - current progress is ' + str(int(float(k+1)/float(len(assetPairs))*100))+'%')
        result_ohlc = pd.concat([result_ohlc,result_ohlc_asset_k])
        
    else :
        print(time.strftime('%Y-%m-%d %H:%M:%S')+ ' : '+'data not collected for asset '+ asset_k)

print(time.strftime('%Y-%m-%d %H:%M:%S')+ ' : ' + 'no more data to collect from Kraken')        