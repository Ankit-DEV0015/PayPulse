
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import all API routers
from api.routes import (
    transactions,
    predictions,
    retries,
    auth,
    uploads,
)

# Initialize FastAPI
app = FastAPI(
    title="PayPulse API",
    description="AI-powered payment failure recovery platform",
    version="0.3.0",
)

# --------------------------------------------------
# CORS Configuration
# --------------------------------------------------

origins = [
    # Local React frontend
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",

    # Deployed Vercel frontend
    "https://pay-pulse-nu.vercel.app",
]

# Additional frontend origins from environment
extra_origins = os.getenv("FRONTEND_ORIGINS", "")

origins.extend(
    origin.strip()
    for origin in extra_origins.split(",")
    if origin.strip()
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ],
    allow_headers=[
        "Content-Type",
        "Authorization",
    ],
)

# --------------------------------------------------
# Register API Routes
# --------------------------------------------------

# Transaction API
app.include_router(transactions.router)

# ML prediction API
app.include_router(predictions.router)

# Retry recommendation API
app.include_router(retries.router)

# Signup, login, logout and sessions
app.include_router(auth.router)

# CSV / Excel upload API
app.include_router(
    uploads.router,
    prefix="/api/v1",
)

# --------------------------------------------------
# Root Endpoint
# --------------------------------------------------

@app.get("/")
async def root():
    return {
        "message": "Welcome to PayPulse API",
        "version": "0.3.0",
        "status": "running",
    }

# --------------------------------------------------
# Health Check
# --------------------------------------------------

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "PayPulse API",
    }
