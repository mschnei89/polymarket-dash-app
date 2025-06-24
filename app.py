from dash import Dash, dcc, html, Input, Output
import pandas as pd
import plotly.graph_objs as go

# Load the data
df = pd.read_csv("Fed_rate_panel_data.csv")

# Parse dates
df['trade_date'] = pd.to_datetime(df['trade_date'])

# Filter only "Yes" token outcomes
df = df[df['token_outcome_name'].str.lower().str.startswith("yes")]

# Initialize the app
app = Dash(__name__)

# Layout
app.layout = html.Div([
    html.H1("Polymarket Price Visualization", style={'textAlign': 'center'}),
    html.Label("Select a Market:"),
    dcc.Dropdown(
        id='market-dropdown',
        options=[{'label': name, 'value': name} for name in sorted(df['event_market_name'].unique())],
        value=df['event_market_name'].iloc[0]
    ),
    dcc.Graph(id='line-chart')
])

# Callback
@app.callback(
    Output('line-chart', 'figure'),
    Input('market-dropdown', 'value')
)
def update_chart(selected_market):
    filtered = df[df['event_market_name'] == selected_market]

    fig = go.Figure()

    for q in filtered['question'].unique():
        sub = filtered[filtered['question'] == q]
        fig.add_trace(go.Scatter(
            x=sub['trade_date'], y=sub['avg_price'],
            mode='lines', name=q
        ))

    # Volume bar chart
    fig.add_trace(go.Bar(
        x=filtered['trade_date'],
        y=filtered['daily_volume'],
        name='Volume',
        yaxis='y2',
        marker_color='gray',
        opacity=0.6
    ))

    # Layout
    fig.update_layout(
        title=f"Price Trends for '{selected_market}'",
        yaxis=dict(title='Price', range=[0, 1]),
        yaxis2=dict(title='Volume', overlaying='y', side='right'),
        legend=dict(x=0, y=1.1, orientation="h"),
        margin=dict(l=40, r=40, t=40, b=40)
    )

    return fig

app.server = app.server  # for gunicorn

if __name__ == '__main__':
    app.run(debug=True)
