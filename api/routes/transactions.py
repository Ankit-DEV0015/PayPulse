
import csv
import logging
from pathlib import Path
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import ValidationError

from api.schemas import TransactionCreate, TransactionResponse

router = APIRouter(
    prefix="/api/v1/transactions",
    tags=["transactions"]
)

logger = logging.getLogger(__name__)

# Project root: PayPulse/
BASE_DIR = Path(__file__).resolve().parents[2]

# Dataset location
CSV_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "transactions_cleaned.csv"
)

# Temporary in-memory storage
_fake_db: List[TransactionResponse] = []


def load_transactions():
    """Load demonstration transactions from the CSV."""

    if not CSV_PATH.is_file():
        logger.warning(
            "Transaction dataset not found: %s",
            CSV_PATH
        )
        return

    loaded = []

    try:
        with CSV_PATH.open(
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            reader = csv.DictReader(file)

            for row_number, row in enumerate(
                reader,
                start=1
            ):
                try:
                    # CSV column names must match
                    # TransactionResponse fields.
                    data = {
                        key: value
                        for key, value in row.items()
                        if key is not None
                        and value not in (None, "")
                    }

                    data.setdefault(
                        "id",
                        row_number
                    )

                    transaction = (
                        TransactionResponse(**data)
                    )

                    loaded.append(transaction)

                except (ValidationError, ValueError) as exc:
                    logger.warning(
                        "Skipping CSV row %s: %s",
                        row_number,
                        exc
                    )

    except (OSError, csv.Error):
        logger.exception(
            "Unable to read transaction dataset"
        )
        return

    _fake_db.clear()
    _fake_db.extend(loaded)

    logger.info(
        "Loaded %s transactions",
        len(_fake_db)
    )


# Load dataset when this module is imported
load_transactions()


@router.get(
    "",
    response_model=List[TransactionResponse]
)
async def list_transactions(
    skip: int = 0,
    limit: int = 100
):
    if skip < 0 or limit < 1:
        raise HTTPException(
            status_code=400,
            detail="Invalid pagination parameters"
        )

    return _fake_db[skip:skip + limit]


@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse
)
async def get_transaction(transaction_id: str):

    for tx in _fake_db:
        if tx.transaction_id == transaction_id:
            return tx

    raise HTTPException(
        status_code=404,
        detail="Transaction not found"
    )


@router.post(
    "",
    response_model=TransactionResponse
)
async def create_transaction(
    tx: TransactionCreate
):
    # IDs are unique within the current process.
    new_id = max(
        (item.id for item in _fake_db),
        default=0
    ) + 1

    # Support Pydantic v1 and v2
    if hasattr(tx, "model_dump"):
        data = tx.model_dump()
    else:
        data = tx.dict()

    response = TransactionResponse(
        **data,
        id=new_id
    )

    _fake_db.append(response)

    return response
