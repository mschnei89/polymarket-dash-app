import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go

# Load and prepare data
df = pd.read_csv('Fed_rate_panel_data.csv')
df['trade_date'] = pd.to_datetime(df['trade_date'])

# Filter for 'Yes-' token outcomes only
df = df[df['token_outcome_name'].str.lower().str.startswith('yes')]

# Initialize Dash app
dash_app = Dash(__name__)
app = dash_app.server  # gunicorn needs this

# Layout
dash_app.layout = html.Div([
    html.H2("Polymarket Price & Volume Viewer"),
    dcc.Dropdown(
        id='market-dropdown',
        options=[
            {'label': name, 'value': name}
            for name in sorted(df['event_market_name'].unique())
        ],
        value=sorted(df['event_market_name'].unique())[0]
    ),
    dcc.Graph(id='price-volume-graph')
])

# Callback
@dash_app.callback(
    Output('price-volume-graph', 'figure'),
    Input('market-dropdown', 'value')
)
def update_graph(selected_market):
    dff = df[df['event_market_name'] == selected_market]
    
    fig = go.Figure()

    for question in dff['question'].unique():
        question_df = dff[dff['question'] == question]
        fig.add_trace(go.Scatter(
            x=question_df['trade_date'],
            y=question_df['avg_price'],
            mode='lines',
            name=question,
            yaxis='y1'
        ))

    volume_df = (
        dff.groupby('trade_date')['daily_volume'].sum().reset_index()
    )

    fig.add_trace(go.Bar(
        x=volume_df['trade_date'],
        y=volume_df['daily_volume'],
        name='Volume',
        yaxis='y2',
        marker=dict(color='gray'),
        opacity=0.6
    ))

    fig.update_layout(
        title=f"Price & Volume: {selected_market}",
        xaxis=dict(title='Date'),
        yaxis=dict(title='Avg Price', side='left'),
        yaxis2=dict(
            title='Volume',
            overlaying='y',
            side='right',
            showgrid=False
        ),
        legend=dict(x=0, y=1),
        bargap=0.2,
        height=600
    )

    return fig

# Local dev only
if __name__ == '__main__':
    dash_app.run_server(debug=True)
