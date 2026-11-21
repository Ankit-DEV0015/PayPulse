from fastapi import APIRouter, HTTPException
from typing import List
from api.schemas import TransactionCreate, TransactionResponse

router = APIRouter(prefix="/api/v1/transactions", tags=["transactions"])

# In‑memory store for demo purposes (will be replaced by DB later)
_fake_db: List[TransactionResponse] = []

@router.post("", response_model=TransactionResponse)
async def create_transaction(tx: TransactionCreate):
    # Simple auto‑increment ID
    new_id = len(_fake_db) + 1
    response = TransactionResponse(**tx.dict(), id=new_id)
    _fake_db.append(response)
    return response

@router.get("", response_model=List[TransactionResponse])
async def list_transactions(skip: int = 0, limit: int = 100):
    return _fake_db[skip : skip + limit]

@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: str):
    for tx in _fake_db:
        if tx.transaction_id == transaction_id:
            return tx
    raise HTTPException(status_code=404, detail="Transaction not found")
