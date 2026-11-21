from pathlib import Path
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline

# Paths (relative to this file)
PROCESSED_DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "processed" / "transactions_cleaned.csv"
FEATURES_OUTPUT_PATH = Path(__file__).resolve().parents[1] / "data" / "processed" / "features.parquet"

def load_cleaned_data() -> pd.DataFrame:
    """Load the cleaned CSV produced by `data_processing.py`."""
    df = pd.read_csv(PROCESSED_DATA_PATH)
    return df

def build_preprocessor() -> ColumnTransformer:
    """Create a ColumnTransformer that:
    - One‑hot encodes categorical columns.
    - Scales numeric columns with StandardScaler.
    Returns a transformer ready to be used inside an sklearn Pipeline.
    """
    categorical_cols = ["currency", "payment_method", "bank_name", "gateway_name", "failure_reason", "failure_code", "day_of_week"]
    numeric_cols = ["transaction_amount", "transaction_hour", "attempt_number", "previous_failure_count", "time_since_last_attempt", "retry_delay_minutes", "customer_payment_history"]

    categorical_transformer = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    numeric_transformer = StandardScaler()

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", categorical_transformer, categorical_cols),
            ("num", numeric_transformer, numeric_cols),
        ]
    )
    return preprocessor

def fit_transform_features(df: pd.DataFrame) -> pd.DataFrame:
    """Fit the preprocessing pipeline on the provided DataFrame (excluding the target) and return the transformed feature matrix as a DataFrame.
    The column names are generated from the one‑hot encoder categories.
    """
    X = df.drop(columns=["recovered", "transaction_id", "customer_id", "transaction_timestamp"])  # keep only features
    preprocessor = build_preprocessor()
    X_transformed = preprocessor.fit_transform(X)
    # Build column names for the transformed DataFrame
    cat_features = preprocessor.named_transformers_["cat"].get_feature_names_out()
    all_features = list(cat_features) + list(preprocessor.transformers_[1][2])
    features_df = pd.DataFrame(X_transformed, columns=all_features)
    return features_df

def save_features(df: pd.DataFrame) -> Path:
    """Persist the transformed features to disk (Parquet for efficient storage)."""
    FEATURE_OUTPUT = FEATURES_OUTPUT_PATH
    FEATURE_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(FEATURE_OUTPUT, index=False)
    return FEATURE_OUTPUT

def main():
    cleaned = load_cleaned_data()
    features = fit_transform_features(cleaned)
    out_path = save_features(features)
    print(f"Feature matrix saved to {out_path} (shape: {features.shape})")

if __name__ == "__main__":
    main()
