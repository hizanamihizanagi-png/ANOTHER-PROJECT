"""
ScorAI — Virtual Ledger Service.
Agent 02 : Le cœur financier de ScorAI.

Ce service gère le Grand Livre Virtuel qui permet de créditer
instantanément le solde virtuel (UX/dopamine) sans déclencher
de prélèvement Mobile Money réel à chaque événement sportif.

Workflow:
1. Trigger sportif → credit_virtual() → solde virtuel +X FCFA (instantané)
2. Montant mis en file d'attente (status: PENDING)
3. Quand seuil atteint → batch settlement via MoMo (voir batch_engine.py)
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import asdict
import uuid

from backend.core.database import db
from backend.core.config import settings
from backend.models.schemas import (
    Wallet,
    VirtualTransaction,
    TransactionStatus,
)


class VirtualLedger:
    """
    Grand Livre Virtuel — Le moteur de dopamine financière.

    Principe clé: séparer la gratification (instantanée, visuelle)
    du prélèvement réel (batché, optimisé pour les frais MoMo).
    """

    async def get_or_create_wallet(self, user_id: str) -> Dict[str, Any]:
        """Récupérer ou créer le wallet d'un utilisateur."""
        wallet = await db.select_one("wallets", {"user_id": user_id})
        if not wallet:
            new_wallet = Wallet(user_id=user_id)
            wallet = await db.insert("wallets", asdict(new_wallet))
        return wallet

    async def credit_virtual(
        self,
        user_id: str,
        amount_fcfa: int,
        trigger_id: Optional[str] = None,
        trigger_event: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Créditer le solde VIRTUEL d'un utilisateur.

        C'est la méthode appelée quand un trigger sportif se déclenche.
        - Le solde virtuel augmente INSTANTANÉMENT (pour l'UX)
        - La transaction est mise en file d'attente (PENDING)
        - Aucun argent réel ne bouge à ce stade

        Returns:
            Dict avec le nouveau solde virtuel et la transaction créée.
        """
        # 1. Récupérer/créer le wallet
        wallet = await self.get_or_create_wallet(user_id)

        # 2. Créer la transaction virtuelle (PENDING)
        transaction = VirtualTransaction(
            user_id=user_id,
            wallet_id=wallet["id"],
            amount_fcfa=amount_fcfa,
            trigger_id=trigger_id,
            trigger_event=trigger_event,
            status=TransactionStatus.PENDING,
        )
        tx_record = await db.insert("virtual_transactions", asdict(transaction))

        # 3. Mettre à jour le solde virtuel (UX instantané)
        new_virtual_balance = wallet.get("virtual_balance_fcfa", 0) + amount_fcfa
        new_total_saved = wallet.get("total_saved_fcfa", 0) + amount_fcfa

        await db.update(
            "wallets",
            {"id": wallet["id"]},
            {
                "virtual_balance_fcfa": new_virtual_balance,
                "total_saved_fcfa": new_total_saved,
                "last_trigger_date": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            },
        )

        # 4. Mettre à jour le streak
        await self._update_streak(wallet)

        return {
            "transaction_id": tx_record["id"],
            "amount_fcfa": amount_fcfa,
            "new_virtual_balance": new_virtual_balance,
            "trigger_event": trigger_event,
            "status": "PENDING",
            "message": f"+{amount_fcfa} FCFA ajoutés à ton coffre! 🎉",
        }

    async def get_balance(self, user_id: str) -> Dict[str, Any]:
        """
        Obtenir le solde complet d'un utilisateur.

        Returns:
            Dict avec solde virtuel, solde confirmé, pending, streak.
        """
        wallet = await self.get_or_create_wallet(user_id)

        # Calculer le montant en attente de settlement
        pending_txs = await db.select(
            "virtual_transactions",
            {"user_id": user_id, "status": "PENDING"},
        )
        pending_amount = sum(tx.get("amount_fcfa", 0) for tx in pending_txs)

        return {
            "virtual_balance_fcfa": wallet.get("virtual_balance_fcfa", 0),
            "confirmed_balance_fcfa": wallet.get("confirmed_balance_fcfa", 0),
            "pending_settlement_fcfa": pending_amount,
            "total_saved_fcfa": wallet.get("total_saved_fcfa", 0),
            "current_streak_days": wallet.get("current_streak_days", 0),
            "longest_streak_days": wallet.get("longest_streak_days", 0),
        }

    async def get_pending_batch(self, user_id: str) -> Dict[str, Any]:
        """
        Vérifier si un utilisateur a atteint le seuil de batching.

        Returns:
            Dict avec le statut de batch et le montant pending.
        """
        pending_txs = await db.select(
            "virtual_transactions",
            {"user_id": user_id, "status": "PENDING"},
        )
        pending_amount = sum(tx.get("amount_fcfa", 0) for tx in pending_txs)
        ready_for_batch = pending_amount >= settings.BATCH_THRESHOLD_FCFA

        return {
            "pending_amount_fcfa": pending_amount,
            "threshold_fcfa": settings.BATCH_THRESHOLD_FCFA,
            "ready_for_batch": ready_for_batch,
            "pending_transactions_count": len(pending_txs),
        }

    async def get_transaction_history(
        self, user_id: str, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Historique des transactions virtuelles d'un utilisateur."""
        transactions = await db.select(
            "virtual_transactions",
            {"user_id": user_id},
            order_by="-created_at",
            limit=limit,
        )
        return transactions

    async def _update_streak(self, wallet: Dict[str, Any]) -> None:
        """Mettre à jour le streak d'épargne de l'utilisateur."""
        current_streak = wallet.get("current_streak_days", 0) + 1
        longest = max(current_streak, wallet.get("longest_streak_days", 0))

        await db.update(
            "wallets",
            {"id": wallet["id"]},
            {
                "current_streak_days": current_streak,
                "longest_streak_days": longest,
            },
        )


# Singleton
virtual_ledger = VirtualLedger()
