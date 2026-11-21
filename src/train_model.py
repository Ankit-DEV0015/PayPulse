import joblib
import json
from pathlib import Path
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
)
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
try:
    from xgboost import XGBClassifier
except ImportError:
    XGBClassifier = None  # XGBoost not available; will be skipped

# Paths (relative to repository root)
CLEANED_PATH = Path(__file__).resolve().parents[1] / "data" / "processed" / "transactions_cleaned.csv"
MODEL_DIR = Path(__file__).resolve().parents[1] / "models"
METRICS_PATH = MODEL_DIR / "model_metrics.json"

def load_cleaned_data():
    """Load the cleaned CSV and separate features / target.
    Returns:
        X_raw: DataFrame of raw features (before encoding/scaling)
        y: Series of target labels
    """
    df = pd.read_csv(CLEANED_PATH)
    y = df["recovered"]
    # Drop columns that are identifiers or timestamps (not used for modeling)
    X_raw = df.drop(columns=["recovered", "transaction_id", "customer_id", "transaction_timestamp"]).copy()
    return X_raw, y

def evaluate_model(model, X_test, y_test):
    probs = model.predict_proba(X_test)[:, 1]
    preds = (probs >= 0.5).astype(int)
    metrics = {
        "accuracy": accuracy_score(y_test, preds),
        "precision": precision_score(y_test, preds, zero_division=0),
        "recall": recall_score(y_test, preds),
        "f1": f1_score(y_test, preds),
        "roc_auc": roc_auc_score(y_test, probs),
        "pr_auc": average_precision_score(y_test, probs),
        "brier": brier_score_loss(y_test, probs),
        "confusion_matrix": confusion_matrix(y_test, preds).tolist(),
    }
    return metrics

def main():
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    X_raw, y = load_cleaned_data()

    # Build and fit the preprocessor on the training portion of raw data
    from feature_engineering import build_preprocessor
    preproc = build_preprocessor()

    # Chronological split (70% train, 15% val, 15% test)
    n = len(X_raw)
    train_end = int(0.7 * n)
    val_end = int(0.85 * n)
    X_train_raw, y_train = X_raw.iloc[:train_end], y.iloc[:train_end]
    X_val_raw, y_val = X_raw.iloc[train_end:val_end], y.iloc[train_end:val_end]
    X_test_raw, y_test = X_raw.iloc[val_end:], y.iloc[val_end:]

    # Fit preprocessor on training raw data and transform all splits
    X_train = preproc.fit_transform(X_train_raw)
    X_val = preproc.transform(X_val_raw)
    X_test = preproc.transform(X_test_raw)

    # Save the fitted preprocessor for later inference
    joblib.dump(preproc, MODEL_DIR / "preprocessor.joblib")

    models = {
        "logistic_regression": LogisticRegression(max_iter=500),
        "random_forest": RandomForestClassifier(n_estimators=200, random_state=42),
    }
    if XGBClassifier is not None:
        models["xgboost"] = XGBClassifier(
            n_estimators=300,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            eval_metric="logloss",
            use_label_encoder=False,
            n_jobs=-1,
            random_state=42,
        )

    best_score = -1.0
    best_name = None
    all_metrics = {}

    for name, model in models.items():
        print(f"Training {name} …")
        model.fit(X_train, y_train)
        val_metrics = evaluate_model(model, X_val, y_val)
        all_metrics[name] = val_metrics
        if val_metrics["roc_auc"] > best_score:
            best_score = val_metrics["roc_auc"]
            best_name = name
        # Save the model
        joblib.dump(model, MODEL_DIR / f"{name}.joblib")

    # Evaluate the selected best model on the test set
    best_model = joblib.load(MODEL_DIR / f"{best_name}.joblib")
    test_metrics = evaluate_model(best_model, X_test, y_test)
    all_metrics["best_model"] = {"name": best_name, "test_metrics": test_metrics}

    # Persist metrics to JSON
    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(all_metrics, f, indent=2)

    print(f"Best model: {best_name} (validation ROC‑AUC={best_score:.4f})")
    print("Test metrics:")
    for k, v in test_metrics.items():
        print(f"  {k}: {v}")

if __name__ == "__main__":
    main()
