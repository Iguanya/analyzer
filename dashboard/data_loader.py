import pandas as pd
import os

def load_merged_data():
    """
    Load merged PPRA dataset, or fallback to dummy data.
    """
    DATA_PATH = os.path.join(os.path.dirname(__file__), "merged_ppra_data.csv")

    try:
        df = pd.read_csv(DATA_PATH)
    except FileNotFoundError:
        print(f"[⚠] Dataset not found at {DATA_PATH}. Using placeholder data.")
        df = pd.DataFrame([{
            "buyer_name": "(no data)",
            "year": 0,
            "total_value_kes": 0.0,
            "is_anomaly": 0,
            "contract_duration_days": 0,
            "cluster": "N/A",
            "tender_procurementmethod": "N/A",
            "anomaly_score": 0.0,
            "identifier_legalname": "",
            "title": ""
        }])

    for col in ["total_value_kes", "contract_duration_days", "anomaly_score"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df
