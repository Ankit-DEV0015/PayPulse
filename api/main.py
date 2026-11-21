from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import transactions, predictions, retries

app = FastAPI(title="PayPulse API", version="0.1.0")

# CORS (allow all for dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(transactions.router)
app.include_router(predictions.router)
app.include_router(retries.router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
