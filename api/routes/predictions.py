import os
import sys
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

# Ensure the project root is on the PYTHONPATH so we can import src modules
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from src.train_model import load_cleaned_data
import joblib
import pandas as pd

router = APIRouter(prefix="/api/v1/predictions", tags=["predictions"])

class PredictionRequest(BaseModel):
    transaction_id: str

class PredictionResponse(BaseModel):
    transaction_id: str
    recovery_probability: float
    model_version: str = "v1"
    explanation: Optional[str] = None

# Load model and preprocessor lazily (first request)
_model = None
_preprocessor = None

def _load_artifacts():
    global _model, _preprocessor
    if _model is None:
        model_path = os.path.join(PROJECT_ROOT, "models", "logistic_regression.joblib")
        preproc_path = os.path.join(PROJECT_ROOT, "models", "preprocessor.joblib")
        if not os.path.exists(model_path) or not os.path.exists(preproc_path):
            raise FileNotFoundError("Trained model or preprocessor not found. Run train_model.py first.")
        _model = joblib.load(model_path)
        _preprocessor = joblib.load(preproc_path)

@router.post("", response_model=PredictionResponse)
async def get_prediction(req: PredictionRequest):
    _load_artifacts()
    # Load the cleaned dataset (small enough to keep in memory)
    df_clean = pd.read_csv(os.path.join(PROJECT_ROOT, "data", "processed", "transactions_cleaned.csv"))
    row = df_clean[df_clean["transaction_id"] == req.transaction_id]
    if row.empty:
        raise HTTPException(status_code=404, detail="Transaction not found")
    # Prepare raw features (same columns used during training)
    X_raw = row.drop(columns=["recovered", "transaction_id", "customer_id", "transaction_timestamp"]).copy()
    X_transformed = _preprocessor.transform(X_raw)
    prob = _model.predict_proba(X_transformed)[0, 1]
    return PredictionResponse(
        transaction_id=req.transaction_id,
        recovery_probability=round(float(prob), 4),
        explanation="Logistic regression probability output",
    )
