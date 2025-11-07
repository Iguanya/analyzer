from dash import Dash, dcc, html, Input, Output
from flask import Flask
import sys, os

# Local imports
from dashboard.data_loader import load_merged_data
from dashboard.layouts.main_dashboard import create_main_dashboard_layout
from dashboard.layouts.benford_page import benford_page_layout
from dashboard.callbacks.callbacks import register_callbacks
from dashboard.callbacks.benford_callbacks import register_benford_callbacks

# Ensure relative imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def init_dashboard(server: Flask):
    """Initialize and mount Dash app on Flask server."""

    print("🚀 [Dashboard] Initializing Dash application...")

    # --- Load merged data once ---
    merged_df = load_merged_data()
    print(f"📦 [Dashboard] Loaded merged_df with shape: {merged_df.shape}")

    # --- Create Dash app instance ---
    app = Dash(
        __name__,
        server=server,
        url_base_pathname="/dashboard/",
        suppress_callback_exceptions=True,
        title="PPRA Contracts Dashboard"
    )

    # --- Define navigation bar ---
    def navbar():
        return html.Div(
            [
                dcc.Link("🏠 Home", href="/dashboard/", className="nav-link"),
                dcc.Link("📊 Dashboard", href="/dashboard/main", className="nav-link"),
                dcc.Link("📈 Benford Analysis", href="/dashboard/benford", className="nav-link"),
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
                "position": "sticky",
                "top": "0",
                "zIndex": "1000"
            }
        )

    # --- Base app layout ---
    app.layout = html.Div([
        dcc.Location(id="url", refresh=False),
        html.Div(id="page-content")
    ])

    # --- Page router callback ---
    @app.callback(
        Output("page-content", "children"),
        [Input("url", "pathname")]
    )
    def display_page(pathname):
        """Router function for Dash pages"""
        print(f"🔄 [Router] Navigating to: {pathname}")

        if pathname in ["/dashboard", "/dashboard/"]:
            return html.Div([
                navbar(),
                html.H2("🏠 Welcome to the PPRA Contracts Intelligence Portal",
                        style={"textAlign": "center", "marginTop": "40px"}),
                html.P("Use the navigation bar above to explore analytics and insights.",
                       style={"textAlign": "center"})
            ])

        elif pathname == "/dashboard/main":
            print("📊 [Router] Loading Main Dashboard Page")
            return html.Div([
                navbar(),
                create_main_dashboard_layout(merged_df)
            ])

        elif pathname == "/dashboard/benford":
            print("📈 [Router] Loading Benford Analysis Page")
            return html.Div([
                navbar(),
                benford_page_layout(app, merged_df)
            ])

        else:
            print("❌ [Router] 404 - Page not found")
            return html.Div([
                navbar(),
                html.H3("404 - Page not found", style={"textAlign": "center", "color": "red"})
            ])

    # --- Register callbacks globally ---
    print("⚙️ [Dashboard] Registering callbacks...")
    register_callbacks(app, merged_df)
    register_benford_callbacks(app, merged_df)

    print("✅ [Dashboard] All callbacks registered successfully.")
    return app
