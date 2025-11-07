from dash import Input, Output
from dash.exceptions import PreventUpdate
import plotly.express as px
import pandas as pd


def register_callbacks(app, merged_df):
    """Main dashboard callbacks (charts, tables)."""

    @app.callback(
        [
            Output("contracts-by-year", "figure"),
            Output("top-buyers", "figure"),
            Output("procurement-methods", "figure"),
            Output("anomalies-by-cluster", "figure"),
            Output("value-vs-duration", "figure"),
            Output("cluster-distribution", "figure"),
            Output("contracts-table", "data"),
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

        if df.empty:
            raise PreventUpdate

        # --- Contracts by Year ---
        fig_year = px.bar(
            df.groupby("year", as_index=False)["total_value_kes"].sum(),
            x="year", y="total_value_kes",
            title="Contract Value by Year"
        )

        # --- Top Buyers ---
        top_buyers = (
            df.groupby("buyer_name", as_index=False)["total_value_kes"].sum()
            .nlargest(10, "total_value_kes")
        )
        fig_buyers = px.bar(
            top_buyers,
            x="buyer_name", y="total_value_kes",
            title="Top 10 Buyers",
            text_auto=True
        )
        fig_buyers.update_xaxes(tickangle=45)

        # --- Procurement Methods ---
        if "tender_procurementmethod" in df.columns:
            fig_methods = px.pie(
                df, names="tender_procurementmethod",
                title="Procurement Methods Distribution"
            )
        else:
            fig_methods = px.pie(names=["No Data"], values=[1])

        # --- Anomalies by Cluster ---
        if "cluster" in df.columns and "is_anomaly" in df.columns:
            anomalies = df.groupby("cluster", as_index=False)["is_anomaly"].sum()
            fig_anomalies = px.bar(anomalies, x="cluster", y="is_anomaly",
                                   title="Anomalies by Cluster")
        else:
            fig_anomalies = px.bar(title="Anomalies by Cluster (No Data)")

        # --- Contract Value vs Duration ---
        if "contract_duration_days" in df.columns:
            fig_value_duration = px.scatter(
                df, x="contract_duration_days", y="total_value_kes",
                color=df["is_anomaly"].map({True: "Anomaly", False: "Normal"})
                if "is_anomaly" in df.columns else None,
                title="Contract Value vs Duration",
                labels={
                    "contract_duration_days": "Duration (Days)",
                    "total_value_kes": "Value (KES)"
                }
            )
        else:
            fig_value_duration = px.scatter(title="No duration data")

        # --- Cluster Distribution ---
        if "cluster" in df.columns:
            cluster_dist = df["cluster"].value_counts().reset_index()
            cluster_dist.columns = ["cluster", "count"]
            fig_cluster_dist = px.bar(
                cluster_dist, x="cluster", y="count",
                title="Cluster Distribution"
            )
        else:
            fig_cluster_dist = px.bar(title="Cluster Distribution (No Data)")

        # --- Table Data ---
        table_data = df.head(200).to_dict("records")

        return (
            fig_year, fig_buyers, fig_methods,
            fig_anomalies, fig_value_duration,
            fig_cluster_dist, table_data
        )
