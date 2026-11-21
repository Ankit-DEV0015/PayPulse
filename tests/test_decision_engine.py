import pytest
import pandas as pd
from src.decision_engine import recommend_action, RETRY_COST, MAX_RETRY_ATTEMPTS

# Helper to build a minimal transaction Series
def make_tx(failure_reason, amount=1000.0, attempts=1):
    data = {
        "failure_reason": failure_reason,
        "transaction_amount": amount,
        "attempt_number": attempts,
    }
    return pd.Series(data)

def test_permanent_failure_stops():
    tx = make_tx("Invalid Card")
    action, net, expl = recommend_action(tx, recovery_prob=0.9)
    assert action == "stop_retry"
    assert net == 0.0
    assert "Permanent failure" in expl

def test_max_attempts_stops():
    tx = make_tx("Network Timeout", attempts=MAX_RETRY_ATTEMPTS)
    action, net, expl = recommend_action(tx, recovery_prob=0.8)
    assert action == "stop_retry"
    assert net == 0.0
    assert "Maximum retry attempts" in expl

def test_temporary_failure_selects_best_action():
    tx = make_tx("Network Timeout", amount=2000.0, attempts=1)
    action, net, expl = recommend_action(tx, recovery_prob=0.9)
    # The implementation picks the first max net benefit (retry_immediately)
    assert action == "retry_immediately"
    assert net == pytest.approx(2000.0 * 0.9 - RETRY_COST)
    assert "net benefit" in expl

def test_negative_net_benefit_still_returns_action():
    tx = make_tx("Network Timeout", amount=100.0, attempts=1)
    # Very low probability leading to negative net benefit
    action, net, expl = recommend_action(tx, recovery_prob=0.001)
    assert net < 0
    assert action in ["retry_immediately", "retry_30_min", "retry_2_hr", "retry_24_hr"]
    assert "net benefit" in expl
