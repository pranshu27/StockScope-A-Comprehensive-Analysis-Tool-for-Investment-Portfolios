import yfinance as yf
import pandas as pd
import dash
import numpy as np
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline
import plotly.graph_objs as go
import plotly.express as px
import datetime as dt
from scipy.stats import norm
from dateutil.relativedelta import relativedelta
import dash_bootstrap_components as dbc

top50 = ['AAPL', 'MSFT', 'GOOG', 'AMZN', 'FB', 'TSLA', 'JPM', 'JNJ', 'V', 'BRK-A', 'NVDA', 'PG', 'UNH', 'MA', 'HD', 'DIS', 'PYPL', 'BAC', 'INTC', 'VZ', 'CMCSA', 'KO', 'PEP', 'PFE', 'NFLX',
         'T', 'ABT', 'CRM', 'CVX', 'MRK', 'WMT', 'CSCO', 'XOM', 'ABBV', 'CVS', 'ACN', 'ADBE', 'ORCL', 'BA', 'TMO', 'TGT', 'F', 'NKE', 'MDT', 'UPS', 'MCD', 'LOW', 'IBM', 'MMM', 'GE', 'AMGN']


# Define the app
app = dash.Dash(__name__, external_stylesheets=[
                dbc.themes.BOOTSTRAP, './assets/custom.css'])


# Define the navigation bar
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink(
            "HOME", href="javascript:location.reload(true)")),
        dbc.NavItem(dbc.NavLink("ABOUT", href="/about", active='exact'))
    ],
    brand="STOCK COMPARISON",
    brand_href="#",
    color="brown",
    dark=True,
)

# Define the list of time periods
periods = {
    '6m': '6mo',
    '1y': '1y',
    '2y': '2y',
    '5y': '5y',
    '10y': '10y',
    '20y': '20y'
}


# Define the layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Br(),
    dbc.Tabs([
        # dcc.Tab(label='Risk Analysis using LR', children=[
        #     html.Div([
        #         html.Br(),
        #         html.Label('Select stock symbol:', style={
        #                    'font-weight': 'bold', 'font-size': '20px', 'color': '#007bff'}),
        #         dcc.Dropdown(id='st', options=[
        #                      {'label': i, 'value': i} for i in top50], value='AAPL'),
        #         html.Br(),
        #         html.Label('Select Time Period used for Prediction: ', style={
        #                    'font-weight': 'bold', 'font-size': '20px', 'color': '#007bff'}),
        #         dcc.RadioItems(id='overall', options=[
        #             {'label': '6 Months', 'value': '6mo'},
        #             {'label': '1 Year', 'value': '1y'},
        #             {'label': '5 Years', 'value': '5y'},
        #             {'label': '10 Years', 'value': '10y'},
        #             {'label': '20 Years', 'value': '20y'}
        #         ], value='1y'),
        #         html.Br(),
        #         html.Label('Select Prediction Time Period: ', style={
        #                    'font-weight': 'bold', 'font-size': '20px', 'color': '#007bff'}),

        #         dcc.RadioItems(
        #             id='prediction-time',
        #             options=[
        #                 {'label': '30 days', 'value': '30'},
        #                 {'label': '60 days', 'value': '60'},
        #                 {'label': '90 days', 'value': '90'},
        #             ],
        #             value='30'
        #         ),
        #         html.Br(),
        #         dcc.Graph(id='risk-analysis-graph')
        #     ])
        # ]),


        dcc.Tab(label='Technical Analysis using Candlestick Chart', children=[
            html.Div([
                html.Br(),
                html.Label('Select stock symbol: ', style={
                           'font-weight': 'bold', 'font-size': '20px', 'color': '#007bff'}),
                dbc.Row([
                    dbc.Col(
                        dcc.Dropdown(
                            id='symbol-dropdown', options=[{'label': s, 'value': s} for s in top50], value=top50[0]),
                    ),
                    html.Br(),
                    html.Br(),
                    html.Br(),
                    html.Label('Select Time Period for Technical Analysis', style={
                               'font-weight': 'bold', 'font-size': '20px', 'color': '#007bff'}),
                    dbc.Col(
                        dcc.Dropdown(id='period-dropdown', options=[
                                     {'label': k, 'value': v} for k, v in periods.items()], value='1y'),
                    ),
                ]),

                dbc.Row([
                    dbc.Col(
                        dcc.Graph(id='graph'),
                        width={'size': 10, 'offset': 1}
                    )
                ]),
            ])
        ]),

        dcc.Tab(label='Risk Analysis using Monte Carlo Simulation', children=[
            html.Div([

                html.Label('Select stock symbol: '),
                dcc.Dropdown(id='stk', options=[
                             {'label': i, 'value': i} for i in top50], value='AAPL'),
                html.Br(),
                html.Label('Select number of simulations to run: '),
                dcc.RadioItems(id='sim', options=[
                    {'label': '5', 'value': '5'},
                    {'label': '50', 'value': '50'},
                    {'label': '100', 'value': '100'},
                    {'label': '500', 'value': '500'},
                    # {'label': '20 Years', 'value': '20y'}
                ], value='100'),
                html.Br(),
                html.Label('Select Prediction Time Period: '),

                dcc.RadioItems(
                    id='time',
                    options=[
                        {'label': '30 days', 'value': '30'},
                        {'label': '60 days', 'value': '60'},
                        {'label': '90 days', 'value': '90'},
                    ],
                    value='30'
                ),
                html.Br(),
                dcc.Graph(id='monte-carlo'),
                dcc.Graph(id='monte-carlo-dist')
            ])
        ]),

        # stk, sim, time

        dcc.Tab(label='Stocks\'/Attributes Comparison Playground', children=[
            html.Div([
                html.Label('Select stock symbol: '),
                dcc.Dropdown(
                    id='input-box', options=[{'label': i, 'value': i} for i in top50], value='AAPL', multi=True),

                html.Br(),
                html.Label('Select stock attribute: '),
                dcc.Dropdown(id='stock-attribute', options=[
                    {'label': 'Open', 'value': 'Open'},
                    {'label': 'High', 'value': 'High'},
                    {'label': 'Low', 'value': 'Low'},
                    {'label': 'Close', 'value': 'Close'},
                    {'label': 'Adj Close', 'value': 'Adj Close'},
                ], value='Adj Close'),
                html.Br(),
                html.Label('Select time period: '),
                dcc.RadioItems(id='time-period', options=[
                    {'label': '1 Month', 'value': '1mo'},
                    {'label': '3 Months', 'value': '3mo'},
                    {'label': '6 Months', 'value': '6mo'},
                    {'label': '1 Year', 'value': '1y'},
                    {'label': '5 Years', 'value': '5y'}
                ], value='1mo'),
                html.Br(),
                dcc.Graph(id='stock-vs-sensex')
            ])
        ]),

        dcc.Tab(label='Avg. Sensex Hike/Dip', children=[
            html.Div([
                html.Label('Select Overall Time Period: '),
                dcc.RadioItems(id='overall-time-period', options=[
                    {'label': '6 Months', 'value': '6mo'},
                    {'label': '1 Year', 'value': '1y'},
                    {'label': '5 Years', 'value': '5y'},
                    {'label': '10 Years', 'value': '10y'},
                    {'label': '20 Years', 'value': '20y'}
                ], value='1mo'),
                html.Br(),
                html.Label('Select Rolling Average Time Period: '),

                dcc.RadioItems(
                    id='rolling-mean-time',
                    options=[
                        {'label': '30 days', 'value': 30},
                        {'label': '60 days', 'value': 60},
                        {'label': '90 days', 'value': 90},
                    ],
                    value=30
                ),
                html.Br(),
                dcc.Graph(id='average-sensex-hike')
            ])
        ]),
        dcc.Tab(label='Pair Plots', children=[
            html.Div([
                html.Label('Select stock symbol: '),
                dcc.Dropdown(
                    id='input-box1', options=[{'label': i, 'value': i} for i in top50], value='AAPL'),
                html.Br(),
                dcc.Graph(id='pair-plots')
            ])
        ]),
        dcc.Tab(label='Long/Short Term Stocks Based on Variability', children=[
            html.Div([

                html.Label('Select stock symbol: '),
                dcc.Dropdown(id='stkk', options=[
                             {'label': i, 'value': i} for i in top50], value='AAPL'),
                html.Br(),
                html.Label('Select Time Period used for Prediction: '),
                dcc.RadioItems(id='overall1', options=[
                    {'label': '6 Months', 'value': '6mo'},
                    {'label': '1 Year', 'value': '1y'},
                    {'label': '5 Years', 'value': '5y'},
                    {'label': '10 Years', 'value': '10y'},
                    {'label': '20 Years', 'value': '20y'}
                ], value='1y'),
                html.Br(),
                dcc.Graph(id='Long-short')
            ])
        ]),
        dcc.Tab(label='Day-to-day change', children=[
            html.Div([

                html.Label('Select stock symbol: '),
                dcc.Dropdown(id='stkk2', options=[
                             {'label': i, 'value': i} for i in top50], value='AAPL'),
                html.Br(),
                html.Label('Select Time Period used for Prediction: '),
                dcc.RadioItems(id='overall2', options=[
                    {'label': '6 Months', 'value': '6mo'},
                    {'label': '1 Year', 'value': '1y'},
                    {'label': '5 Years', 'value': '5y'},
                    {'label': '10 Years', 'value': '10y'},
                    {'label': '20 Years', 'value': '20y'}
                ], value='1y'),
                html.Br(),
                dcc.Graph(id='day-to-day-change')
            ])
        ]),
        dcc.Tab(label='Trend Analysis', children=[
            html.Div([

                html.Label('Select stock symbol: '),
                dcc.Dropdown(id='stkk3', options=[
                             {'label': i, 'value': i} for i in top50], value='AAPL'),
                html.Br(),
                html.Label('Select Time Period: '),
                dcc.RadioItems(id='overall3', options=[
                    {'label': '6 Months', 'value': '6mo'},
                    {'label': '1 Year', 'value': '1y'},
                    {'label': '5 Years', 'value': '5y'},
                    {'label': '10 Years', 'value': '10y'},
                    {'label': '20 Years', 'value': '20y'}
                ], value='1y'),
                html.Br(),
                dcc.Graph(id='trend-analysis')
            ])
        ])
    ])
])


# Trend Analysis
@app.callback(Output('trend-analysis', 'figure'),
              [Input('stkk3', 'value')],
              [Input('overall3', 'value')])
def update_trend_analysis(stock_name, time_period):
    end_date = dt.date.today()

    if time_period == '6mo':
        start_date = end_date - dt.timedelta(days=180)
    elif time_period == '1y':
        start_date = end_date - dt.timedelta(days=365)
    elif time_period == '5y':
        start_date = end_date - dt.timedelta(days=1825)
    elif time_period == '10y':
        start_date = end_date - dt.timedelta(days=3650)
    elif time_period == '20y':
        start_date = end_date - dt.timedelta(days=7300)
    else:
        start_date = end_date - dt.timedelta(days=365)

    sx_data = yf.download(stock_name, start=start_date, end=end_date)

    # Function defining trend
    def trend(x):
        if x > -0.5 and x <= 0.5:
            return 'Slight or No change'
        elif x > 0.5 and x <= 1:
            return 'Slight Positive'
        elif x > -1 and x <= -0.5:
            return 'Slight Negative'
        elif x > 1 and x <= 3:
            return 'Positive'
        elif x > -3 and x <= -1:
            return 'Negative'
        elif x > 3 and x <= 7:
            return 'Among top gainers'
        elif x > -7 and x <= -3:
            return 'Among top losers'
        elif x > 7:
            return 'Bull run'
        elif x <= -7:
            return 'Bear drop'

    # Compute the daily percentage change in the stock prices
    sx_data['Day_Perc_Change'] = sx_data['Close'].pct_change() * 100

    # Add a new column for the trend
    sx_data['Trend'] = sx_data['Day_Perc_Change'].apply(trend)

    # Group the data by trend and count the number of occurrences
    sx_pie = sx_data.groupby(
        'Trend')['Trend'].count().reset_index(name='count')

    # Plot the pie chart using Plotly
    fig = px.pie(sx_pie, values='count', names='Trend',
                 title='Trend Analysis',
                 hole=0.4, color='Trend')
    return fig


# Long short term stocks based on variability


@ app.callback(Output('Long-short', 'figure'),
               [Input('stkk', 'value')],
               [Input('overall1', 'value')])
def update_graph(stock_name, time_period):
    end_date = dt.date.today()

    if time_period == '6mo':
        start_date = end_date - dt.timedelta(days=180)
    elif time_period == '1y':
        start_date = end_date - dt.timedelta(days=365)
    elif time_period == '5y':
        start_date = end_date - dt.timedelta(days=1825)
    elif time_period == '10y':
        start_date = end_date - dt.timedelta(days=3650)
    elif time_period == '20y':
        start_date = end_date - dt.timedelta(days=7300)
    else:
        start_date = end_date - dt.timedelta(days=365)

    sensex_data = yf.download(stock_name, start=start_date, end=end_date)

    # Calculate the mean and standard deviation of closing prices for the selected company
    mean = sensex_data['Close'].mean()
    std_dev = sensex_data['Close'].std()

    # Calculate the long-term and short-term stocks based on variability for the selected company
    long_term_stocks = sensex_data[sensex_data['Close'] > (mean + std_dev)]
    short_term_stocks = sensex_data[sensex_data['Close'] < (mean - std_dev)]

    # Create traces for the long-term and short-term stocks for the selected company
    long_trace = {
        'x': long_term_stocks.index,
        'y': long_term_stocks['Close'],
        'type': 'scatter',
        'name': 'Long Term Stocks'
    }

    short_trace = {
        'x': short_term_stocks.index,
        'y': short_term_stocks['Close'],
        'type': 'scatter',
        'name': 'Short Term Stocks'
    }

    # Create the layout for the graph
    layout = {
        'title': 'Stock Prices',
        'xaxis': {'title': 'Date'},
        'yaxis': {'title': 'Closing Price ($)', 'range': [sensex_data['Close'].min(), sensex_data['Close'].max()]},
    }

    # Combine the traces and layout into a figure and return it

    # Combine the traces and layout into a figure and return it
    return {'data': [long_trace, short_trace], 'layout': layout}


# day to day change
@ app.callback(Output('day-to-day-change', 'figure'),
               [Input('stkk2', 'value')],
               [Input('overall2', 'value')])
def update_day_to_day_change(stock_name, time_period):
    end_date = dt.date.today()

    if time_period == '6mo':
        start_date = end_date - dt.timedelta(days=180)
    elif time_period == '1y':
        start_date = end_date - dt.timedelta(days=365)
    elif time_period == '5y':
        start_date = end_date - dt.timedelta(days=1825)
    elif time_period == '10y':
        start_date = end_date - dt.timedelta(days=3650)
    elif time_period == '20y':
        start_date = end_date - dt.timedelta(days=7300)
    else:
        start_date = end_date - dt.timedelta(days=365)

    stock_data = yf.download(stock_name, start=start_date, end=end_date)
    print(stock_data)
    stock_data['Change'] = stock_data['Close'] - stock_data['Close'].shift(1)

    # Create a line chart of the day-to-day change
    fig = go.Figure(data=go.Scatter(
        x=stock_data.index, y=stock_data['Change']))
    fig.update_layout(title='Day-to-day Change',
                      xaxis_title='Date',
                      yaxis_title='Change')

    return fig


# Define the callback for candlestick chart
@ app.callback(
    Output('graph', 'figure'),
    [Input('symbol-dropdown', 'value'),
     Input('period-dropdown', 'value')])
def update_figure(symbol, period):
    # Load stock data
    df = yf.Ticker(symbol).history(period=period)

    # Create the candlestick chart trace
    trace = go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])

    # Create the figure layout
    layout = go.Layout(
        xaxis_rangeslider_visible=False,
        yaxis=dict(title='Price'),
        xaxis=dict(title='Date'),
    )

    # Create the figure object
    fig = go.Figure(data=[trace], layout=layout)

    return fig

# Define the callback for average-sensex-hike graph


@ app.callback(Output('average-sensex-hike', 'figure'),
               [Input('overall-time-period', 'value'),
               Input('rolling-mean-time', 'value')])
def update_graph(time_period, rolling_mean_time):
    end_date = dt.date.today()

    if time_period == '6mo':
        start_date = end_date - dt.timedelta(days=180)
    elif time_period == '1y':
        start_date = end_date - dt.timedelta(days=365)
    elif time_period == '5y':
        start_date = end_date - dt.timedelta(days=1825)
    elif time_period == '10y':
        start_date = end_date - dt.timedelta(days=3650)
    elif time_period == '20y':
        start_date = end_date - dt.timedelta(days=7300)
    else:
        start_date = end_date - dt.timedelta(days=365)

    sensex_data = yf.download("^BSESN", start=start_date, end=end_date)
    sensex_data['Daily Return'] = sensex_data['Adj Close'].pct_change()
    rolling_avg = sensex_data['Daily Return'].rolling(
        window=rolling_mean_time).mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=sensex_data.index, y=rolling_avg,
                  mode='lines', name='Rolling Average'))
    # fig.update_layout(title='Average Sensex Hike', xaxis_title='Date', yaxis_title='Average Daily Return', )

    fig.update_layout(
        title='Average Sensex Hike',
        xaxis_title='Date',
        yaxis_title='Average Daily Return',
        hovermode='x unified',
        xaxis=dict(showspikes=True, spikemode='across', spikedash='dot'),
        yaxis=dict(showspikes=True, spikemode='across', spikedash='dot')
    )

    fig.add_shape(
        dict(
            type='line',
            x0=sensex_data.index[0],
            y0=0,
            x1=sensex_data.index[-1],
            y1=0,
            line=dict(
                color='black',
                width=1,
                dash='dash'
            )
        )
    )

    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(count=5, label="5y", step="year", stepmode="backward")

                ])
            ),
            rangeslider=dict(visible=True),
            type="date"
        )
    )

    return fig


# Define the callback for stock vs. sensex graph
@ app.callback(Output('stock-vs-sensex', 'figure'),
               [Input('input-box', 'value'),
               Input('stock-attribute', 'value'),
               Input('time-period', 'value')])
def update_stock_vs_sensex(ticker, attribute, time_period):
    tickers = ticker
    # Get data for selected stock and Sensex
    end_date = dt.date.today()
    if time_period == '1mo':
        start_date = end_date - dt.timedelta(days=30)
    elif time_period == '3mo':
        start_date = end_date - dt.timedelta(days=90)
    elif time_period == '6mo':
        start_date = end_date - dt.timedelta(days=180)
    elif time_period == '1y':
        start_date = end_date - dt.timedelta(days=365)
    elif time_period == '5y':
        start_date = end_date - dt.timedelta(days=1825)
    else:
        start_date = end_date - dt.timedelta(days=365)

    data = []
    tmp = None
    if type(tickers) == str:
        stock_data = yf.download(tickers, start=start_date, end=end_date)
        trace = go.Scatter(x=stock_data.index,
                           y=stock_data[attribute], name=tickers)
        tmp = tickers
        data.append(trace)
    else:
        for ticker in tickers:
            # print(ticker, type(ticker))
            stock_data = yf.download(ticker, start=start_date, end=end_date)
            trace = go.Scatter(x=stock_data.index,
                               y=stock_data[attribute], name=ticker)
            data.append(trace)
            tmp = ','.join(tickers)

    layout = go.Layout(
        title=f'{attribute} - Comparison of {tmp} over {time_period}',
        yaxis=dict(title='Price(₹)'),
        hovermode='x unified',
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),


                ])
            ),
            rangeslider=dict(visible=True),
            type="date"
        )
    )
    return {'data': data, 'layout': layout}


# Define the callback for pair plots
@ app.callback(Output('pair-plots', 'figure'),
               [Input('input-box1', 'value')])
def update_graph(stock_symbol):
    # Get data for stock
    stock_data = yf.download(
        stock_symbol, start='2022-01-01', end='2023-04-06')

    # Create pair plot
    fig = px.scatter_matrix(stock_data,
                            dimensions=['Open', 'High',
                                        'Low', 'Close', 'Adj Close'],
                            color='Volume')

    # Update layout
    fig.update_layout(title=f'{stock_symbol} Pair Plots')

    # Return figure
    return fig


# ===============================================================================================================================================================
@ app.callback(
    Output('risk-analysis-graph', 'figure'),
    [Input('st', 'value'),
     Input('overall', 'value'),
     Input('prediction-time', 'value')]
)
# def update_risk_analysis_graph(stock, tot_time, prediction_time):
#     end_date = dt.date.today()
# #  we predict from end_date to till after looking at start_time to till data
#     if prediction_time == '30':
#         till = end_date - dt.timedelta(days=30)
#     elif prediction_time == '60':
#         till = end_date - dt.timedelta(days=60)
#     elif prediction_time == '90':
#         till = end_date - dt.timedelta(days=90)
#     else:
#         till = end_date - dt.timedelta(days=30)
#     actual_data = yf.download(stock, start=till, end=end_date)
#     # =================================================================
#     end_date = dt.date.today()
#     if tot_time == '6mo':
#         start_date = till - dt.timedelta(days=180)
#     elif tot_time == '1y':
#         start_date = till - dt.timedelta(days=365)
#     elif tot_time == '5y':
#         start_date = till - dt.timedelta(days=1825)
#     elif tot_time == '10y':
#         start_date = till - dt.timedelta(days=3650)
#     elif tot_time == '20y':
#         start_date = till - dt.timedelta(days=7300)
#     else:
#         start_date = till - dt.timedelta(days=365)
#     analyse_data = yf.download(stock, start=start_date, end=till)
#     # using the analyse_data we will predict the expected value for 'prediction_time' time period and plot it alongside actual_data
#     # Perform linear regression on the analyse_data
#     X = np.arange(len(analyse_data)).reshape(-1, 1)
#     Y = analyse_data['Close']
#     try:
#         model = Pipeline(
#             [('poly', PolynomialFeatures(degree=2)), ('linear', LinearRegression())])
#         model.fit(X, Y)
#     except ValueError:
#         model = LinearRegression().fit(X, Y)
#     # Predict the stock price for the next prediction_time days
#     num_days = int(prediction_time)
#     X_pred = np.arange(len(analyse_data), len(
#         analyse_data) + num_days).reshape(-1, 1)
#     y_pred = model.predict(X_pred)
#     # Create a datetime index for the predicted values
#     pred_dates = pd.date_range(start=till, periods=num_days, freq='D')
#     # Combine actual data with predicted data
#     combined_data = pd.concat(
#         [actual_data['Close'], pd.Series(y_pred, index=pred_dates)], axis=0)
# # Create the plot
#     fig = go.Figure()
#     fig.add_trace(go.Scatter(x=combined_data.index,
#                   y=combined_data, name='Actual'))
#     fig.add_trace(go.Scatter(x=pred_dates, y=y_pred, name='Expected'))
#     fig.update_layout(title='Risk Analysis Graph',
#                       xaxis_title='Date', yaxis_title='Stock Price')
#     return fig
#    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ===============================================================================================================================================================
# Define function to calculate expected stock price using Monte Carlo simulation
def monte_carlo_simulation(start_price, days, mu, sigma, num_simulations):
    dt = 1 / 252  # time interval for simulation
    prices = np.zeros((days, num_simulations))  # initialize prices array
    prices[0] = start_price  # set the initial price

    for i in range(1, days):
        # calculate the daily returns
        daily_returns = np.exp((mu - 0.5 * sigma ** 2) * dt + sigma *
                               np.sqrt(dt) * norm.ppf(np.random.rand(num_simulations)))

        # calculate the new prices
        prices[i] = prices[i-1] * daily_returns

    return prices


@ app.callback(
    [Output('monte-carlo', 'figure'), Output('monte-carlo-dist', 'figure')],
    [Input('stk', 'value'),
     Input('sim', 'value'),
     Input('time', 'value')]
)
def update_risk_analysis_graph_monte_carlo(stock, simulations, prediction_time):
    end_date = dt.date.today()

    if prediction_time == '30':
        days = 30
    elif prediction_time == '60':
        days = 60
    else:
        days = 90

    start_date = end_date - dt.timedelta(days=730)
    data = yf.download(stock, start=start_date, end=end_date)

    # calculate the daily returns
    returns = np.log(1 + data['Close'].pct_change()).dropna()

    # calculate the expected return and volatility
    mu = returns.mean()
    sigma = returns.std()

    # get the last closing price
    start_price = data['Close'][-1]

    # perform Monte Carlo simulation
    if simulations == '5':
        num_simulations = 5
    elif simulations == '50':
        num_simulations = 50
    elif simulations == '500':
        num_simulations = 500
    else:
        num_simulations = 100

    prices = monte_carlo_simulation(
        start_price, days, mu, sigma, num_simulations)

    # plot the results
    fig = go.Figure()

    for i in range(num_simulations):
        fig.add_trace(go.Scatter(
            x=data.index, y=prices[:, i], mode='lines', name='Simulation ' + str(i+1)))

    fig.update_layout(title='Monte Carlo Simulation',
                      xaxis_title='Date', yaxis_title='Stock Price')
    # return fig

    #  plot the distribution of final results
    final_prices = prices[-1, :]
    fig_dist = go.Figure()
    fig_dist.add_trace(go.Histogram(
        x=final_prices, nbinsx=20, name='Final Prices'))
    fig_dist.add_vline(x=np.percentile(final_prices, 1),
                       line_dash='dash', line_color='red', name='1% Quantile')
    fig_dist.update_layout(title='Distribution of Final Prices',
                           xaxis_title='Final Stock Price at 1% Quartile', yaxis_title='Frequency',  bargap=0.1)

    return fig, fig_dist


# Run the app
if __name__ == '__main__':
    app.run_server(port=8051, debug=True)
