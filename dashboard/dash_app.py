from dash import Dash, dcc, html, dash_table, Input, Output
from flask import Flask
import plotly.express as px
import pandas as pd
import os


def init_dashboard(server):
    """
    Initialize and mount the Dash dashboard to a Flask server.
    """

    # --- Load dataset ---
    DATA_PATH = os.path.join(os.path.dirname(__file__), "merged_ppra_data.csv")
    merged_df = pd.read_csv(DATA_PATH)

    # --- Clean Data ---
    for col in ["total_value_kes", "contract_duration_days", "anomaly_score"]:
        if col in merged_df.columns:
            merged_df[col] = pd.to_numeric(merged_df[col], errors="coerce")

    # --- Create Dash app ---
    app = Dash(
        __name__,
        server=server,
        url_base_pathname="/dashboard/",
        suppress_callback_exceptions=True,
        title="PPRA Contracts Dashboard"
    )

    # --- Layout ---
    app.layout = html.Div([
        html.H1("📊 PPRA Contracts Intelligence Dashboard", style={"textAlign": "center"}),

        # Summary cards
        html.Div([
            html.Div([
                html.H4("Total Contracts"),
                html.H2(f"{len(merged_df):,}")
            ], className="card"),

            html.Div([
                html.H4("Total Value (KES)"),
                html.H2(f"{merged_df['total_value_kes'].sum():,.0f}")
            ], className="card"),

            html.Div([
                html.H4("Anomalies (%)"),
                html.H2(f"{(merged_df['is_anomaly'].mean() * 100):.2f}%")
            ], className="card"),

            html.Div([
                html.H4("Avg. Duration (Days)"),
                html.H2(f"{merged_df['contract_duration_days'].mean():.0f}")
            ], className="card")
        ], style={
            "display": "flex",
            "justifyContent": "space-around",
            "padding": "20px",
            "flexWrap": "wrap"
        }),

        html.Hr(),

        # Filters
        html.Div([
            html.Div([
                html.Label("Filter by Buyer:"),
                dcc.Dropdown(
                    options=[{"label": b, "value": b} for b in sorted(merged_df["buyer_name"].dropna().unique())],
                    id="buyer-filter", multi=False, placeholder="Select buyer..."
                )
            ], style={"width": "45%", "display": "inline-block"}),

            html.Div([
                html.Label("Filter by Year:"),
                dcc.Dropdown(
                    options=[{"label": int(y), "value": int(y)} for y in sorted(merged_df["year"].dropna().unique())],
                    id="year-filter", multi=False, placeholder="Select year..."
                )
            ], style={"width": "45%", "display": "inline-block", "marginLeft": "20px"})
        ], style={"padding": "20px"}),

        # Charts Grid
        html.Div([
            dcc.Graph(id="contracts-by-year"),
            dcc.Graph(id="top-buyers"),
            dcc.Graph(id="procurement-methods"),
            dcc.Graph(id="anomalies-by-cluster"),
            dcc.Graph(id="value-vs-duration"),
            dcc.Graph(id="cluster-distribution")
        ], style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "20px"}),

        html.Hr(),

        html.H3("🔍 Contract Explorer"),
        dash_table.DataTable(
            id="contracts-table",
            columns=[{"name": i, "id": i} for i in [
                "buyer_name", "identifier_legalname", "title", "total_value_kes", "contract_duration_days",
                "year", "is_anomaly", "anomaly_score"
            ] if i in merged_df.columns],
            data=merged_df.head(200).to_dict("records"),
            page_size=100,
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "left", "padding": "5px"},
            filter_action="native",
            sort_action="native"
        )
    ])

    # --- Callbacks ---
    @app.callback(
        [
            Output("contracts-by-year", "figure"),
            Output("top-buyers", "figure"),
            Output("procurement-methods", "figure"),
            Output("anomalies-by-cluster", "figure"),
            Output("value-vs-duration", "figure"),
            Output("cluster-distribution", "figure"),
            Output("contracts-table", "data")
        ],
        [Input("buyer-filter", "value"),
         Input("year-filter", "value")]
    )
    def update_dashboard(selected_buyer, selected_year):
        df = merged_df.copy()

        if selected_buyer:
            df = df[df["buyer_name"] == selected_buyer]
        if selected_year:
            df = df[df["year"] == selected_year]

        # 1️⃣ Contracts by Year
        fig_year = px.bar(
            df.groupby("year")["total_value_kes"].sum().reset_index(),
            x="year", y="total_value_kes", title="Contract Value by Year"
        )

        # 2️⃣ Top Buyers
        fig_buyers = px.bar(
            df.groupby("buyer_name")["total_value_kes"].sum().nlargest(10).reset_index(),
            x="buyer_name", y="total_value_kes", title="Top 10 Buyers", text_auto=True
        )
        fig_buyers.update_xaxes(tickangle=45)

        # 3️⃣ Procurement Methods
        fig_methods = px.pie(
            df, names="tender_procurementmethod", title="Procurement Methods Distribution"
        )

        # 4️⃣ Anomalies by Cluster
        fig_anomalies = px.bar(
            df.groupby("cluster")["is_anomaly"].sum().reset_index(),
            x="cluster", y="is_anomaly", title="Anomalies by Cluster"
        )

        # 5️⃣ Contract Value vs Duration
        fig_value_duration = px.scatter(
            df, x="contract_duration_days", y="total_value_kes",
            color="is_anomaly",
            title="Contract Value vs Duration (Highlighting Anomalies)",
            labels={"contract_duration_days": "Duration (Days)", "total_value_kes": "Value (KES)"}
        )

        # 6️⃣ Cluster Distribution
        fig_cluster_dist = px.bar(
            df["cluster"].value_counts().reset_index(),
            x="count", y="cluster",
            labels={"index": "Cluster", "cluster": "Count"},
            title="Cluster Distribution"
        )

        table_data = df.head(200).to_dict("records")

        return (
            fig_year, fig_buyers, fig_methods, fig_anomalies,
            fig_value_duration, fig_cluster_dist, table_data
        )

    return app
