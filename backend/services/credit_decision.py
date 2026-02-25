"""
ScorAI — Credit Decision Engine.
Agent 07 : Décision de crédit, décaissement et suivi de remboursement.

Ce module gère tout le cycle de vie d'un micro-prêt:
1. Évaluation de la demande (score + éligibilité)
2. Calcul des intérêts et plafonnement
3. Décaissement via MoMo
4. Suivi de remboursement (rappels, pénalités)
5. Boucle de feedback vers le modèle ML
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import asdict

from backend.core.database import db
from backend.core.config import settings, SCORE_TIERS
from backend.models.schemas import Loan, LoanStatus
from backend.ml.scorai_model import scorai_model


class CreditEngine:
    """
    Moteur de décision de crédit — Le centre de profit de ScorAI.

    Gère l'évaluation, l'approbation, le décaissement et le suivi
    des micro-prêts instantanés (le produit que les utilisateurs
    restent pour utiliser — la rétention ultime).
    """

    # ============================================================
    # Évaluation de Demande
    # ============================================================

    async def evaluate_loan_request(
        self, user_id: str, requested_amount_fcfa: int
    ) -> Dict[str, Any]:
        """
        Évaluer une demande de prêt.

        Vérifie: score, tier, plafond, prêt actif, KYC.
        Si approuvé, crée le prêt et déclenche le décaissement.

        Returns:
            Dict avec la décision (approved/rejected), les détails
            du prêt, et les raisons.
        """
        # 1. Obtenir le score actuel
        score_data = await scorai_model.predict(user_id)

        if score_data.get("tier") in ("INELIGIBLE", "REJECTED"):
            return self._reject(
                user_id,
                requested_amount_fcfa,
                f"Score insuffisant (Trust Index: {score_data.get('trust_score', 0)})",
                score_data,
            )

        # 2. Vérifier le plafond
        max_loan = score_data.get("max_loan_fcfa", 0)

        # Ajuster le plafond pour le premier prêt
        previous_loans = await db.select(
            "loans",
            {"user_id": user_id, "status": "REPAID"},
        )
        if not previous_loans:
            max_loan = min(max_loan, settings.FIRST_LOAN_MAX_FCFA)

        if requested_amount_fcfa > max_loan:
            return self._reject(
                user_id,
                requested_amount_fcfa,
                f"Montant demandé ({requested_amount_fcfa} FCFA) supérieur au plafond ({max_loan} FCFA)",
                score_data,
            )

        # 3. Vérifier qu'il n'y a pas de prêt actif
        active_loans = await db.select(
            "loans",
            {"user_id": user_id},
        )
        active = [
            l for l in active_loans
            if l.get("status") in ("APPROVED", "DISBURSED", "OVERDUE")
        ]
        if active:
            return self._reject(
                user_id,
                requested_amount_fcfa,
                "Un prêt est déjà en cours. Rembourse-le d'abord.",
                score_data,
            )

        # 4. Vérifier le KYC
        kyc = await db.select_one("kyc_records", {"user_id": user_id, "status": "VERIFIED"})
        if not kyc:
            return self._reject(
                user_id,
                requested_amount_fcfa,
                "Vérification d'identité (KYC) requise avant le premier prêt.",
                score_data,
            )

        # 5. APPROUVÉ — Créer le prêt
        interest = int(requested_amount_fcfa * settings.LOAN_INTEREST_RATE)
        total_due = requested_amount_fcfa + interest
        due_date = datetime.utcnow() + timedelta(days=settings.LOAN_DURATION_DAYS)

        loan = Loan(
            user_id=user_id,
            amount_fcfa=requested_amount_fcfa,
            interest_fcfa=interest,
            total_due_fcfa=total_due,
            interest_rate=settings.LOAN_INTEREST_RATE,
            duration_days=settings.LOAN_DURATION_DAYS,
            status=LoanStatus.APPROVED,
            trust_score_at_approval=score_data.get("trust_score", 0),
        )
        loan_record = await db.insert("loans", asdict(loan))

        # 6. Décaissement automatique via MoMo
        disbursement = await self._disburse_loan(loan_record)

        return {
            "decision": "APPROVED",
            "loan_id": loan_record["id"],
            "amount_fcfa": requested_amount_fcfa,
            "interest_fcfa": interest,
            "interest_rate": f"{settings.LOAN_INTEREST_RATE * 100}%",
            "total_due_fcfa": total_due,
            "duration_days": settings.LOAN_DURATION_DAYS,
            "due_date": due_date.strftime("%d/%m/%Y"),
            "trust_score": score_data.get("trust_score", 0),
            "tier": score_data.get("tier_label", ""),
            "disbursement": disbursement,
            "message": f"🎉 Prêt de {requested_amount_fcfa} FCFA approuvé! Fonds envoyés sur ton MoMo.",
        }

    # ============================================================
    # Décaissement
    # ============================================================

    async def _disburse_loan(self, loan_record: Dict[str, Any]) -> Dict[str, Any]:
        """Décaisser le prêt via Mobile Money."""
        from backend.services.momo_gateway import momo_gateway

        result = await momo_gateway.disburse(
            user_id=loan_record["user_id"],
            amount_fcfa=loan_record["amount_fcfa"],
            reference=loan_record["id"],
        )

        if result.get("success"):
            await db.update(
                "loans",
                {"id": loan_record["id"]},
                {
                    "status": LoanStatus.DISBURSED.value,
                    "disbursed_at": datetime.utcnow(),
                    "due_date": datetime.utcnow() + timedelta(days=settings.LOAN_DURATION_DAYS),
                },
            )

        return result

    # ============================================================
    # Remboursement
    # ============================================================

    async def process_repayment(
        self, loan_id: str, amount_fcfa: int
    ) -> Dict[str, Any]:
        """
        Traiter un remboursement de prêt.

        Vérifie le montant, met à jour le statut,
        et alimente la boucle de feedback ML.
        """
        loan = await db.select_one("loans", {"id": loan_id})
        if not loan:
            return {"error": "Prêt introuvable"}

        if loan.get("status") not in ("DISBURSED", "OVERDUE"):
            return {"error": f"Ce prêt ne peut pas être remboursé (statut: {loan.get('status')})"}

        total_due = loan.get("total_due_fcfa", 0) + loan.get("penalty_fcfa", 0)

        if amount_fcfa < total_due:
            return {
                "status": "PARTIAL",
                "paid_fcfa": amount_fcfa,
                "remaining_fcfa": total_due - amount_fcfa,
                "message": f"Paiement partiel reçu. Reste: {total_due - amount_fcfa} FCFA",
            }

        # Remboursement complet
        await db.update(
            "loans",
            {"id": loan_id},
            {
                "status": LoanStatus.REPAID.value,
                "repaid_at": datetime.utcnow(),
            },
        )

        # Boucle de feedback: le remboursement réussi booste le score
        await self._feedback_repayment(loan, success=True)

        return {
            "status": "REPAID",
            "loan_id": loan_id,
            "amount_repaid_fcfa": amount_fcfa,
            "message": "✅ Prêt remboursé avec succès! Ton score de confiance augmente. 📈",
        }

    async def _feedback_repayment(
        self, loan: Dict[str, Any], success: bool
    ) -> None:
        """
        Boucle de feedback ML: les remboursements mis à jour
        alimentent le modèle ScorAI pour améliorer la prédiction.
        """
        from backend.core.database import db

        event_data = {
            "loan_id": loan.get("id"),
            "amount_fcfa": loan.get("amount_fcfa"),
            "trust_score_at_approval": loan.get("trust_score_at_approval"),
            "repaid_on_time": success,
            "duration_actual_days": (
                (datetime.utcnow() - datetime.fromisoformat(loan["disbursed_at"])).days
                if loan.get("disbursed_at")
                else None
            ),
        }

        await db.insert("analytics_events", {
            "user_id": loan.get("user_id"),
            "event_type": "loan_repaid" if success else "loan_defaulted",
            "event_data": event_data,
            "created_at": datetime.utcnow(),
        })

    # ============================================================
    # Rappels de Remboursement
    # ============================================================

    async def check_overdue_loans(self) -> List[Dict[str, Any]]:
        """
        Vérifier les prêts en retard et envoyer des rappels.

        Schedule: J-3, J-1, J0, J+1, J+3, J+7
        """
        all_disbursed = await db.select("loans", {"status": "DISBURSED"})
        reminders = []

        for loan in all_disbursed:
            due_date_str = loan.get("due_date")
            if not due_date_str:
                continue

            if isinstance(due_date_str, str):
                due_date = datetime.fromisoformat(due_date_str)
            else:
                due_date = due_date_str

            days_until_due = (due_date - datetime.utcnow()).days

            if days_until_due <= -7:
                # Prêt en défaut
                await db.update(
                    "loans",
                    {"id": loan["id"]},
                    {
                        "status": LoanStatus.DEFAULTED.value,
                        "penalty_fcfa": int(loan.get("total_due_fcfa", 0) * settings.LATE_PENALTY_RATE * 4),
                    },
                )
                await self._feedback_repayment(loan, success=False)
                reminders.append({"loan_id": loan["id"], "action": "DEFAULTED"})

            elif days_until_due <= 0:
                # En retard
                weeks_overdue = max(1, abs(days_until_due) // 7 + 1)
                penalty = int(loan.get("total_due_fcfa", 0) * settings.LATE_PENALTY_RATE * weeks_overdue)
                await db.update(
                    "loans",
                    {"id": loan["id"]},
                    {
                        "status": LoanStatus.OVERDUE.value,
                        "penalty_fcfa": penalty,
                    },
                )
                reminders.append({
                    "loan_id": loan["id"],
                    "action": "OVERDUE_REMINDER",
                    "days_overdue": abs(days_until_due),
                    "penalty_fcfa": penalty,
                })

            elif days_until_due in (1, 3):
                reminders.append({
                    "loan_id": loan["id"],
                    "action": "UPCOMING_REMINDER",
                    "days_until_due": days_until_due,
                })

        return reminders

    # ============================================================
    # Historique
    # ============================================================

    async def get_loan_status(self, loan_id: str) -> Optional[Dict[str, Any]]:
        """Récupérer le statut d'un prêt spécifique."""
        return await db.select_one("loans", {"id": loan_id})

    async def get_user_loans(self, user_id: str) -> List[Dict[str, Any]]:
        """Récupérer tous les prêts d'un utilisateur."""
        return await db.select("loans", {"user_id": user_id}, order_by="-created_at")

    async def get_loan_stats(self) -> Dict[str, Any]:
        """Statistiques globales de crédit (admin)."""
        all_loans = await db.select("loans", {})

        total_disbursed = sum(l.get("amount_fcfa", 0) for l in all_loans if l.get("status") in ("DISBURSED", "REPAID", "OVERDUE", "DEFAULTED"))
        total_repaid = sum(l.get("total_due_fcfa", 0) for l in all_loans if l.get("status") == "REPAID")
        defaulted = [l for l in all_loans if l.get("status") == "DEFAULTED"]
        npl_rate = len(defaulted) / max(len(all_loans), 1)

        return {
            "total_loans": len(all_loans),
            "total_disbursed_fcfa": total_disbursed,
            "total_repaid_fcfa": total_repaid,
            "npl_rate": round(npl_rate * 100, 2),
            "npl_target": "< 12%",
            "avg_loan_fcfa": round(total_disbursed / max(len(all_loans), 1)),
        }

    # ============================================================
    # Helpers
    # ============================================================

    def _reject(
        self, user_id: str, amount: int, reason: str, score_data: Dict
    ) -> Dict[str, Any]:
        """Construire un résultat de rejet."""
        return {
            "decision": "REJECTED",
            "user_id": user_id,
            "requested_amount_fcfa": amount,
            "reason": reason,
            "trust_score": score_data.get("trust_score", 0),
            "tier": score_data.get("tier", "REJECTED"),
            "message": f"❌ Demande rejetée: {reason}",
        }


# Singleton
credit_engine = CreditEngine()
