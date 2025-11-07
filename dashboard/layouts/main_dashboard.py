from dash import html, dcc, dash_table
import plotly.express as px
import numpy as np
import pandas as pd


def create_main_dashboard_layout(merged_df):
    """
    Returns the main dashboard layout for the PPRA Contracts Intelligence Dashboard.
    """
    return html.Div([
        html.H1("📊 PPRA Contracts Intelligence Dashboard", style={"textAlign": "center"}),

        # Summary Cards
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
                    options=[
                        {"label": b, "value": b}
                        for b in sorted(merged_df["buyer_name"].dropna().unique())
                    ],
                    id="buyer-filter",
                    placeholder="Select buyer..."
                )
            ], style={"width": "45%", "display": "inline-block"}),

            html.Div([
                html.Label("Filter by Year:"),
                dcc.Dropdown(
                    options=[
                        {"label": int(y), "value": int(y)}
                        for y in sorted(merged_df["year"].dropna().unique())
                    ],
                    id="year-filter",
                    placeholder="Select year..."
                )
            ], style={
                "width": "45%",
                "display": "inline-block",
                "marginLeft": "20px"
            })
        ], style={"padding": "20px"}),

        html.Hr(),

        # Charts Grid (with default figures to show initial visuals)
        html.Div([
            dcc.Graph(
                id="contracts-by-year",
                figure=px.bar(
                    merged_df.groupby("year")["total_value_kes"].sum().reset_index(),
                    x="year", y="total_value_kes",
                    title="Contracts by Year"
                )
            ),

            dcc.Graph(
                id="top-buyers",
                figure=px.bar(
                    merged_df.groupby("buyer_name")["total_value_kes"].sum().nlargest(10).reset_index(),
                    x="buyer_name", y="total_value_kes",
                    title="Top 10 Buyers"
                )
            ),

            dcc.Graph(
                id="procurement-methods",
                figure=px.pie(
                    merged_df, names="tender_procurementmethod",
                    title="Procurement Methods"
                )
            ),

            dcc.Graph(
                id="anomalies-by-cluster",
                figure=px.bar(
                    merged_df.groupby("cluster")["is_anomaly"].mean().reset_index(),
                    x="cluster", y="is_anomaly",
                    title="Anomalies by Cluster"
                )
            ),

            dcc.Graph(
                id="value-vs-duration",
                figure=px.scatter(
                    merged_df, x="contract_duration_days", y="total_value_kes",
                    color="is_anomaly",
                    title="Value vs Duration (with Anomalies)"
                )
            ),

            dcc.Graph(
                id="cluster-distribution",
                figure=px.histogram(
                    merged_df, x="cluster",
                    title="Cluster Distribution"
                )
            )
        ], style={
            "display": "grid",
            "gridTemplateColumns": "1fr 1fr",
            "gap": "20px"
        }),

        html.Hr(),

        # Contract Explorer
        html.Div([
            html.H2("📂 Contract Explorer", style={
                "textAlign": "center",
                "marginBottom": "10px"
            }),
            html.P(
                "Explore individual contract records below. Use filters and search to drill down into specific contracts.",
                style={"textAlign": "center", "color": "#555"}
            ),

            dash_table.DataTable(
                id="contracts-table",
                columns=[
                    {"name": "Buyer", "id": "buyer_name"},
                    {"name": "Supplier", "id": "identifier_legalname"},
                    {"name": "Tender Title", "id": "title"},
                    {"name": "Contract Value (KES)", "id": "total_value_kes"},
                    {"name": "Procurement Method", "id": "tender_procurementmethod"},
                    {"name": "Start Date", "id": "contract_start_date"},
                    {"name": "End Date", "id": "contract_end_date"},
                    {"name": "Year", "id": "year"},
                    {"name": "Cluster", "id": "cluster"}
                ],
                data=merged_df.head(200).to_dict("records"),
                page_size=25,
                sort_action="native",
                filter_action="native",
                style_table={"overflowX": "auto"},
                style_cell={
                    "textAlign": "left",
                    "padding": "5px",
                    "fontSize": "14px"
                },
                style_header={
                    "backgroundColor": "#f2f2f2",
                    "fontWeight": "bold"
                }
            )
        ], style={"padding": "20px", "marginBottom": "50px"})
    ])


# Export layout
main_dashboard_layout = create_main_dashboard_layout
