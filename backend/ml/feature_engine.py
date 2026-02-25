"""
ScorAI — Feature Engineering Pipeline.
Agent 05 : Construction du vecteur de features pour le scoring ML.

Ce module transforme les données brutes (épargne, Telco, MoMo, comportement)
en un vecteur de features normalisé pour le modèle ScorAI Trust Index.

Catégories de features:
1. Discipline d'Épargne (40% du score) — Données internes
2. Télécoms / Stabilité (20%) — Données simulées (production: Telco API)
3. Mobile Money Activity (25%) — Données du wallet
4. Comportement (15%) — Factures, régularité
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import math
import random

from backend.core.database import db
from backend.core.config import settings


class FeatureEngine:
    """
    Pipeline de feature engineering pour le ScorAI Trust Index.

    Extrait 20+ features à partir des données multi-sources
    et les normalise pour input dans le modèle XGBoost.
    """

    # Poids des catégories (calibrés sur le business plan)
    CATEGORY_WEIGHTS = {
        "savings_discipline": 0.40,
        "telco_stability": 0.20,
        "momo_activity": 0.25,
        "behavioral": 0.15,
    }

    async def extract_features(self, user_id: str) -> Dict[str, Any]:
        """
        Extraire le vecteur de features complet pour un utilisateur.

        Returns:
            Dict avec toutes les features normalisées (0-1)
            + les métadonnées (observation_days, data_completeness).
        """
        # 1. Features de discipline d'épargne
        savings = await self._extract_savings_features(user_id)

        # 2. Features télécoms (simulées pour le MVP)
        telco = await self._extract_telco_features(user_id)

        # 3. Features Mobile Money
        momo = await self._extract_momo_features(user_id)

        # 4. Features comportementales
        behavioral = await self._extract_behavioral_features(user_id)

        # 5. Calculer le score par catégorie
        category_scores = {
            "savings_discipline_score": savings["category_score"],
            "telco_stability_score": telco["category_score"],
            "momo_activity_score": momo["category_score"],
            "behavioral_score": behavioral["category_score"],
        }

        # 6. Assembler le vecteur complet
        feature_vector = {
            **savings["features"],
            **telco["features"],
            **momo["features"],
            **behavioral["features"],
        }

        # 7. Calculer le score composite pondéré
        weighted_score = sum(
            category_scores[f"{cat}_score"] * weight
            for cat, weight in self.CATEGORY_WEIGHTS.items()
        )

        return {
            "user_id": user_id,
            "feature_vector": feature_vector,
            "category_scores": category_scores,
            "weighted_score": weighted_score,
            "observation_days": savings["features"].get("observation_days", 0),
            "data_completeness": self._calculate_completeness(feature_vector),
            "extracted_at": datetime.utcnow().isoformat(),
        }

    # ============================================================
    # 1. SAVINGS DISCIPLINE (40%)
    # ============================================================

    async def _extract_savings_features(self, user_id: str) -> Dict[str, Any]:
        """
        Features de discipline d'épargne — données 100% internes.
        """
        wallet = await db.select_one("wallets", {"user_id": user_id})
        transactions = await db.select(
            "virtual_transactions", {"user_id": user_id}
        )
        triggers = await db.select(
            "user_triggers", {"user_id": user_id, "status": "ACTIVE"}
        )

        if not wallet:
            return {"features": self._default_savings_features(), "category_score": 0.0}

        # Feature extraction
        total_deposits = len(transactions)
        settled_deposits = len([t for t in transactions if t.get("status") == "SETTLED"])

        # Observation period
        created = wallet.get("created_at", datetime.utcnow().isoformat())
        if isinstance(created, str):
            try:
                created_dt = datetime.fromisoformat(created)
            except (ValueError, TypeError):
                created_dt = datetime.utcnow()
        else:
            created_dt = created
        observation_days = max((datetime.utcnow() - created_dt).days, 1)

        # Frequency (dépôts par mois)
        months = max(observation_days / 30, 1)
        deposit_frequency = total_deposits / months

        # Streak
        current_streak = wallet.get("current_streak_days", 0)
        longest_streak = wallet.get("longest_streak_days", 0)

        # Montant moyen
        amounts = [t.get("amount_fcfa", 0) for t in transactions]
        avg_amount = sum(amounts) / max(len(amounts), 1)

        # Régularité (std dev normalisée — plus faible = plus régulier)
        if len(amounts) > 1:
            mean = sum(amounts) / len(amounts)
            variance = sum((x - mean) ** 2 for x in amounts) / len(amounts)
            std_dev = math.sqrt(variance)
            regularity = max(0, 1 - (std_dev / max(mean, 1)))
        else:
            regularity = 0.5

        features = {
            "observation_days": observation_days,
            "total_deposits": total_deposits,
            "deposit_frequency_monthly": round(deposit_frequency, 2),
            "current_streak_days": current_streak,
            "longest_streak_days": longest_streak,
            "streak_ratio": round(current_streak / max(observation_days, 1), 3),
            "avg_deposit_amount": round(avg_amount, 0),
            "deposit_regularity": round(regularity, 3),
            "active_triggers_count": len(triggers),
            "total_saved_fcfa": wallet.get("total_saved_fcfa", 0),
        }

        # Score de catégorie (0-1)
        score = self._normalize_score([
            min(deposit_frequency / 10, 1.0) * 0.25,       # Fréquence
            min(current_streak / 90, 1.0) * 0.30,           # Streak (3 mois = max)
            regularity * 0.20,                                # Régularité
            min(len(triggers) / 3, 1.0) * 0.10,             # Triggers actifs
            min(total_deposits / 20, 1.0) * 0.15,           # Volume total
        ])

        return {"features": features, "category_score": score}

    # ============================================================
    # 2. TELCO STABILITY (20%)
    # ============================================================

    async def _extract_telco_features(self, user_id: str) -> Dict[str, Any]:
        """
        Features télécoms — simulées pour le MVP.

        En production, ces données viennent des API Telco
        (historique recharges, âge SIM, volume appels).
        """
        # === SIMULATION pour le MVP ===
        # Génération réaliste basée sur les distributions camerounaises
        random.seed(hash(user_id) % 2**32)

        sim_age_months = random.randint(6, 96)  # 6 mois à 8 ans
        airtime_recharge_freq = random.uniform(2, 15)  # Recharges/mois
        avg_recharge_amount = random.randint(200, 2000)  # FCFA
        call_regularity = random.uniform(0.3, 0.95)
        data_usage_mb = random.randint(100, 5000)
        unique_contacts_30d = random.randint(5, 100)

        features = {
            "sim_age_months": sim_age_months,
            "airtime_recharge_frequency": round(airtime_recharge_freq, 2),
            "avg_recharge_amount_fcfa": avg_recharge_amount,
            "call_regularity_score": round(call_regularity, 3),
            "data_usage_mb_monthly": data_usage_mb,
            "unique_contacts_30d": unique_contacts_30d,
        }

        # Score de catégorie
        score = self._normalize_score([
            min(sim_age_months / 48, 1.0) * 0.30,            # Ancienneté SIM
            min(airtime_recharge_freq / 10, 1.0) * 0.25,     # Fréquence recharge
            call_regularity * 0.20,                            # Régularité appels
            min(unique_contacts_30d / 50, 1.0) * 0.15,       # Réseau social
            min(data_usage_mb / 3000, 1.0) * 0.10,           # Usage data
        ])

        return {"features": features, "category_score": score}

    # ============================================================
    # 3. MOBILE MONEY ACTIVITY (25%)
    # ============================================================

    async def _extract_momo_features(self, user_id: str) -> Dict[str, Any]:
        """
        Features Mobile Money — dérivées des données du wallet.

        En production, enrichies par l'accès aux logs SMS MoMo
        (avec consentement e-KYC).
        """
        wallet = await db.select_one("wallets", {"user_id": user_id})
        settlements = await db.select(
            "batch_settlements", {"user_id": user_id, "status": "SETTLED"}
        )

        if not wallet:
            return {"features": self._default_momo_features(), "category_score": 0.0}

        # Transaction volume
        total_volume = sum(s.get("total_amount_fcfa", 0) for s in settlements)
        transaction_count = len(settlements)
        avg_batch_size = total_volume / max(transaction_count, 1)

        # === SIMULATION des données MoMo enrichies ===
        random.seed(hash(user_id + "momo") % 2**32)

        incoming_transfers_monthly = random.randint(1, 20)
        unique_senders = random.randint(1, 10)
        bill_payments_monthly = random.randint(0, 5)
        merchant_payments_monthly = random.randint(0, 15)

        features = {
            "momo_transaction_volume_30d": total_volume,
            "momo_transaction_count_30d": transaction_count,
            "momo_avg_batch_size_fcfa": round(avg_batch_size, 0),
            "incoming_transfers_monthly": incoming_transfers_monthly,
            "unique_senders_count": unique_senders,
            "bill_payments_monthly": bill_payments_monthly,
            "merchant_payments_monthly": merchant_payments_monthly,
        }

        # Score de catégorie
        score = self._normalize_score([
            min(total_volume / 50000, 1.0) * 0.25,            # Volume
            min(incoming_transfers_monthly / 10, 1.0) * 0.25, # Transferts entrants
            min(unique_senders / 5, 1.0) * 0.20,              # Stabilité revenus
            min(bill_payments_monthly / 3, 1.0) * 0.20,       # Factures
            min(transaction_count / 10, 1.0) * 0.10,           # Activité
        ])

        return {"features": features, "category_score": score}

    # ============================================================
    # 4. BEHAVIORAL (15%)
    # ============================================================

    async def _extract_behavioral_features(self, user_id: str) -> Dict[str, Any]:
        """
        Features comportementales — paiement de factures, régularité.

        En production, enrichies par les APIs de facturiers
        (ENEO, CamWater, etc.).
        """
        # === SIMULATION pour le MVP ===
        random.seed(hash(user_id + "behavior") % 2**32)

        eneo_payment_regularity = random.uniform(0.2, 1.0)
        camwater_payment_regularity = random.uniform(0.1, 0.9)
        device_age_months = random.randint(3, 48)
        app_sessions_weekly = random.randint(1, 21)
        notification_response_rate = random.uniform(0.2, 0.95)

        features = {
            "eneo_payment_regularity": round(eneo_payment_regularity, 3),
            "camwater_payment_regularity": round(camwater_payment_regularity, 3),
            "device_age_months": device_age_months,
            "app_sessions_weekly": app_sessions_weekly,
            "notification_response_rate": round(notification_response_rate, 3),
        }

        # Score de catégorie
        score = self._normalize_score([
            eneo_payment_regularity * 0.30,                      # Facture élec.
            camwater_payment_regularity * 0.20,                  # Facture eau
            min(device_age_months / 24, 1.0) * 0.15,            # Stabilité device
            min(app_sessions_weekly / 14, 1.0) * 0.15,          # Engagement app
            notification_response_rate * 0.20,                    # Réactivité
        ])

        return {"features": features, "category_score": score}

    # ============================================================
    # Helpers
    # ============================================================

    def _normalize_score(self, weighted_components: List[float]) -> float:
        """Normaliser un score composite entre 0 et 1."""
        return round(min(max(sum(weighted_components), 0), 1), 4)

    def _calculate_completeness(self, features: Dict) -> float:
        """Calculer le taux de complétude des données."""
        total = len(features)
        filled = sum(1 for v in features.values() if v is not None and v != 0)
        return round(filled / max(total, 1), 3)

    def _default_savings_features(self) -> Dict[str, Any]:
        """Features par défaut quand aucune donnée d'épargne n'existe."""
        return {
            "observation_days": 0, "total_deposits": 0,
            "deposit_frequency_monthly": 0, "current_streak_days": 0,
            "longest_streak_days": 0, "streak_ratio": 0,
            "avg_deposit_amount": 0, "deposit_regularity": 0,
            "active_triggers_count": 0, "total_saved_fcfa": 0,
        }

    def _default_momo_features(self) -> Dict[str, Any]:
        """Features par défaut quand aucune donnée MoMo n'existe."""
        return {
            "momo_transaction_volume_30d": 0, "momo_transaction_count_30d": 0,
            "momo_avg_batch_size_fcfa": 0, "incoming_transfers_monthly": 0,
            "unique_senders_count": 0, "bill_payments_monthly": 0,
            "merchant_payments_monthly": 0,
        }


# Singleton
feature_engine = FeatureEngine()
