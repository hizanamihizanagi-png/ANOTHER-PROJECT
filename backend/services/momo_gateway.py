"""
ScorAI — Mobile Money Gateway.
Agent 04 : Intégration MTN MoMo & Orange Money.

Abstraction unifiée pour les prélèvements et décaissements
via les API Mobile Money du Cameroun.

Features:
- Client MTN MoMo (Collection API Sandbox)
- Client Orange Money (Sandbox)
- Retry avec backoff exponentiel
- Webhook receiver pour confirmations asynchrones
- Mock complet pour développement local
"""

from datetime import datetime
from typing import Dict, Any, Optional
import uuid
import asyncio


class MoMoGateway:
    """
    Passerelle Mobile Money unifiée.

    Supporte MTN MoMo et Orange Money avec une interface commune.
    En mode sandbox/dev, simule les transactions pour le testing.
    """

    def __init__(self, sandbox: bool = True):
        self.sandbox = sandbox
        self._transaction_log: list = []
        self._max_retries: int = 3
        self._base_delay: float = 1.0  # secondes

    # ============================================================
    # Prélèvements (Collection — pour le batching)
    # ============================================================

    async def request_debit(
        self,
        user_id: str,
        amount_fcfa: int,
        reference: str,
        phone_number: str = "",
        provider: str = "MTN",
    ) -> Dict[str, Any]:
        """
        Demander un prélèvement sur le portefeuille Mobile Money.

        Utilisé par le BatchEngine pour les prélèvements groupés.
        Implémente un retry avec backoff exponentiel.

        Args:
            user_id: ID utilisateur ScorAI
            amount_fcfa: Montant en FCFA
            reference: Référence unique (batch_id)
            phone_number: Numéro de téléphone MoMo
            provider: "MTN" ou "ORANGE"

        Returns:
            Dict avec success, transaction_id, et détails.
        """
        for attempt in range(self._max_retries):
            try:
                if self.sandbox:
                    result = await self._simulate_debit(
                        user_id, amount_fcfa, reference, provider
                    )
                else:
                    if provider == "MTN":
                        result = await self._mtn_request_to_pay(
                            phone_number, amount_fcfa, reference
                        )
                    elif provider == "ORANGE":
                        result = await self._orange_request_payment(
                            phone_number, amount_fcfa, reference
                        )
                    else:
                        return {"success": False, "error": f"Provider inconnu: {provider}"}

                if result.get("success"):
                    self._transaction_log.append({
                        "type": "DEBIT",
                        "user_id": user_id,
                        "amount_fcfa": amount_fcfa,
                        "reference": reference,
                        "provider": provider,
                        "transaction_id": result["transaction_id"],
                        "timestamp": datetime.utcnow().isoformat(),
                    })
                    return result

            except Exception as e:
                if attempt < self._max_retries - 1:
                    delay = self._base_delay * (2 ** attempt)  # Backoff exponentiel
                    await asyncio.sleep(delay)
                else:
                    return {
                        "success": False,
                        "error": f"Échec après {self._max_retries} tentatives: {str(e)}",
                    }

        return {"success": False, "error": "Max retries reached"}

    # ============================================================
    # Décaissements (Disbursement — pour les prêts)
    # ============================================================

    async def disburse(
        self,
        user_id: str,
        amount_fcfa: int,
        reference: str,
        phone_number: str = "",
        provider: str = "MTN",
    ) -> Dict[str, Any]:
        """
        Envoyer de l'argent vers le portefeuille Mobile Money de l'utilisateur.

        Utilisé par le CreditEngine pour le décaissement des prêts.

        Args:
            user_id: ID utilisateur ScorAI
            amount_fcfa: Montant du prêt en FCFA
            reference: Référence unique (loan_id)
            phone_number: Numéro de téléphone MoMo
            provider: "MTN" ou "ORANGE"

        Returns:
            Dict avec success, transaction_id, et détails.
        """
        for attempt in range(self._max_retries):
            try:
                if self.sandbox:
                    result = await self._simulate_disbursement(
                        user_id, amount_fcfa, reference, provider
                    )
                else:
                    if provider == "MTN":
                        result = await self._mtn_transfer(
                            phone_number, amount_fcfa, reference
                        )
                    elif provider == "ORANGE":
                        result = await self._orange_transfer(
                            phone_number, amount_fcfa, reference
                        )
                    else:
                        return {"success": False, "error": f"Provider inconnu: {provider}"}

                if result.get("success"):
                    self._transaction_log.append({
                        "type": "DISBURSEMENT",
                        "user_id": user_id,
                        "amount_fcfa": amount_fcfa,
                        "reference": reference,
                        "provider": provider,
                        "transaction_id": result["transaction_id"],
                        "timestamp": datetime.utcnow().isoformat(),
                    })
                    return result

            except Exception as e:
                if attempt < self._max_retries - 1:
                    delay = self._base_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
                else:
                    return {
                        "success": False,
                        "error": f"Échec après {self._max_retries} tentatives: {str(e)}",
                    }

        return {"success": False, "error": "Max retries reached"}

    async def check_status(self, transaction_id: str) -> Dict[str, Any]:
        """Vérifier le statut d'une transaction MoMo."""
        if self.sandbox:
            return {
                "transaction_id": transaction_id,
                "status": "SUCCESSFUL",
                "reason": "Sandbox simulation",
            }
        # TODO: Appel API réel pour vérification de statut
        raise NotImplementedError("Production check_status not implemented")

    async def get_balance(self, provider: str = "MTN") -> Dict[str, Any]:
        """Vérifier le solde du compte collecteur ScorAI."""
        if self.sandbox:
            return {
                "provider": provider,
                "balance_fcfa": 5000000,  # 5M FCFA simulé
                "currency": "XAF",
            }
        raise NotImplementedError("Production get_balance not implemented")

    # ============================================================
    # Webhook Handler
    # ============================================================

    async def handle_callback(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Traiter les callbacks/webhooks de MoMo.

        Les opérateurs envoient des notifications asynchrones
        quand une transaction est complétée ou échoue.
        """
        transaction_id = payload.get("externalId") or payload.get("transactionId")
        status = payload.get("status", "UNKNOWN")

        # Logger le callback
        self._transaction_log.append({
            "type": "CALLBACK",
            "transaction_id": transaction_id,
            "status": status,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat(),
        })

        return {
            "received": True,
            "transaction_id": transaction_id,
            "status": status,
        }

    # ============================================================
    # Simulation (Sandbox)
    # ============================================================

    async def _simulate_debit(
        self, user_id: str, amount_fcfa: int, reference: str, provider: str
    ) -> Dict[str, Any]:
        """Simuler un prélèvement MoMo (sandbox)."""
        await asyncio.sleep(0.1)  # Simuler la latence réseau

        # Simulation: 95% de succès (réaliste pour le Cameroun)
        import random
        success = random.random() < 0.95

        return {
            "success": success,
            "transaction_id": f"MOMO_{provider}_{uuid.uuid4().hex[:12].upper()}",
            "amount_fcfa": amount_fcfa,
            "provider": provider,
            "reference": reference,
            "status": "SUCCESSFUL" if success else "FAILED",
            "error": None if success else "Solde insuffisant",
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def _simulate_disbursement(
        self, user_id: str, amount_fcfa: int, reference: str, provider: str
    ) -> Dict[str, Any]:
        """Simuler un décaissement MoMo (sandbox)."""
        await asyncio.sleep(0.1)

        return {
            "success": True,
            "transaction_id": f"DISB_{provider}_{uuid.uuid4().hex[:12].upper()}",
            "amount_fcfa": amount_fcfa,
            "provider": provider,
            "reference": reference,
            "status": "SUCCESSFUL",
            "timestamp": datetime.utcnow().isoformat(),
        }

    # ============================================================
    # Production API Clients (Stubs)
    # ============================================================

    async def _mtn_request_to_pay(
        self, phone: str, amount: int, reference: str
    ) -> Dict[str, Any]:
        """
        MTN MoMo Collection API — RequestToPay.
        
        Production implementation:
        POST https://sandbox.momodeveloper.mtn.com/collection/v1_0/requesttopay
        Headers: Authorization: Bearer {token}, X-Reference-Id: {uuid}
        Body: {"amount": "1000", "currency": "XAF", "payer": {"partyIdType": "MSISDN", "partyId": "237XXXXXXXXX"}}
        """
        raise NotImplementedError("MTN production API not configured")

    async def _mtn_transfer(
        self, phone: str, amount: int, reference: str
    ) -> Dict[str, Any]:
        """MTN MoMo Disbursement API — Transfer."""
        raise NotImplementedError("MTN disbursement API not configured")

    async def _orange_request_payment(
        self, phone: str, amount: int, reference: str
    ) -> Dict[str, Any]:
        """Orange Money Payment API — Request Payment."""
        raise NotImplementedError("Orange Money API not configured")

    async def _orange_transfer(
        self, phone: str, amount: int, reference: str
    ) -> Dict[str, Any]:
        """Orange Money Transfer API."""
        raise NotImplementedError("Orange Money transfer not configured")


# Singleton
momo_gateway = MoMoGateway(sandbox=True)
