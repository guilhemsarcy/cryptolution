"""Main script describing dash app."""

import datetime as dt
import json
from datetime import timedelta
from os import getenv

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from settings import mapping_status

AWS_ACCESS_KEY_ID = getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = getenv('AWS_SECRET_ACCESS_KEY')

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
app.title = 'cryptolution'
server = app.server

result_ohlc = pd.read_csv("s3://cryptolution/data.csv")

with open('modules/data/pairs.json') as json_pairs:
    pairs = json.load(json_pairs)
    # hotfix!
    pairs.pop("AUDUSD", None)
    pairs.pop("ZEURZUSD", None)
    pairs.pop("ZGBPZUSD", None)
    pairs.pop("KEEPEUR", None)
    pairs.pop("KEEPUSD", None)
    pairs.pop("XREPZEUR", None)
    pairs.pop("XREPZUSD", None)

currency_options = ['EUR', 'USD']
dropdown_currency_options = [{'label': c, 'value': c} for c in currency_options]

with open('modules/assets_mapping/mapping.json') as json_mapping_file:
    mapping = json.load(json_mapping_file)
assets = [a for a in pairs]
assets.sort()
dropdown_asset_options = sorted([{'label': mapping[pairs[a]['asset']], 'value': a} for a in assets],
                                key=lambda i: i['label'])

measures = ['open_price', 'close_price', 'volume']
measure_options = [{'label': m, 'value': m} for m in measures]

colors = {
    'background': '#111111',
    'text': 'white',
    'text_dropdowns': '#F9FBFC'
}

app.layout = dbc.Container(
    children=[
        dbc.Row(
            dbc.Col(
                html.Div(
                    [
                        dbc.Button(
                            id='last_available_data',
                            size="lg",
                            outline=True,
                            disabled=True,
                            className="mr-1",
                            style={"margin-top": 10}
                        )
                    ]
                ),
                width={"size": 6, "offset": 3}
            ),
            justify="center"
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.Label(children='Reference currency choice', style={'color': colors['text_dropdowns']}),
                    width=2
                ),
                dbc.Col(
                    html.Label(children='Asset choice', style={'color': colors['text_dropdowns']}),
                    width=2
                ),
                dbc.Col(
                    html.Label(children='Metric choice', style={'color': colors['text_dropdowns']}),
                    width=2
                )
            ],
            justify="center"
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Dropdown(
                        id='currency_choice',
                        options=dropdown_currency_options,
                        value='EUR',
                        style={'backgroundColor': colors['background'], 'color': 'black', 'line-height': '34px'}
                    ),
                    width=2
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id='asset_choice',
                        options=dropdown_asset_options,
                        value='',
                        style={'backgroundColor': colors['background'], 'color': 'black'}
                    ),
                    width=2
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id='measure_choice',
                        options=measure_options,
                        value='open_price',
                        style={'backgroundColor': colors['background'], 'color': 'black'}
                    ),
                    width=2
                )
            ],
            justify="center"
        ),
        dbc.Row(
            dbc.Col(
                html.Label(children='Date range choice', style={'color': colors['text_dropdowns']}),
                width=2
            )
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.DatePickerRange(
                        id='date_picker_range',
                        display_format='YYYY-MM-DD',
                        month_format='YYYY, MMMM',
                        start_date=dt.datetime.strptime(result_ohlc['time'].min(), "%Y-%m-%d %H:%M:%S"),
                        end_date=dt.datetime.strptime(result_ohlc['time'].max(), "%Y-%m-%d %H:%M:%S"),
                        end_date_placeholder_text='Select a date!',
                        style={'backgroundColor': colors['background'], 'color': 'black'}
                    ),
                    width=2
                )
            ]
        ),

        html.H1(
            id='title',
            style={'textAlign': 'center', 'color': colors['text']}
        ),

        dcc.Graph(
            id='graph_1'
        )
    ],
    style={
        'backgroundColor': colors['background'],
        'color': colors['text_dropdowns'],
        'height': '100vh'
    },
    fluid=True
)


@app.callback(
    dash.dependencies.Output('last_available_data', 'children'),
    dash.dependencies.Input('asset_choice', 'value')
)
def update_last_available_data(selected_asset: str) -> str:
    """
    Get last available data.

    :param selected_asset: targeted asset
    :return: last available data
    """
    try:
        return f"Last available data : {max(result_ohlc[result_ohlc.asset_pair == selected_asset].time)[:10]}"
    except ValueError:
        return f"Last available data : {max(result_ohlc.time)[:10]}"


@app.callback(
    dash.dependencies.Output('last_available_data', 'color'),
    dash.dependencies.Input('asset_choice', 'value')
)
def update_status(selected_asset):
    """
    Get data update status.

    :param selected_asset: targeted asset
    :return: data update status (given the last available time)
    """
    try:
        max_date_asset = max(result_ohlc[result_ohlc.asset_pair == selected_asset].time)[:10]
    except ValueError:
        max_date_asset = max(result_ohlc.time)[:10]

    last_date = dt.datetime.strptime(max_date_asset, '%Y-%m-%d')
    if last_date >= dt.datetime.now() - timedelta(days=5):
        status = 'fresh'
    elif last_date >= dt.datetime.now() - timedelta(days=15):
        status = 'half_fresh'
    else:
        status = 'rotten'

    return mapping_status[status]


@app.callback(
    dash.dependencies.Output('title', 'children'),
    [
        dash.dependencies.Input('currency_choice', 'value'),
        dash.dependencies.Input('asset_choice', 'value'),
        dash.dependencies.Input('measure_choice', 'value')
    ]
)
def update_title(currency, asset, metric):
    """
    Update graph title according to dropdown values.

    :param currency: reference currency choice
    :type currency: string
    :param asset: asset choice
    :type asset: string
    :param metric: metric choice
    :type metric: string

    :return: graph title
    :rtype: string
    """
    try:
        asset_label = mapping[pairs[asset]['asset']]
    except KeyError:
        asset_label = ''
    if asset_label == '':
        return ''
    else:
        if 'price' in metric:
            return f"Evolution of daily {metric} for {asset_label} (in {currency})"
        else:
            return f"Evolution of daily {metric} for {asset_label}"


@app.callback(
    dash.dependencies.Output('asset_choice', 'options'),
    dash.dependencies.Input('currency_choice', 'value')
)
def update_assets_list(curr):
    """
    Update assets' dropdown component, based on currency choice.

    :param curr: currency
    :type curr: string

    :return: dropdown component definition for assets
    :rtype: List[Dict]
    """
    return sorted([{'label': mapping[pairs[a]['asset']], 'value': a} for a in assets if a.endswith(curr)],
                  key=lambda i: i['label'])


@app.callback(
    dash.dependencies.Output('graph_1', 'figure'),
    [
        dash.dependencies.Input('asset_choice', 'value'),
        dash.dependencies.Input('currency_choice', 'value'),
        dash.dependencies.Input('measure_choice', 'value'),
        dash.dependencies.Input('date_picker_range', 'start_date'),
        dash.dependencies.Input('date_picker_range', 'end_date')
    ]
)
def update_graph(selected_asset, selected_currency, selected_measure, selected_start_date, selected_end_date):
    """
    Update graph component, base on asset, measure, start date and end date.

    :param selected_asset: asset choice
    :type selected_asset: string
    :param selected_currency: currency choice
    :type selected_currency: string
    :param selected_measure: measure choice
    :type selected_measure: string
    :param selected_start_date: choice for start date
    :type selected_start_date: datetime
    :param selected_end_date: choice for end date
    :type selected_end_date: datetime

    :return: graph component definition for asset's evolution
    :rtype: Dict
    """
    filtered_df = result_ohlc[
        (result_ohlc.asset_pair == selected_asset) &
        (result_ohlc.currency == selected_currency) &
        (result_ohlc.time >= selected_start_date) &
        (result_ohlc.time <= selected_end_date)
    ]
    symbol = '€'
    if selected_currency != 'EUR':
        symbol = '$'

    return {
        'data': [
            {
                'x': filtered_df['time'],
                'y': filtered_df[selected_measure],
                'mode': 'lines',
                'line': dict(color='#749ce1', line=dict(width=5))
            }
        ],
        'layout': {
            'plot_bgcolor': colors['background'],
            'paper_bgcolor': colors['background'],
            'font': {
                'color': colors['text']
            },
            'height': 600,
            'yaxis': {
                "ticksuffix": f"{symbol}",
            }
        }
    }


if __name__ == '__main__':
    app.run_server(debug=True)
