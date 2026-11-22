
from io import BytesIO
from pathlib import Path

import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile

router = APIRouter(prefix="/uploads", tags=["Uploads"])

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}


@router.post("/preview")
async def preview_uploaded_file(file: UploadFile = File(...)):
    filename = Path(file.filename or "").name
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only CSV, XLSX and XLS files are supported.",
        )

    try:
        content = await file.read(MAX_FILE_SIZE + 1)
    finally:
        await file.close()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File exceeds the 10 MB limit.",
        )

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    try:
        if extension == ".csv":
            df = pd.read_csv(BytesIO(content))
        elif extension == ".xlsx":
            df = pd.read_excel(BytesIO(content), engine="openpyxl")
        else:
            df = pd.read_excel(BytesIO(content), engine="xlrd")

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Could not read this file. Check its format and contents.",
        )

    if df.empty:
        raise HTTPException(
            status_code=400,
            detail="The file contains no transaction rows.",
        )

    if len(df.columns) > 200:
        raise HTTPException(
            status_code=400,
            detail="Too many columns. Maximum is 200.",
        )

    # Convert missing values into JSON-safe null values
    preview_df = df.head(5).astype(object)
    preview_df = preview_df.where(pd.notna(preview_df), None)

    return {
        "filename": filename,
        "file_type": extension.lstrip("."),
        "row_count": len(df),
        "columns": [str(col) for col in df.columns],
        "preview": preview_df.to_json(
            orient="records",
            date_format="iso",
        ),
        "message": "File successfully read by PayPulse.",
    }
