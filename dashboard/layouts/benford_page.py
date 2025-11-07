from dash import html, dcc, dash_table
import numpy as np
import pandas as pd

# ✅ Import the callback registration function
from dashboard.callbacks.benford_callbacks import register_benford_callbacks


def benford_page_layout(app, merged_df):
    """Layout for Benford’s Law page — dynamically generated, with clean handling."""

    print("🟢 [Benford] Page layout loaded")

    # --- Log dataframe metadata ---
    try:
        print("🔍 [Benford] DataFrame Info:")
        print(f"  → Shape: {merged_df.shape}")
        print(f"  → Columns ({len(merged_df.columns)}): {list(merged_df.columns)}")
        print("📋 [Benford] Sample:")
        print(merged_df.head(3).to_dict(orient="records"))
    except Exception as e:
        print("❌ [Benford] Could not print DataFrame info:", e)

    # --- Normalize column names ---
    merged_df = merged_df.rename(columns={
        "buyer": "buyer_name",
        "supplier_name": "identifier_legalname",
        "contract_title": "title",
        "contract_value": "total_value_kes",
        "contract_year": "year",
    })

    # --- Ensure required columns exist even if missing ---
    required_columns = [
        "buyer_name", "identifier_legalname", "title", "description",
        "tender_procurementmethod", "tender_mainprocurementcategory",
        "total_value_kes", "contract_duration_days", "year", "status",
        "cluster", "anomaly_score", "is_anomaly"
    ]
    for col in required_columns:
        if col not in merged_df.columns:
            merged_df[col] = np.nan

    # --- Convert numpy types & handle NaN safely ---
    merged_df = merged_df.replace({np.nan: None})

    # --- Format numeric columns ---
    if "total_value_kes" in merged_df.columns:
        merged_df["total_value_kes"] = merged_df["total_value_kes"].apply(
            lambda x: f"{x:,.0f}" if isinstance(x, (int, float)) and not pd.isna(x) else ""
        )

    if "anomaly_score" in merged_df.columns:
        merged_df["anomaly_score"] = merged_df["anomaly_score"].apply(
            lambda x: round(x, 4) if isinstance(x, (int, float)) and not pd.isna(x) else ""
        )

    # --- Clean up boolean column ---
    if "is_anomaly" in merged_df.columns:
        merged_df["is_anomaly"] = merged_df["is_anomaly"].astype(bool)

    # --- Register callbacks ---
    register_benford_callbacks(app, merged_df)

    # --- Dropdown setup ---
    numeric_columns = [
        {"label": col.replace("_", " ").title(), "value": col}
        for col in merged_df.select_dtypes(include=[np.number]).columns
    ]

    buyers = sorted(merged_df["buyer_name"].dropna().unique()) if "buyer_name" in merged_df.columns else []
    years = sorted(merged_df["year"].dropna().unique()) if "year" in merged_df.columns else []

    # --- Table columns mapping ---
    table_columns = [
        {"name": "Buyer Name", "id": "buyer_name"},
        {"name": "Supplier (Legal Name)", "id": "identifier_legalname"},
        {"name": "Title", "id": "title"},
        {"name": "Description", "id": "description"},
        {"name": "Procurement Method", "id": "tender_procurementmethod"},
        {"name": "Procurement Category", "id": "tender_mainprocurementcategory"},
        {"name": "Total Value (KES)", "id": "total_value_kes"},
        {"name": "Contract Duration (Days)", "id": "contract_duration_days"},
        {"name": "Year", "id": "year"},
        {"name": "Status", "id": "status"},
        {"name": "Cluster", "id": "cluster"},
        {"name": "Anomaly Score", "id": "anomaly_score"},
        {"name": "Is Anomaly", "id": "is_anomaly"},
    ]

    print(f"🧩 [Benford] Final table columns: {[c['id'] for c in table_columns]}")

    # --- Ensure DataTable-friendly data ---
    data_records = merged_df.to_dict(orient="records")

    print(f"✅ [Benford] Loaded {len(data_records)} records into DataTable")

    # --- Page layout ---
    return html.Div([
        dcc.Location(id="benford-url"),

        html.H2("📊 Benford’s Law Analysis", style={"textAlign": "center"}),

        # --- Filter controls ---
        html.Div([
            html.Div([
                html.Label("Buyer:"),
                dcc.Dropdown(
                    id="buyer-filter",
                    options=[{"label": b, "value": b} for b in buyers],
                    placeholder="Select buyer (optional)",
                    style={"width": "100%"},
                ),
            ], style={"flex": "1", "marginRight": "10px"}),

            html.Div([
                html.Label("Year:"),
                dcc.Dropdown(
                    id="year-filter",
                    options=[{"label": str(y), "value": y} for y in years],
                    placeholder="Select year (optional)",
                    style={"width": "100%"},
                ),
            ], style={"flex": "1", "marginRight": "10px"}),

            html.Div([
                html.Label("Numeric Column:"),
                dcc.Dropdown(
                    id="benford-column",
                    options=numeric_columns,
                    placeholder="Choose a numeric column...",
                    value="total_value_kes" if "total_value_kes" in merged_df.columns else None,
                    style={"width": "100%"},
                ),
            ], style={"flex": "1"}),
        ], style={
            "display": "flex",
            "justifyContent": "center",
            "width": "80%",
            "margin": "20px auto",
            "gap": "10px"
        }),

        # --- Output Section ---
        dcc.Loading(
            type="circle",
            children=[
                html.Pre(
                    id="benford-report",
                    style={
                        "whiteSpace": "pre-wrap",
                        "marginTop": "15px",
                        "backgroundColor": "#f8f9fa",
                        "padding": "10px",
                        "borderRadius": "8px",
                    },
                ),
                html.Img(
                    id="benford-img",
                    style={
                        "maxWidth": "100%",
                        "marginTop": "15px",
                        "borderRadius": "8px",
                    },
                ),
                dash_table.DataTable(
                    id="benford-table",
                    columns=[
                        {"name": "Total Value (KES)", "id": "total_value_kes"},
                        {"name": "Main Procurement Category", "id": "tender_mainprocurementcategory"},
                        {"name": "Procurement Method", "id": "tender_procurementmethod"},
                        {"name": "Contract Duration (Days)", "id": "contract_duration_days"},
                        {"name": "Year", "id": "year"},
                        {"name": "Status", "id": "status"},
                        {"name": "Description", "id": "description"},
                        {"name": "Title", "id": "title"},
                        {"name": "Buyer Name", "id": "buyer_name"},
                        {"name": "Supplier (Legal Name)", "id": "identifier_legalname"},
                        {"name": "Combined Text", "id": "combined_text"},
                        {"name": "Cluster", "id": "cluster"},
                        {"name": "Anomaly Score", "id": "anomaly_score"},
                        {"name": "Is Anomaly", "id": "is_anomaly"},
                    ],
                    data=merged_df.to_dict("records"),
                    page_size=10,
                    style_table={"overflowX": "auto", "marginTop": "15px"},
                    style_header={"backgroundColor": "#e9ecef", "fontWeight": "bold"},
                    style_cell={
                        "textAlign": "left",
                        "padding": "6px",
                        "whiteSpace": "normal",
                        "fontSize": "14px",
                    },
                    style_data_conditional=[
                        {
                            "if": {"filter_query": "{is_anomaly} eq True"},
                            "backgroundColor": "#ffe6e6",
                            "color": "#c00",
                            "fontWeight": "bold",
                        },
                        {"if": {"row_index": "odd"}, "backgroundColor": "#f9f9f9"},
                    ],
                    filter_action="native",
                    sort_action="native",
                ),
            ],
        ),
    ])
