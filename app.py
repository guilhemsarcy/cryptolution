import krakenex
import time
import pandas as pd
import dash
import json
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import datetime as dt
import os


try:
    kraken = krakenex.API()
    kraken.load_key('../auth/kraken.key')
except FileNotFoundError:
    kraken = krakenex.API(key=f"{os.environ.get('KRAKEN_KEY', None)}")

interval_in_minutes = '1440'
result_ohlc = pd.DataFrame(columns=['asset_pair', 'wsname', 'asset', 'currency',
                                    'time', 'open_price', 'close_price', 'volume'])

print(time.strftime('%Y-%m-%d %H:%M:%S') + ' : ' +
      'starting to collect data from Kraken')

ret = False
while not ret:
    try:
        print(time.strftime('%Y-%m-%d %H:%M:%S') + ' : ' +
              'trying to collect the list of asset pairs')
        assetPairs = kraken.query_public('AssetPairs')
        ret = True
    except ValueError:
        print(time.strftime('%Y-%m-%d %H:%M:%S') + ' : ' +
              'Kraken not available - retry after 5 sec')
        time.sleep(5)
pairs = assetPairs['result']
print(time.strftime('%Y-%m-%d %H:%M:%S') +
      ' : ' + 'list of asset pairs collected')
pairs = {p: {'wsname': pairs[p]['wsname'],
             'asset': pairs[p]['wsname'].split('/')[0],
             'currency': pairs[p]['wsname'].split('/')[1]
             } for p in pairs if p.endswith('EUR') or p.endswith('USD')
         }
# test on few items
from itertools import islice
pairs = dict(islice(pairs.items(), 5))
# end test

for k, items in enumerate(pairs.items()):
    asset_pair = items[0]
    wsname = items[1]['wsname']
    asset = items[1]['asset']
    currency = items[1]['currency']
    current_result_ohlc_asset = pd.DataFrame(columns=['asset_pair', 'wsname', 'asset', 'currency',
                                                      'time', 'open_price', 'close_price', 'volume'])
    ret = False
    while not ret:
        try:
            current_query_ohlc = kraken.query_public(
                'OHLC', {'pair': asset_pair, 'interval': interval_in_minutes})
            ret = True
        except ValueError:
            print(time.strftime('%Y-%m-%d %H:%M:%S') + ' : ' +
                  'Kraken not available ' + '- retry after 5 sec')
            time.sleep(5)
    print(time.strftime('%Y-%m-%d %H:%M:%S') + ' : ' +
          'trying to collect data for asset pair ' + asset_pair)

    try:
        error = current_query_ohlc['error'][0]
    except IndexError:
        error = 'No error'

    if error == 'No error':
        current_data_ohlc_asset = current_query_ohlc['result'][asset_pair]
        for i in range(0, len(current_data_ohlc_asset)):
            temp_time = time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(current_data_ohlc_asset[i][0]))  # period
            # price at the beginning of the period
            temp_open_price = current_data_ohlc_asset[i][1]
            # price at the end of the period
            temp_close_price = current_data_ohlc_asset[i][4]
            # number of shares traded
            temp_volume = current_data_ohlc_asset[i][6]
            current_result_ohlc_asset.loc[i] = [asset_pair, wsname, asset, currency, temp_time,
                                                temp_open_price, temp_close_price, temp_volume]
        print(time.strftime('%Y-%m-%d %H:%M:%S') + ' : ' + 'data collected for asset pair ' + asset_pair +
              ' - current progress is ' + str(int(float(k + 1) / float(len(pairs)) * 100)) + '%')
        result_ohlc = pd.concat([result_ohlc, current_result_ohlc_asset])

    else:
        print(time.strftime('%Y-%m-%d %H:%M:%S') + ' : ' +
              'data not collected for asset pair ' + asset_pair)

print(time.strftime('%Y-%m-%d %H:%M:%S') + ' : ' +
      'No more data to collect from Kraken')

# Dash App

app = dash.Dash(__name__)
server = app.server

currency_options = ['EUR', 'USD']
dropdown_currency_options = [{'label': c, 'value': c} for c in currency_options]

with open('assets_mapping/mapping.json') as json_mapping_file:
    mapping = json.load(json_mapping_file)
assets = [a for a in pairs]
assets.sort()
dropdown_asset_options = [{'label': mapping[pairs[a]['asset']], 'value': a} for a in assets]

measures = ['open_price', 'close_price', 'volume']
measure_options = [{'label': m, 'value': m} for m in measures]

colors = {
    'background': '#111111',
    'text': '#7FDBFF',
    'text_dropdowns': '#F9FBFC'
}

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.Label(children='Select your currency', style={'color': colors['text_dropdowns']}),
    dcc.Dropdown(
        id='currency_choice',
        options=dropdown_currency_options,
        value='EUR'
    ),

    html.Label(children='Select your asset pair', style={'color': colors['text_dropdowns']}),
    dcc.Dropdown(
        id='asset_choice',
        options=dropdown_asset_options,
        value=''
    ),

    html.Label(children='Select your KPI', style={'color': colors['text_dropdowns']}),
    dcc.Dropdown(
        id='measure_choice',
        options=measure_options,
        value='open_price'
    ),

    html.H1(
        children='Cryptocurrencies on Kraken',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.Div(children='Using Kraken API to collect data about cryptocurrencies', style={
        'textAlign': 'center',
        'color': colors['text']
    }),

    dcc.Graph(
        id='graph_1',
        figure={
            'data': [{'x': result_ohlc['time'],
                      'y': result_ohlc['open_price']
                      }],
            'layout': {
                'plot_bgcolor': colors['background'],
                'paper_bgcolor': colors['background'],
                'font': {
                    'color': colors['text']
                }
            }
        }
    ),

    html.Label(children='Select your date range', style={'color': colors['text_dropdowns']}),
    html.Div([
        dcc.DatePickerRange(
            id='date_picker_range',
            start_date=dt.datetime.strptime(result_ohlc['time'].min(), "%Y-%m-%d %H:%M:%S"),
            end_date=dt.datetime.strptime(result_ohlc['time'].max(), "%Y-%m-%d %H:%M:%S"),
            end_date_placeholder_text='Select a date!'
        )
    ]
    )
])


@app.callback(
    dash.dependencies.Output('asset_choice', 'options'),
    dash.dependencies.Input('currency_choice', 'value')
)
def update_assets_list(curr):
    return [{'label': mapping[pairs[a]['asset']], 'value': a} for a in assets if a.endswith(curr)]


@app.callback(
    dash.dependencies.Output('graph_1', 'figure'),
    [dash.dependencies.Input('asset_choice', 'value'),
     dash.dependencies.Input('measure_choice', 'value'),
     dash.dependencies.Input('date_picker_range', 'start_date'),
     dash.dependencies.Input('date_picker_range', 'end_date')])
def update_graph(selected_asset, selected_measure, selected_start_date, selected_end_date):
    filtered_df = result_ohlc[result_ohlc.asset_pair == selected_asset]
    filtered_df = filtered_df[filtered_df.time >= selected_start_date]
    filtered_df = filtered_df[filtered_df.time <= selected_end_date]
    return {
        'data': [
            {'x': filtered_df['time'],
             'y': filtered_df[selected_measure],
             'name': 'Open price'}
        ],
        'layout': {
            'plot_bgcolor': colors['background'],
            'paper_bgcolor': colors['background'],
            'font': {
                'color': colors['text']
            }
        }
    }


if __name__ == '__main__':
    app.run_server(debug=True)
