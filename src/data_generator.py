# Synthetic Transaction Data Generator
"""Generate a realistic synthetic dataset for PayPulse development.
The generator creates a CSV file with a configurable number of records.
It uses only the Python standard library to avoid external dependencies.
"""

import csv
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
NUM_RECORDS = 20000
OUTPUT_PATH = Path(__file__).resolve().parents[1] / "data" / "raw" / "synthetic_transactions.csv"

# Helper functions to simulate realistic patterns
def random_currency():
    return random.choice(["USD", "EUR", "INR", "GBP", "JPY"])

def random_payment_method():
    return random.choice(["UPI", "Card", "Net Banking"])

def random_bank():
    return random.choice(["Bank of America", "HSBC", "ICICI", "SBI", "Citi"])

def random_gateway():
    return random.choice(["Stripe", "PayPal", "Razorpay", "Square"])

def random_failure_reason():
    return random.choice([
        "Network Timeout",
        "Invalid Card",
        "Insufficient Funds",
        "Expired Card",
        "Gateway Unavailable",
        "Bank Maintenance",
        "Incorrect Details",
    ])

def failure_code_from_reason(reason):
    mapping = {
        "Network Timeout": "NT01",
        "Invalid Card": "IC02",
        "Insufficient Funds": "IF03",
        "Expired Card": "EC04",
        "Gateway Unavailable": "GU05",
        "Bank Maintenance": "BM06",
        "Incorrect Details": "ID07",
    }
    return mapping.get(reason, "UNKN")

def recovery_probability(reason, attempt_number, amount):
    """Base probability depends on failure reason and decreases with attempts.
    Larger amounts are weighted slightly lower to reflect business caution.
    """
    base = {
        "Network Timeout": 0.70,
        "Gateway Unavailable": 0.65,
        "Bank Maintenance": 0.60,
        "Insufficient Funds": 0.30,
        "Invalid Card": 0.05,
        "Expired Card": 0.05,
        "Incorrect Details": 0.10,
    }.get(reason, 0.20)
    prob = base * (0.8 ** (attempt_number - 1))
    prob *= max(0.5, 1 - (amount / 10000) * 0.1)
    return min(max(prob, 0.01), 0.99)

def random_timestamp():
    """Return a random datetime within the last 180 days."""
    start = datetime.now() - timedelta(days=180)
    random_seconds = random.randint(0, 180 * 24 * 60 * 60)
    return start + timedelta(seconds=random_seconds)

def generate_record():
    transaction_timestamp = random_timestamp()
    transaction_amount = round(random.uniform(10, 5000), 2)
    payment_method = random_payment_method()
    failure_reason = random_failure_reason()
    attempt_number = random.randint(1, 4)
    prob = recovery_probability(failure_reason, attempt_number, transaction_amount)
    recovered = 1 if random.random() < prob else 0
    return {
        "transaction_id": str(uuid.uuid4()),
        "customer_id": str(uuid.uuid4()),
        "transaction_amount": transaction_amount,
        "currency": random_currency(),
        "payment_method": payment_method,
        "bank_name": random_bank(),
        "gateway_name": random_gateway(),
        "transaction_timestamp": transaction_timestamp.isoformat(),
        "failure_reason": failure_reason,
        "failure_code": failure_code_from_reason(failure_reason),
        "transaction_hour": transaction_timestamp.hour,
        "day_of_week": transaction_timestamp.strftime("%A"),
        "attempt_number": attempt_number,
        "previous_failure_count": max(0, attempt_number - 1),
        "time_since_last_attempt": random.randint(1, 1440),
        "retry_delay_minutes": random.choice([0, 30, 120, 1440]),
        "customer_payment_history": random.randint(0, 20),
        "recovered": recovered,
    }

def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "transaction_id",
        "customer_id",
        "transaction_amount",
        "currency",
        "payment_method",
        "bank_name",
        "gateway_name",
        "transaction_timestamp",
        "failure_reason",
        "failure_code",
        "transaction_hour",
        "day_of_week",
        "attempt_number",
        "previous_failure_count",
        "time_since_last_attempt",
        "retry_delay_minutes",
        "customer_payment_history",
        "recovered",
    ]
    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for _ in range(NUM_RECORDS):
            writer.writerow(generate_record())
    print(f"Synthetic dataset written to {OUTPUT_PATH} ({NUM_RECORDS} rows)")

if __name__ == "__main__":
    main()
