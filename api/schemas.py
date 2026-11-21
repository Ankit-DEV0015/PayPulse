from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class TransactionCreate(BaseModel):
    transaction_id: str = Field(..., description="Unique transaction identifier")
    customer_id: str = Field(..., description="Synthetic customer identifier")
    transaction_amount: float = Field(..., gt=0)
    currency: str = Field(..., max_length=3)
    payment_method: str
    bank_name: str
    gateway_name: str
    transaction_timestamp: datetime
    failure_reason: str
    failure_code: str
    transaction_hour: int
    day_of_week: str
    attempt_number: int
    previous_failure_count: int
    time_since_last_attempt: int
    retry_delay_minutes: int
    customer_payment_history: int
    recovered: int = Field(..., ge=0, le=1)

class TransactionResponse(TransactionCreate):
    id: int  # internal DB ID placeholder

class PredictionRequest(BaseModel):
    transaction_id: str
    # In a real system you could either send the full feature payload or just ID.

class PredictionResponse(BaseModel):
    transaction_id: str
    recovery_probability: float = Field(..., ge=0, le=1)
    model_version: str = "v1"

class RetryRecommendationRequest(BaseModel):
    transaction_id: str

class RetryRecommendationResponse(BaseModel):
    transaction_id: str
    recommended_action: str
    expected_recovery_value: float
    expected_net_benefit: float
    explanation: Optional[str] = None
