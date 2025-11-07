from dash import html, dcc, dash_table
import numpy as np

def navbar():
    """Reusable navigation bar."""
    return html.Div(
        [
            dcc.Link("🏠 Home", href="/", className="nav-link"),
            dcc.Link("📈 Benford Analysis", href="/benford", className="nav-link"),
            dcc.Link("📊 Dashboard", href="/dashboard", className="nav-link"),
        ],
        className="navbar",
        style={
            "display": "flex",
            "justifyContent": "center",
            "gap": "40px",
            "backgroundColor": "#f8f9fa",
            "padding": "15px",
            "borderBottom": "2px solid #e0e0e0",
            "fontWeight": "bold",
            "fontSize": "16px",
        },
    )

def layout(merged_df):
    return html.Div([
        navbar(),

        html.H1("📊 PPRA Contracts Intelligence Dashboard", 
                style={"textAlign": "center", "marginTop": "20px"}),

        html.Hr(),

        # Your summary cards, filters, graphs, and outlier table go here
        html.Div(id="dashboard-content"),

        html.Hr(),

        html.Div([
            html.A("➡️ Go to Benford Analysis", href="/benford", style={
                "textDecoration": "none",
                "color": "#0066cc",
                "fontWeight": "bold",
                "fontSize": "16px"
            })
        ], style={"textAlign": "center", "margin": "20px"})
    ])
