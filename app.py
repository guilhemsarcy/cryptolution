"""Main script describing dash app."""

import datetime as dt
import json
from datetime import timedelta

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

result_ohlc = pd.read_csv("data/data.csv")
last_date = dt.datetime.strptime(max(result_ohlc.time)[:10], '%Y-%m-%d')
if last_date >= dt.datetime.now() - timedelta(days=1):
    status = 'fresh'
elif last_date >= dt.datetime.now() - timedelta(days=10):
    status = 'half_fresh'
else:
    status = 'rotten'

status_mapping = {
    'fresh': 'success',
    'half_fresh': 'warning',
    'rotten': 'danger'
}

with open('data/pairs.json') as json_pairs:
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
    'text': 'white',
    'text_dropdowns': '#F9FBFC'
}

app.layout = html.Div(
    style={'backgroundColor': colors['background'],
           'color': colors['text_dropdowns']},
    children=[
        html.H1(
            children='Cryptocurrency market',
            style={
                'textAlign': 'center',
                'color': colors['text']
            }
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.Label(children='Select your currency', style={'color': colors['text_dropdowns']})
                ),
                dbc.Col(
                    html.Label(children='Select your asset pair', style={'color': colors['text_dropdowns']})
                ),
                dbc.Col(
                    html.Label(children='Select your KPI', style={'color': colors['text_dropdowns']})
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Dropdown(
                        id='currency_choice',
                        options=dropdown_currency_options,
                        value='EUR',
                        style={'backgroundColor': colors['background'], 'color': 'black'}
                    )
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id='asset_choice',
                        options=dropdown_asset_options,
                        value='',
                        style={'backgroundColor': colors['background'], 'color': 'black'}
                    )
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id='measure_choice',
                        options=measure_options,
                        value='open_price',
                        style={'backgroundColor': colors['background'], 'color': 'black'}
                    )
                )
            ]
        ),


        html.Label(children='Select your date range', style={'color': colors['text_dropdowns']}),
        html.Div([
            dcc.DatePickerRange(
                id='date_picker_range',
                display_format='YYYY-MM-DD',
                month_format='YYYY, MMMM',
                start_date=dt.datetime.strptime(result_ohlc['time'].min(), "%Y-%m-%d %H:%M:%S"),
                end_date=dt.datetime.strptime(result_ohlc['time'].max(), "%Y-%m-%d %H:%M:%S"),
                end_date_placeholder_text='Select a date!',
                style={'backgroundColor': colors['background'],
                       'color': 'black'}
            ),
        ]
        ),

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

        html.Div([
            dbc.Button(
                f"Last available data : {max(result_ohlc.time)[:10]}",
                size="lg",
                outline=True,
                color=f"{status_mapping[status]}",
                disabled=True,
                className="mr-1"
            )
        ]
        )
    ]
)


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
    return [{'label': mapping[pairs[a]['asset']], 'value': a} for a in assets if a.endswith(curr)]


@app.callback(
    dash.dependencies.Output('graph_1', 'figure'),
    [dash.dependencies.Input('asset_choice', 'value'),
     dash.dependencies.Input('measure_choice', 'value'),
     dash.dependencies.Input('date_picker_range', 'start_date'),
     dash.dependencies.Input('date_picker_range', 'end_date')])
def update_graph(selected_asset, selected_measure, selected_start_date, selected_end_date):
    """
    Update graph component, base on asset, measure, start date and end date.

    :param selected_asset: asset choice
    :type selected_asset: string
    :param selected_measure: measure choice
    :type selected_measure: string
    :param selected_start_date: choice for start date
    :type selected_start_date: datetime
    :param selected_end_date: choice for end date
    :type selected_end_date: datetime

    :return: graph component definition for asset's evolution
    :rtype: Dict
    """
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
