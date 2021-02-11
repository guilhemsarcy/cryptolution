import pandas as pd
import dash
import json
import dash_core_components as dcc
import dash_html_components as html
import datetime as dt


# Dash App

app = dash.Dash(__name__)
server = app.server

result_ohlc = pd.read_csv("kraken_data/data.csv")
with open('kraken_data/pairs.json') as json_pairs:
    pairs = json.load(json_pairs)

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
