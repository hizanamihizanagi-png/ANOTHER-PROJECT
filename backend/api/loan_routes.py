"""ScorAI — Loan / Credit API Routes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.credit_decision import credit_engine


loan_router = APIRouter()


class LoanRequest(BaseModel):
    user_id: str
    amount_fcfa: int


class RepaymentRequest(BaseModel):
    loan_id: str
    amount_fcfa: int


@loan_router.post("/loans/apply")
async def apply_for_loan(req: LoanRequest):
    """Demander un micro-prêt instantané."""
    return await credit_engine.evaluate_loan_request(req.user_id, req.amount_fcfa)


@loan_router.get("/loans/status/{loan_id}")
async def get_loan_status(loan_id: str):
    """Statut d'un prêt spécifique."""
    result = await credit_engine.get_loan_status(loan_id)
    if not result:
        raise HTTPException(status_code=404, detail="Prêt introuvable")
    return result


@loan_router.get("/loans/user/{user_id}")
async def get_user_loans(user_id: str):
    """Historique des prêts d'un utilisateur."""
    return await credit_engine.get_user_loans(user_id)


@loan_router.post("/loans/repay")
async def repay_loan(req: RepaymentRequest):
    """Rembourser un prêt."""
    return await credit_engine.process_repayment(req.loan_id, req.amount_fcfa)


@loan_router.post("/loans/check-overdue")
async def check_overdue():
    """Vérifier les prêts en retard (scheduler)."""
    return await credit_engine.check_overdue_loans()


@loan_router.get("/loans/stats")
async def get_loan_stats():
    """Statistiques de crédit globales (admin)."""
    return await credit_engine.get_loan_stats()
