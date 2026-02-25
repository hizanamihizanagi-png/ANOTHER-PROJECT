"""
ScorAI — Batch Settlement Engine.
Agent 02 : Consolidation et exécution des prélèvements MoMo.

Ce service agrège les transactions virtuelles PENDING et déclenche
un UNIQUE prélèvement Mobile Money lorsque le seuil est atteint,
diluant ainsi les frais MoMo (1%) sur un volume viable.

Workflow:
1. Vérifier les wallets avec solde pending >= seuil (5000 FCFA)
2. Créer un BatchSettlement groupant les transactions
3. Appeler MoMoGateway pour le prélèvement unique
4. Marquer les transactions comme SETTLED
5. Mettre à jour le confirmed_balance du wallet
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import asdict
import uuid

from backend.core.database import db
from backend.core.config import settings
from backend.models.schemas import (
    BatchSettlement,
    TransactionStatus,
)


class BatchEngine:
    """
    Moteur de consolidation des prélèvements.

    Résout le problème #1 des fintechs africaines: les frais MoMo
    qui détruisent le capital sur les micro-transactions.

    Stratégie: au lieu de 10 prélèvements de 500 FCFA (= 50 FCFA de frais x 10 = 500 FCFA perdus),
    on fait 1 prélèvement de 5000 FCFA (= 50 FCFA de frais x 1 = 50 FCFA perdus).
    Économie: 90% des frais.
    """

    async def check_and_execute_batches(self) -> List[Dict[str, Any]]:
        """
        Processus principal de batching (appelé par le scheduler).

        Scan tous les wallets, identifie ceux qui ont atteint le seuil,
        et crée/exécute les batch settlements.

        Returns:
            Liste des batches exécutés.
        """
        executed_batches = []

        # 1. Trouver tous les utilisateurs avec des transactions PENDING
        all_pending = await db.select(
            "virtual_transactions", {"status": "PENDING"}
        )

        # 2. Grouper par utilisateur
        user_pending: Dict[str, List[Dict]] = {}
        for tx in all_pending:
            uid = tx["user_id"]
            user_pending.setdefault(uid, []).append(tx)

        # 3. Pour chaque utilisateur, vérifier le seuil
        for user_id, transactions in user_pending.items():
            total_pending = sum(tx.get("amount_fcfa", 0) for tx in transactions)

            if total_pending >= settings.BATCH_THRESHOLD_FCFA:
                batch = await self._create_and_execute_batch(
                    user_id, transactions, total_pending
                )
                if batch:
                    executed_batches.append(batch)

        return executed_batches

    async def force_batch_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Forcer l'exécution du batch pour un utilisateur spécifique.
        Utilisé pour le batch du dimanche soir (fallback cron).
        """
        pending_txs = await db.select(
            "virtual_transactions",
            {"user_id": user_id, "status": "PENDING"},
        )

        if not pending_txs:
            return None

        total = sum(tx.get("amount_fcfa", 0) for tx in pending_txs)
        return await self._create_and_execute_batch(user_id, pending_txs, total)

    async def _create_and_execute_batch(
        self,
        user_id: str,
        transactions: List[Dict],
        total_amount: int,
    ) -> Dict[str, Any]:
        """
        Créer un batch et exécuter le prélèvement MoMo.

        Steps:
        1. Calculer les frais MoMo
        2. Créer le record BatchSettlement
        3. Appeler MoMoGateway (simulé pour le MVP)
        4. Marquer toutes les transactions comme SETTLED
        5. Mettre à jour le confirmed_balance du wallet
        """
        # 1. Calculer les frais
        momo_fee = int(total_amount * settings.MOMO_FEE_PERCENTAGE)
        net_amount = total_amount - momo_fee

        # 2. Créer le batch record
        batch = BatchSettlement(
            user_id=user_id,
            total_amount_fcfa=total_amount,
            momo_fee_fcfa=momo_fee,
            net_amount_fcfa=net_amount,
            transaction_count=len(transactions),
            status=TransactionStatus.BATCHED,
        )
        batch_record = await db.insert("batch_settlements", asdict(batch))

        # 3. Appeler MoMoGateway (import ici pour éviter circular)
        from backend.services.momo_gateway import momo_gateway

        momo_result = await momo_gateway.request_debit(
            user_id=user_id,
            amount_fcfa=total_amount,
            reference=batch_record["id"],
        )

        if momo_result.get("success"):
            # 4. Marquer les transactions comme SETTLED
            for tx in transactions:
                await db.update(
                    "virtual_transactions",
                    {"id": tx["id"]},
                    {
                        "status": TransactionStatus.SETTLED.value,
                        "batch_id": batch_record["id"],
                        "settled_at": datetime.utcnow(),
                    },
                )

            # 5. Mettre à jour le batch et le wallet
            await db.update(
                "batch_settlements",
                {"id": batch_record["id"]},
                {
                    "status": TransactionStatus.SETTLED.value,
                    "momo_transaction_id": momo_result.get("transaction_id"),
                    "executed_at": datetime.utcnow(),
                },
            )

            # 6. Mettre à jour le confirmed_balance
            wallet = await db.select_one("wallets", {"user_id": user_id})
            if wallet:
                new_confirmed = wallet.get("confirmed_balance_fcfa", 0) + net_amount
                await db.update(
                    "wallets",
                    {"id": wallet["id"]},
                    {
                        "confirmed_balance_fcfa": new_confirmed,
                        "updated_at": datetime.utcnow(),
                    },
                )

            return {
                "batch_id": batch_record["id"],
                "user_id": user_id,
                "total_amount_fcfa": total_amount,
                "momo_fee_fcfa": momo_fee,
                "net_amount_fcfa": net_amount,
                "transactions_settled": len(transactions),
                "status": "SETTLED",
                "fee_savings_percentage": round(
                    (1 - (1 / len(transactions))) * 100, 1
                ),
            }
        else:
            # Échec MoMo — marquer comme FAILED, retry plus tard
            await db.update(
                "batch_settlements",
                {"id": batch_record["id"]},
                {"status": TransactionStatus.FAILED.value},
            )
            return {
                "batch_id": batch_record["id"],
                "status": "FAILED",
                "error": momo_result.get("error", "MoMo debit failed"),
            }

    async def get_batch_history(
        self, user_id: str, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Historique des batch settlements d'un utilisateur."""
        return await db.select(
            "batch_settlements",
            {"user_id": user_id},
            order_by="-created_at",
            limit=limit,
        )

    async def get_batch_stats(self) -> Dict[str, Any]:
        """Statistiques globales de batching (admin)."""
        all_batches = await db.select("batch_settlements", {})
        settled = [b for b in all_batches if b.get("status") == "SETTLED"]

        total_volume = sum(b.get("total_amount_fcfa", 0) for b in settled)
        total_fees = sum(b.get("momo_fee_fcfa", 0) for b in settled)
        total_txs = sum(b.get("transaction_count", 0) for b in settled)

        # Calcul des économies de frais
        naive_fees = total_txs * int(500 * settings.MOMO_FEE_PERCENTAGE)
        fees_saved = naive_fees - total_fees

        return {
            "total_batches": len(settled),
            "total_volume_fcfa": total_volume,
            "total_fees_fcfa": total_fees,
            "total_transactions_batched": total_txs,
            "fees_saved_fcfa": fees_saved,
            "avg_batch_size": round(total_txs / max(len(settled), 1), 1),
        }


# Singleton
batch_engine = BatchEngine()
