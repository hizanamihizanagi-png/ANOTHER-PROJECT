"""ScorAI — Wallet API Routes (Virtual Ledger)."""

from fastapi import APIRouter, HTTPException
from typing import Optional
from pydantic import BaseModel

from backend.services.virtual_ledger import virtual_ledger
from backend.services.batch_engine import batch_engine


wallet_router = APIRouter()


class ManualCreditRequest(BaseModel):
    user_id: str
    amount_fcfa: int
    description: str = "Dépôt manuel"


# ============================================================
# Endpoints
# ============================================================

@wallet_router.get("/wallet/balance/{user_id}")
async def get_balance(user_id: str):
    """Obtenir le solde complet (virtuel + confirmé + pending)."""
    return await virtual_ledger.get_balance(user_id)


@wallet_router.get("/wallet/history/{user_id}")
async def get_history(user_id: str, limit: int = 50):
    """Historique des transactions virtuelles."""
    return await virtual_ledger.get_transaction_history(user_id, limit)


@wallet_router.get("/wallet/batch-status/{user_id}")
async def get_batch_status(user_id: str):
    """Statut du batch en cours (seuil atteint?)."""
    return await virtual_ledger.get_pending_batch(user_id)


@wallet_router.post("/wallet/manual-credit")
async def manual_credit(req: ManualCreditRequest):
    """Crédit virtuel manuel (pour tests/démo)."""
    return await virtual_ledger.credit_virtual(
        user_id=req.user_id,
        amount_fcfa=req.amount_fcfa,
        trigger_event=req.description,
    )


@wallet_router.post("/wallet/execute-batch/{user_id}")
async def execute_batch(user_id: str):
    """Forcer l'exécution du batch pour un utilisateur."""
    result = await batch_engine.force_batch_user(user_id)
    if not result:
        raise HTTPException(status_code=404, detail="Aucune transaction en attente")
    return result


@wallet_router.post("/wallet/execute-all-batches")
async def execute_all_batches():
    """Exécuter tous les batchs éligibles (scheduler)."""
    return await batch_engine.check_and_execute_batches()


@wallet_router.get("/wallet/batch-stats")
async def get_batch_stats():
    """Statistiques globales de batching (admin)."""
    return await batch_engine.get_batch_stats()
