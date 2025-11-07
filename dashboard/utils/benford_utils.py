import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import chisquare
from io import BytesIO
import base64

def benford_expected_probs():
    """Return expected probabilities for Benford's Law (digits 1–9)."""
    return np.log10(1 + 1 / np.arange(1, 10))

def extract_leading_digits(series: pd.Series) -> pd.Series:
    """Extract the first non-zero leading digit from numeric strings."""
    cleaned = (
        series.dropna()
        .astype(str)
        .str.replace(r"[^\d]", "", regex=True)  # remove non-digits
        .str.lstrip("0")  # remove leading zeros
        .str[0]  # take first non-zero digit
        .dropna()
    )
    cleaned = cleaned[cleaned.str.isdigit()].astype(int)
    return cleaned

def run_benford_for_column(df: pd.DataFrame, col: str):
    """
    Run Benford’s Law test on a numeric column.
    Returns:
      - report (str)
      - base64 graph (str)
      - sample dataframe (pd.DataFrame)
    """
    # Ensure column exists and numeric
    if col not in df.columns:
        return f"Column '{col}' not found.", None, pd.DataFrame()

    series = pd.to_numeric(df[col], errors="coerce").dropna()
    leading = extract_leading_digits(series)

    if len(leading) < 30:
        return f"Too few samples in '{col}' (<30 valid entries)", None, pd.DataFrame()

    # Actual and expected distributions
    counts = leading.value_counts(normalize=True).sort_index()
    actual = counts.reindex(range(1, 10), fill_value=0).values
    expected = benford_expected_probs()

    # Chi-square goodness-of-fit test
    stat, p = chisquare(actual * len(leading), expected * len(leading))
    dev_pct = np.abs(actual - expected) / expected * 100
    suspicious_digits = [i + 1 for i, d in enumerate(dev_pct) if d > 15]

    # --- Visualization ---
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(np.arange(1, 10) - 0.2, expected, width=0.4, label="Expected (Benford)", alpha=0.7)
    ax.bar(np.arange(1, 10) + 0.2, actual, width=0.4, label="Actual", alpha=0.7)
    ax.set_xticks(np.arange(1, 10))
    ax.set_xlabel("Leading Digit")
    ax.set_ylabel("Proportion")
    ax.set_title(f"Benford's Law - {col}")
    ax.legend()

    # Encode image
    buf = BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    plt.close(fig)
    b64 = base64.b64encode(buf.getvalue()).decode()

    # Result summary
    report = (
        f"Column '{col}' — χ²={stat:.2f}, p={p:.4f}. "
        f"Suspicious digits (>|15% deviation|): {suspicious_digits or 'None'}"
    )

    return report, f"data:image/png;base64,{b64}", df[[col]].head(10)
