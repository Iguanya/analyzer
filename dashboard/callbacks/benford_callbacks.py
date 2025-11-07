from dash import Input, Output, State, no_update
from dash.exceptions import PreventUpdate
import pandas as pd
from dashboard.utils.benford_utils import run_benford_for_column

def register_benford_callbacks(app, merged_df):
    """Register callbacks for Benford’s Law Analysis page."""

    @app.callback(
        [
            Output("benford-report", "children"),
            Output("benford-img", "src"),
            Output("benford-table", "data")
        ],
        [
            Input("run-benford", "n_clicks"),
            Input("benford-url", "pathname"),  # triggers when user navigates to this page
        ],
        [
            State("buyer-filter", "value"),
            State("year-filter", "value"),
            State("benford-column", "value")
        ]
    )
    def on_run_benford(n_clicks, pathname, selected_buyer, selected_year, benford_col):
        # Auto-run only if we are on the Benford page
        if pathname and not pathname.endswith("/benford"):
            raise PreventUpdate

        # Run automatically on page load
        if not n_clicks:
            print("[log] Auto-running Benford analysis on page load")
            n_clicks = 1

        # Work on a copy of merged_df
        df = merged_df.copy()

        # Apply filters if available
        if selected_buyer:
            df = df[df["buyer_name"] == selected_buyer]
        if selected_year:
            df = df[df["year"] == selected_year]

        # Use chosen column or default
        column_to_check = benford_col or "total_value_kes"
        if column_to_check not in df.columns:
            return f"⚠️ Column '{column_to_check}' not found.", no_update, []

        df[column_to_check] = pd.to_numeric(df[column_to_check], errors="coerce")
        df = df.dropna(subset=[column_to_check])
        if df.empty:
            return f"⚠️ No valid numeric data in '{column_to_check}'.", no_update, []

        # Run Benford
        try:
            report, b64_img, suspect_df = run_benford_for_column(df, column_to_check)
        except Exception as e:
            return f"❌ Error during Benford analysis: {e}", no_update, []

        img_src = (
            b64_img if isinstance(b64_img, str) and b64_img.startswith("data:image")
            else f"data:image/png;base64,{b64_img}"
            if b64_img else None
        )
        table_data = suspect_df.to_dict("records") if not suspect_df.empty else []

        return report, img_src, table_data
