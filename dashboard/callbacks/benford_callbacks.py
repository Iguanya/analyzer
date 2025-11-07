from dash import Input, Output, State, no_update
from dash.exceptions import PreventUpdate
import pandas as pd
from dashboard.utils.benford_utils import run_benford_for_column

import logging
logging.basicConfig(level=logging.INFO)

def register_benford_callbacks(app, merged_df):
    """Register automatic Benford’s Law Analysis callbacks with logging."""

    @app.callback(
        [
            Output("benford-report", "children"),
            Output("benford-img", "src"),
            Output("benford-table", "data"),
        ],
        [
            Input("benford-url", "pathname"),
            Input("benford-column", "value"),
            Input("buyer-filter", "value"),
            Input("year-filter", "value"),
        ],
        prevent_initial_call=False  # allow auto-trigger on first load
    )
    def on_auto_run_benford(pathname, benford_col, selected_buyer, selected_year):
        print("[LOG] Callback triggered for Benford page.")

        # Only run if user is on /benford
        if not pathname or not pathname.endswith("/benford"):
            print("[LOG] Not on Benford page, skipping callback.")
            raise PreventUpdate

        print("[LOG] Running Benford analysis...")
        df = merged_df.copy()

        # Apply filters if any
        if selected_buyer:
            print(f"[LOG] Filtering by buyer: {selected_buyer}")
            df = df[df["buyer_name"] == selected_buyer]
        if selected_year:
            print(f"[LOG] Filtering by year: {selected_year}")
            df = df[df["year"] == selected_year]

        # Determine column to check
        column_to_check = benford_col or "total_value_kes"
        print(f"[LOG] Using column for analysis: {column_to_check}")

        if column_to_check not in df.columns:
            print(f"[ERROR] Column '{column_to_check}' not found in dataframe.")
            return f"⚠️ Column '{column_to_check}' not found.", no_update, []

        # Prepare numeric data
        df[column_to_check] = pd.to_numeric(df[column_to_check], errors="coerce")
        df = df.dropna(subset=[column_to_check])
        if df.empty:
            print(f"[WARN] No valid numeric data found in '{column_to_check}'.")
            return f"⚠️ No valid numeric data in '{column_to_check}'.", no_update, []

        # Run Benford analysis
        try:
            print("[LOG] Executing Benford analysis function...")
            report, b64_img, suspect_df = run_benford_for_column(df, column_to_check)
            print("[LOG] Benford analysis completed successfully.")
        except Exception as e:
            print(f"[ERROR] Exception during Benford analysis: {e}")
            return f"❌ Error during Benford analysis: {e}", no_update, []

        # Prepare outputs
        img_src = (
            b64_img if isinstance(b64_img, str) and b64_img.startswith("data:image")
            else f"data:image/png;base64,{b64_img}" if b64_img else None
        )
        table_data = suspect_df.to_dict("records") if not suspect_df.empty else []

        print(f"[LOG] Returning {len(table_data)} suspect records.")
        
        # Before returning
        logging.info("📘 Benford Table Data Columns: %s", df.columns.tolist())
        logging.info("📊 Sample rows:\n%s", df.head(5).to_string())

        return report, img_src, table_data
