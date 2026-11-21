import os
import sys
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Literal

# Ensure project root on PYTHONPATH
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

import joblib
import pandas as pd
from src.decision_engine import recommend_action

router = APIRouter(prefix="/api/v1/retries", tags=["retries"])

class RetryRequest(BaseModel):
    transaction_id: str

class RetryResponse(BaseModel):
    transaction_id: str
    recommended_action: Literal[
        "retry_immediately",
        "retry_30_min",
        "retry_2_hr",
        "retry_24_hr",
        "suggest_alternative",
        "stop_retry",
    ]
    expected_net_benefit: float
    explanation: str

# Lazy load model and preprocessor (same as prediction route)
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

@router.post("", response_model=RetryResponse)
async def get_retry_recommendation(req: RetryRequest):
    _load_artifacts()
    df = pd.read_csv(os.path.join(PROJECT_ROOT, "data", "processed", "transactions_cleaned.csv"))
    row = df[df["transaction_id"] == req.transaction_id]
    if row.empty:
        raise HTTPException(status_code=404, detail="Transaction not found")
    # Prepare features for prediction
    raw_features = row.drop(columns=["recovered", "transaction_id", "customer_id", "transaction_timestamp"]).copy()
    X = _preprocessor.transform(raw_features)
    prob = _model.predict_proba(X)[0, 1]
    # Decision engine determines best action
    action, net_benefit, explanation = recommend_action(row.iloc[0], float(prob))
    return RetryResponse(
        transaction_id=req.transaction_id,
        recommended_action=action,
        expected_net_benefit=round(net_benefit, 4),
        explanation=explanation,
    )
