import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import requests
import pandas as pd
import datetime
import argparse

# --- App Definition with Bootstrap Theme ---
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

# --- Global variable for API URL ---
API_URL_BASE = "http://127.0.0.1:8001" # Default value

# --- Helper Functions ---
def make_metric_card(title, value):
    """Creates a styled metric card."""
    return dbc.Card(
        dbc.CardBody([
            html.H4(title, className="card-title"),
            html.P(value, className="card-text", style={'fontSize': '24px', 'fontWeight': 'bold'})
        ]),
        className="mb-3",
    )

def make_tipsheet_card(race):
    """Creates an enhanced, styled card for a single race on the tipsheet."""
    factors = race.get('trifectaFactors', {})
    badges = []
    if factors.get('speedAdvantage', {}).get('ok'):
        badges.append(dbc.Badge("Speed Advantage", color="success", className="me-1"))
    if factors.get('classEdge', {}).get('ok'):
        badges.append(dbc.Badge("Class Edge", color="info", className="me-1"))
    if factors.get('valueOdds', {}).get('ok'):
        badges.append(dbc.Badge("Value Odds", color="warning", className="me-1"))

    top_horses = race.get('horses', [])[:3]
    horse_list_items = []
    if top_horses:
        for horse in top_horses:
            horse_list_items.append(html.Li(
                f"#{horse.get('number', 'N/A')} {horse.get('name', 'N/A')} ({horse.get('odds', 0.0):.1f}/1)"
            ))
    else:
        horse_list_items.append(html.Li("No horse data available."))

    return dbc.Card(
        dbc.CardBody([
            html.H3(f"{race.get('track')} - Race {race.get('raceNumber')}", className="card-title"),
            html.P(f"Post Time: {datetime.datetime.fromisoformat(race.get('postTime').replace('Z', '+00:00')).strftime('%H:%M')} | Score: {race.get('checkmateScore', 0):.2f}"),
            html.Div(badges, className="mb-3"),
            html.Hr(),
            html.H4("Top Contenders"),
            html.Ul(horse_list_items)
        ]),
        className="mb-3",
    )

# --- App Layout ---
app.layout = dbc.Container(fluid=True, children=[
    dbc.Row(dbc.Col(html.H1("Checkmate V7 - Cockpit", className="text-center my-4"), width=12)),
    dbc.Row([
        dbc.Col(dbc.Card(dbc.CardBody(id='tipsheet-container')), width=8),
        dbc.Col([
            dbc.Card(dbc.CardBody(id='metric-cards-container'), className="mb-3"),
            dbc.Card(dbc.CardBody(id='feed-status-container'))
        ], width=4)
    ]),
    dcc.Interval(id='interval-component', interval=5*1000, n_intervals=0)
])

# --- Callbacks ---
@app.callback(
    [Output('metric-cards-container', 'children'),
     Output('tipsheet-container', 'children'),
     Output('feed-status-container', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_live_data(n):
    try:
        races_response = requests.get(f'{API_URL_BASE}/api/v1/races/all')
        races_response.raise_for_status()
        races = races_response.json()

        status_response = requests.get(f'{API_URL_BASE}/api/v1/adapters/status')
        status_response.raise_for_status()
        statuses = status_response.json()

        qualified_races = [race for race in races if race.get('qualified', False)]

        metric_cards = [
            html.H2('Metrics', className="card-title"),
            make_metric_card('Total Races Analyzed', len(races)),
            make_metric_card('Qualified Races', len(qualified_races))
        ]

        if qualified_races:
            tipsheet_cards = [make_tipsheet_card(race) for race in qualified_races]
            tipsheet = [html.H2('Live Tipsheet', className="card-title"), *tipsheet_cards]
        else:
            tipsheet = [html.H2('Live Tipsheet', className="card-title"), html.P('No qualified races at the moment.')]

        status_items = []
        for status in statuses:
            color = "success" if status.get('status') == "OK" else "danger"
            status_text = f"{status.get('adapter_id')}: {status.get('status')} ({status.get('races_found')} found)"
            notes = status.get('notes')
            if notes:
                status_text += f" - {notes}"
            status_items.append(dbc.ListGroupItem(status_text, color=color))

        feed_status = [
            html.H2('Feed Status', className="card-title"),
            html.P(f"Last Update: {datetime.datetime.now().strftime('%H:%M:%S')}"),
            dbc.ListGroup(status_items, flush=True)
        ]
        return metric_cards, tipsheet, feed_status

    except requests.exceptions.RequestException as e:
        error_message = str(e)
        metric_cards_error = [html.H2('Metrics'), html.P('Error')]
        tipsheet_error = [html.H2('Live Tipsheet'), html.P(f"API Error: {error_message}")]
        status_display_error = [
            html.H2('Feed Status'),
            html.P(f"Last Update Attempt: {datetime.datetime.now().strftime('%H:%M:%S')}"),
            html.P(f"Status: API Connection Failed - {error_message}", className="text-danger")
        ]
        return metric_cards_error, tipsheet_error, status_display_error

# --- Main Execution ---
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run the Checkmate Cockpit Dash app.")
    parser.add_argument('--port', type=int, default=8050, help='Port to run the app on.')
    parser.add_argument('--api-url', type=str, default="http://127.0.0.1:8001", help='URL of the backend API.')
    args = parser.parse_args()

    API_URL_BASE = args.api_url

    app.run(debug=True, host='0.0.0.0', port=args.port)
