import os
import sys
import joblib
import pandas as pd
import shap
import matplotlib.pyplot as plt

# Ensure project root on PYTHONPATH for imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# Paths to artefacts
MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "logistic_regression.joblib")
PREPROC_PATH = os.path.join(PROJECT_ROOT, "models", "preprocessor.joblib")
CLEANED_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "transactions_cleaned.csv")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "artifacts", "shap")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_model_and_data(sample_frac: float = 0.1):
    """Load the trained model, preprocessor, and a random sample of cleaned data.
    Args:
        sample_frac: fraction of rows to sample for SHAP (default 10%).
    Returns:
        model, preprocessor, X_raw (DataFrame of raw features), y (Series).
    """
    if not os.path.exists(MODEL_PATH) or not os.path.exists(PREPROC_PATH):
        raise FileNotFoundError("Trained model or preprocessor not found. Run train_model.py first.")
    model = joblib.load(MODEL_PATH)
    preproc = joblib.load(PREPROC_PATH)
    df = pd.read_csv(CLEANED_DATA_PATH)
    # Drop identifier columns – same as training
    X_raw = df.drop(columns=["recovered", "transaction_id", "customer_id", "transaction_timestamp"]).copy()
    y = df["recovered"]
    # Sample for speed
    X_raw = X_raw.sample(frac=sample_frac, random_state=42).reset_index(drop=True)
    y = y.loc[X_raw.index]
    return model, preproc, X_raw, y

def compute_shap_values(sample_frac: float = 0.1):
    model, preproc, X_raw, y = load_model_and_data(sample_frac)
    # Transform raw features
    X = preproc.transform(X_raw)
    # Use TreeExplainer for tree‑based models, KernelExplainer otherwise.
    if hasattr(model, "predict_proba") and "tree" in model.__class__.__name__.lower():
        explainer = shap.TreeExplainer(model)
    else:
        # For logistic regression we can safely use LinearExplainer
        if "LogisticRegression" in model.__class__.__name__:
            explainer = shap.LinearExplainer(model, X, feature_perturbation="interventional")
        else:
            explainer = shap.KernelExplainer(model.predict_proba, X)
    shap_values = explainer.shap_values(X)
    # shap_values for binary classification returns list of two arrays – take the positive class
    if isinstance(shap_values, list) and len(shap_values) == 2:
        shap_values = shap_values[1]
    return X_raw, shap_values, explainer

def plot_global_importance(X_raw, shap_values, top_n: int = 20):
    plt.figure(figsize=(10, 6))
    shap.summary_plot(shap_values, X_raw, plot_type="bar", max_display=top_n, show=False)
    out_path = os.path.join(OUTPUT_DIR, "global_feature_importance.png")
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()
    return out_path

def plot_beeswarm(X_raw, shap_values, max_display: int = 100):
    plt.figure(figsize=(12, 8))
    shap.summary_plot(shap_values, X_raw, max_display=max_display, show=False)
    out_path = os.path.join(OUTPUT_DIR, "shap_beeswarm.png")
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()
    return out_path

def explain_single_instance(idx: int = 0):
    X_raw, shap_values, explainer = compute_shap_values()
    plt.figure(figsize=(8, 6))
    shap.force_plot(explainer.expected_value, shap_values[idx], X_raw.iloc[idx], matplotlib=True, show=False)
    out_path = os.path.join(OUTPUT_DIR, f"force_plot_{idx}.png")
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()
    return out_path

def main(sample_frac: float = 0.1):
    X_raw, shap_vals, _ = compute_shap_values(sample_frac)
    global_path = plot_global_importance(X_raw, shap_vals)
    beeswarm_path = plot_beeswarm(X_raw, shap_vals)
    single_path = explain_single_instance(0)
    print("SHAP artefacts saved to:")
    print(f"  Global importance: {global_path}")
    print(f"  Beeswarm plot   : {beeswarm_path}")
    print(f"  Example force   : {single_path}")

if __name__ == "__main__":
    main()
