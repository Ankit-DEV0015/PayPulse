from pathlib import Path
import pandas as pd
import numpy as np

# Paths – relative to this file (src)
RAW_DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "raw" / "synthetic_transactions.csv"
PROCESSED_DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "processed" / "transactions_cleaned.csv"

def load_raw_data() -> pd.DataFrame:
    """Load the raw synthetic CSV.
    Returns:
        DataFrame with original columns and proper dtypes.
    """
    df = pd.read_csv(RAW_DATA_PATH)
    return df

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Perform minimal cleaning:
    - Convert timestamps to ``datetime``.
    - Ensure numeric columns are proper dtypes.
    - Cast ``recovered`` to ``int``.
    - Fill any missing values with sensible defaults (rare in synthetic data).
    """
    # Timestamp conversion
    df["transaction_timestamp"] = pd.to_datetime(df["transaction_timestamp"], errors="coerce")
    # Numeric columns
    numeric_cols = [
        "transaction_amount",
        "transaction_hour",
        "attempt_number",
        "previous_failure_count",
        "time_since_last_attempt",
        "retry_delay_minutes",
        "customer_payment_history",
        "recovered",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    # Categorical columns – ensure string type
    cat_cols = ["currency", "payment_method", "bank_name", "gateway_name", "failure_reason", "failure_code", "day_of_week"]
    for col in cat_cols:
        df[col] = df[col].astype(str)
    # Fill missing (if any)
    df = df.fillna({
        "transaction_timestamp": pd.Timestamp.now(),
        "transaction_amount": df["transaction_amount"].median(),
        "recovered": 0,
    })
    return df

def save_cleaned(df: pd.DataFrame) -> Path:
    """Persist the cleaned DataFrame to the processed folder.
    Returns the path to the saved CSV.
    """
    PROCESSED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_DATA_PATH, index=False)
    return PROCESSED_DATA_PATH

def main():
    raw = load_raw_data()
    cleaned = clean_data(raw)
    out_path = save_cleaned(cleaned)
    print(f"Cleaned data written to {out_path} (rows={cleaned.shape[0]})")

if __name__ == "__main__":
    main()
