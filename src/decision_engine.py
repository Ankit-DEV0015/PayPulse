from typing import Literal, Tuple
import pandas as pd

# Business constants (could be moved to config later)
RETRY_COST = 0.5  # flat cost per retry attempt (currency units)
MAX_RETRY_ATTEMPTS = 3

# Permanent failure reasons – never auto‑retry
PERMANENT_FAILURES = {
    "Invalid Card",
    "Expired Card",
    "Incorrect Details",
}

# Temporary failure reasons – eligible for retry
TEMPORARY_FAILURES = {
    "Network Timeout",
    "Gateway Unavailable",
    "Bank Maintenance",
    "Insufficient Funds",
}

# Candidate actions and assumed additional delay (minutes) – for illustration
ACTION_DELAY = {
    "retry_immediately": 0,
    "retry_30_min": 30,
    "retry_2_hr": 120,
    "retry_24_hr": 1440,
    "suggest_alternative": None,  # no delay, just suggestion
    "stop_retry": None,
}

def _action_expected_value(amount: float, prob: float, delay: int | None) -> float:
    """Calculate expected net benefit for a given action.
    - amount: transaction amount
    - prob: base recovery probability from the model
    - delay: additional wait time in minutes (None for non‑retry actions)
    For simplicity we assume probability does not change with delay, but the cost
    is incurred per retry attempt.
    """
    if delay is None:
        # No automatic retry – net benefit is 0 (business may handle manually)
        return 0.0
    expected_recovery = amount * prob
    net = expected_recovery - RETRY_COST
    return net

def recommend_action(
    transaction: pd.Series, recovery_prob: float
) -> Tuple[Literal[
    "retry_immediately",
    "retry_30_min",
    "retry_2_hr",
    "retry_24_hr",
    "suggest_alternative",
    "stop_retry",
], float, str]:
    """Return the best retry action, its expected net benefit, and a short explanation.
    Args:
        transaction: a row from the cleaned dataframe (including amount, failure_reason, attempt_number, etc.)
        recovery_prob: model‑predicted probability of eventual recovery.
    Returns:
        (action, expected_net_benefit, explanation)
    """
    reason = transaction["failure_reason"]
    amount = transaction["transaction_amount"]
    attempts = transaction["attempt_number"]

    # Permanent failures → stop retry
    if reason in PERMANENT_FAILURES:
        return "stop_retry", 0.0, f"Permanent failure ({reason}) – do not auto‑retry."

    # Exceeded max attempts → stop
    if attempts >= MAX_RETRY_ATTEMPTS:
        return "stop_retry", 0.0, f"Maximum retry attempts ({attempts}) reached."

    # Generate candidate actions (only retry actions for temporary failures)
    candidates = []
    for act, delay in ACTION_DELAY.items():
        if delay is None:
            # skip non‑retry actions for now – we could add "suggest_alternative" later
            continue
        net = _action_expected_value(amount, recovery_prob, delay)
        candidates.append((act, net))

    # Pick the action with highest net benefit (could be negative)
    best_action, best_net = max(candidates, key=lambda x: x[1])
    explanation = f"Chosen {best_action.replace('_', ' ')} (net benefit = {best_net:.2f})."
    return best_action, best_net, explanation
