import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import requests
import pandas as pd
import datetime

# --- Styles ---
STYLES = {
    'app-container': {
        'fontFamily': 'Arial, sans-serif',
        'backgroundColor': '#f0f2f5',
        'padding': '20px'
    },
    'header': {
        'textAlign': 'center',
        'marginBottom': '20px'
    },
    'main-content': {
        'display': 'flex',
        'flexDirection': 'row',
        'gap': '20px'
    },
    'left-column': {
        'flex': '3'
    },
    'right-column': {
        'flex': '1',
        'display': 'flex',
        'flexDirection': 'column',
        'gap': '20px'
    },
    'content-box': {
        'border': '1px solid #ddd',
        'borderRadius': '5px',
        'padding': '20px',
        'backgroundColor': 'white'
    },
    'metric-card': {
        'border': '1px solid #eee',
        'padding': '10px',
        'borderRadius': '5px',
        'marginBottom': '10px'
    },
    'tipsheet-card': {
        'border': '1px solid #ddd',
        'borderRadius': '5px',
        'padding': '15px',
        'marginBottom': '15px',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
    }
}

# --- Helper Functions ---
def make_metric_card(title, value):
    """Creates a styled metric card."""
    return html.Div(style=STYLES['metric-card'], children=[
        html.H4(title),
        html.P(value, style={'fontSize': '24px', 'fontWeight': 'bold'})
    ])

def make_tipsheet_card(race):
    """Creates a styled card for a single race on the tipsheet."""
    top_horse = race.get('horses', [{}])[0]
    return html.Div(style=STYLES['tipsheet-card'], children=[
        html.H3(f"{race.get('track')} - Race {race.get('raceNumber')}"),
        html.P(f"Post Time: {datetime.datetime.fromisoformat(race.get('postTime')).strftime('%H:%M')}"),
        html.Hr(),
        html.H4("Top Selection"),
        html.P(f"#{top_horse.get('number', 'N/A')} {top_horse.get('name', 'N/A')} ({top_horse.get('odds', 'N/A')})"),
        html.Small(f"Jockey: {top_horse.get('jockey', 'N/A')} | Trainer: {top_horse.get('trainer', 'N/A')}")
    ])

# --- App Definition ---
app = dash.Dash(__name__)

app.layout = html.Div(style=STYLES['app-container'], children=[
    html.Div(style=STYLES['header'], children=[
        html.H1(children='Checkmate V7 - Cockpit')
    ]),

    html.Div(style=STYLES['main-content'], children=[
        html.Div(style=STYLES['left-column'], children=[
            html.Div(id='tipsheet-container', style=STYLES['content-box'])
        ]),
        html.Div(style=STYLES['right-column'], children=[
            html.Div(id='metric-cards-container', style=STYLES['content-box']),
            html.Div(id='feed-status-container', style=STYLES['content-box'])
        ])
    ]),

    dcc.Interval(id='interval-component', interval=5*1000, n_intervals=0)
])

@app.callback(
    [Output('metric-cards-container', 'children'),
     Output('tipsheet-container', 'children'),
     Output('feed-status-container', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_live_data(n):
    try:
        response = requests.get('http://127.0.0.1:8000/api/v1/races/all')
        response.raise_for_status()
        races = response.json()

        qualified_races = [race for race in races if race.get('qualified', False)]

        # --- Metric Cards ---
        metric_cards = [
            html.H2('Metrics'),
            make_metric_card('Total Races Analyzed', len(races)),
            make_metric_card('Qualified Races', len(qualified_races))
        ]

        # --- Tipsheet ---
        if qualified_races:
            tipsheet_cards = [make_tipsheet_card(race) for race in qualified_races]
            tipsheet = [html.H2('Live Tipsheet'), *tipsheet_cards]
        else:
            tipsheet = [html.H2('Live Tipsheet'), html.P('No qualified races at the moment.')]

        # --- Feed Status ---
        feed_status = [
            html.H2('Feed Status'),
            html.P(f"Last Update: {datetime.datetime.now().strftime('%H:%M:%S')}"),
            html.P("Status: Connected to API", style={'color': 'green'})
        ]
        return metric_cards, tipsheet, feed_status

    except requests.exceptions.RequestException as e:
        error_message = str(e)
        metric_cards_error = [html.H2('Metrics'), html.P('Error')]
        tipsheet_error = [html.H2('Live Tipsheet'), html.P(f"API Error: {error_message}")]
        status_display_error = [
            html.H2('Feed Status'),
            html.P(f"Last Update Attempt: {datetime.datetime.now().strftime('%H:%M:%S')}"),
            html.P("Status: API Connection Failed", style={'color': 'red'})
        ]
        return metric_cards_error, tipsheet_error, status_display_error

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
