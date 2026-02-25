"""
ScorAI — E2E Integration Tests (Agent 12).
Verifies the complete flow: Signup -> Trigger -> Match Event -> Virtual Ledger -> Batch Settlement -> Score Mvmt -> Credit.
"""

import pytest
import asyncio
from datetime import datetime

from backend.core.database import db
from backend.services.virtual_ledger import virtual_ledger
from backend.services.batch_engine import batch_engine
from backend.services.sports_trigger import sports_trigger
from backend.ml.scorai_model import scorai_model
from backend.services.credit_decision import credit_engine
from backend.core.config import settings

@pytest.mark.asyncio
async def test_scorai_e2e_flow():
    # 1. Setup Data - Mock User
    user_id = "test-user-123"
    await db.insert("users", {"id": user_id, "phone_number": "690000000", "display_name": "Test User", "kyc_status": "VERIFIED"})
    await db.insert("wallets", {"id": "wallet-123", "user_id": user_id, "virtual_balance_fcfa": 0, "confirmed_balance_fcfa": 0})
    await db.insert("kyc_records", {"id": "kyc-123", "user_id": user_id, "status": "VERIFIED"})
    
    # 2. Setup Trigger
    trigger = await sports_trigger.create_trigger(user_id, 42, "Arsenal", "WIN", 2500)
    assert trigger["success"] is True

    # 3. Simulate Match Results (Arsenal Wins twice to hit threshold)
    await sports_trigger._fire_triggers([{"team_id": 42, "type": "WIN"}])
    await sports_trigger._fire_triggers([{"team_id": 42, "type": "WIN"}])

    # 4. Check Virtual Balance
    balance = await virtual_ledger.get_balance(user_id)
    assert balance["virtual_balance_fcfa"] == 5000
    assert balance["pending_settlement_fcfa"] == 5000
    assert balance["confirmed_balance_fcfa"] == 0

    # 5. Execute Batch Settlement (Threshold is 5000)
    batch_results = await batch_engine.check_and_execute_batches()
    assert len(batch_results) == 1
    assert batch_results[0]["status"] == "SETTLED"

    # 6. Check Confirmed Balance
    balance_after = await virtual_ledger.get_balance(user_id)
    assert balance_after["virtual_balance_fcfa"] == 5000
    assert balance_after["pending_settlement_fcfa"] == 0
    assert balance_after["confirmed_balance_fcfa"] == 5000

    # 7. Mock minimum observation days for scoring
    # We update the wallet to look old enough
    wallet = await db.select_one("wallets", {"user_id": user_id})
    old_date = datetime.utcnow() - asyncio.timedelta(days=95)
    await db.update("wallets", {"id": wallet["id"]}, {"created_at": old_date.isoformat(), "current_streak_days": 10})

    # 8. Check Score
    score = await scorai_model.predict(user_id)
    assert score["trust_score"] > 0
    
    # Force a solid score for testing credit
    await db.update("credit_scores", {"user_id": user_id}, {"trust_score": 650, "max_loan_fcfa": 25000, "tier": "EXPERT"})

    # 9. Apply for Loan (10k)
    loan_result = await credit_engine.evaluate_loan_request(user_id, 10000)
    assert loan_result["decision"] == "APPROVED"
    assert loan_result["disbursement"]["success"] is True

    # 10. Repay Loan
    repay_result = await credit_engine.process_repayment(loan_result["loan_id"], 10500) # 10k + 5% interest
    assert repay_result["status"] == "REPAID"

    print("✅ E2E Flow tests passed successfully.")
