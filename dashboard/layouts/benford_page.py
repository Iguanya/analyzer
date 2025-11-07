from dash import html, dcc, dash_table
import numpy as np

def benford_page_layout(merged_df):
    return html.Div([
        dcc.Location(id="benford-url"),  # Detect when this page loads
        dcc.Store(id="benford-init", data={"run": True}),  # Trigger storage for initial run

        html.H2("📊 Benford’s Law Analysis", style={"textAlign": "center"}),

        html.Div([
            html.Label("Select numeric column:"),
            dcc.Dropdown(
                id="benford-column",
                placeholder="Choose a numeric column...",
                options=[
                    {"label": col, "value": col}
                    for col in merged_df.select_dtypes(include=[np.number]).columns
                ],
            ),
            html.Button(
                "Run Benford", id="run-benford", n_clicks=0,
                style={"marginTop": "10px"}
            )
        ], style={"width": "40%", "margin": "auto"}),

        html.Div(id="benford-output", style={"marginTop": "20px"}),

        dcc.Loading(
            children=[
                html.Pre(id="benford-report", style={"whiteSpace": "pre-wrap"}),
                html.Img(id="benford-img", style={"maxWidth": "100%", "marginTop": "10px"}),
                dash_table.DataTable(
                    id="benford-table",
                    columns=[
                        {"name": "Buyer", "id": "buyer_name"},
                        {"name": "Supplier", "id": "identifier_legalname"},
                        {"name": "Tender Title", "id": "title"},
                        {"name": "Contract Value (KES)", "id": "total_value_kes"},
                        {"name": "Year", "id": "year"},
                    ],
                    page_size=15,
                    style_table={"overflowX": "auto"},
                    style_cell={"textAlign": "left"},
                ),
            ],
            type="circle"
        ),
    ])
