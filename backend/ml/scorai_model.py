"""
ScorAI — Trust Index Model.
Agent 06 : Le cœur algorithmique de ScorAI (le MOAT).

Ce module implémente le scoring de crédit alternatif basé sur
les données comportementales. C'est LE produit que l'on vend
aux banques en B2B (Horizon 3).

Architecture:
1. Feature extraction (via feature_engine.py)
2. Score prediction (XGBoost ou règles de fallback)
3. Tier assignment (Débutant → Confirmé → Expert → Élite)
4. SHAP explainability (exigence réglementaire)
"""

from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import math
import random

from backend.core.database import db
from backend.core.config import settings, SCORE_TIERS
from backend.models.schemas import CreditScore, ScoreTier
from backend.ml.feature_engine import feature_engine


class ScorAIModel:
    """
    ScorAI Trust Index — Modèle de scoring de crédit alternatif.

    En mode MVP: scoring basé sur des règles pondérées (rule-based).
    En production: XGBoost entraîné sur les données réelles.

    Le modèle est conçu pour être:
    - Explicable (SHAP values pour chaque décision)
    - Dynamique (mis à jour hebdomadairement avec les nouvelles données)
    - Conservateur (bias vers le rejet pour limiter le NPL)
    """

    def __init__(self):
        self._model = None  # XGBoost model (chargé via train())
        self._model_version: str = "rule_based_v1"
        self._is_ml_model: bool = False

    # ============================================================
    # Scoring
    # ============================================================

    async def predict(self, user_id: str) -> Dict[str, Any]:
        """
        Calculer le ScorAI Trust Index pour un utilisateur.

        Returns:
            Dict avec trust_score (0-1000), tier, max_loan, et explications.
        """
        # 1. Extraire les features
        feature_data = await feature_engine.extract_features(user_id)

        # 2. Vérifier l'éligibilité minimale
        observation_days = feature_data.get("observation_days", 0)
        if observation_days < settings.MIN_OBSERVATION_DAYS:
            return self._ineligible_result(
                user_id,
                observation_days,
                f"Période d'observation insuffisante ({observation_days}/{settings.MIN_OBSERVATION_DAYS} jours)",
            )

        # 3. Calculer le score
        if self._is_ml_model and self._model is not None:
            raw_score = self._predict_ml(feature_data["feature_vector"])
        else:
            raw_score = self._predict_rules(feature_data)

        # 4. Mapper vers le Trust Score (0-1000)
        trust_score = int(raw_score * settings.TRUST_SCORE_MAX)
        trust_score = max(settings.TRUST_SCORE_MIN, min(trust_score, settings.TRUST_SCORE_MAX))

        # 5. Déterminer le tier
        tier, tier_info = self._assign_tier(trust_score)

        # 6. Générer les explications (SHAP-like)
        explanations = self._generate_explanations(feature_data)

        # 7. Sauvegarder le score en DB
        score_record = await self._save_score(
            user_id, trust_score, tier, tier_info["max_loan"],
            feature_data["category_scores"],
            observation_days,
        )

        return {
            "user_id": user_id,
            "trust_score": trust_score,
            "tier": tier,
            "tier_label": tier_info["label"],
            "max_loan_fcfa": tier_info["max_loan"],
            "category_scores": feature_data["category_scores"],
            "explanations": explanations,
            "data_completeness": feature_data.get("data_completeness", 0),
            "model_version": self._model_version,
            "calculated_at": datetime.utcnow().isoformat(),
        }

    def _predict_rules(self, feature_data: Dict[str, Any]) -> float:
        """
        Scoring basé sur des règles pondérées (MVP).

        Utilise le weighted_score des catégories de features
        avec des ajustements pour les facteurs de risque.
        """
        base_score = feature_data.get("weighted_score", 0)

        # Ajustements de risque
        features = feature_data.get("feature_vector", {})
        adjustments = 0.0

        # Bonus: streak long
        streak = features.get("current_streak_days", 0)
        if streak >= 60:
            adjustments += 0.05
        if streak >= 90:
            adjustments += 0.05

        # Bonus: haute régularité
        regularity = features.get("deposit_regularity", 0)
        if regularity > 0.8:
            adjustments += 0.03

        # Bonus: ancienneté SIM
        sim_age = features.get("sim_age_months", 0)
        if sim_age >= 24:
            adjustments += 0.03

        # Malus: trop peu de dépôts
        deposits = features.get("total_deposits", 0)
        if deposits < 5:
            adjustments -= 0.10

        # Malus: données incomplètes
        completeness = feature_data.get("data_completeness", 0)
        if completeness < 0.5:
            adjustments -= 0.10

        return min(max(base_score + adjustments, 0), 1)

    def _predict_ml(self, feature_vector: Dict[str, Any]) -> float:
        """
        Scoring via modèle ML (XGBoost) — Production.

        Prend le vecteur de features et retourne une probabilité
        de remboursement (0-1).
        """
        if self._model is None:
            raise ValueError("ML model not loaded. Call train() first.")

        # Convertir en array pour XGBoost
        feature_names = sorted(feature_vector.keys())
        feature_values = [feature_vector.get(f, 0) for f in feature_names]

        # Prediction (probability of repayment)
        # probability = self._model.predict_proba([feature_values])[0][1]
        # return probability

        # Fallback to rules for now
        return 0.5

    # ============================================================
    # Tier Assignment
    # ============================================================

    def _assign_tier(self, trust_score: int) -> Tuple[str, Dict]:
        """Assigner un tier basé sur le Trust Score."""
        for tier_name, tier_info in SCORE_TIERS.items():
            if tier_info["min"] <= trust_score <= tier_info["max"]:
                return tier_name, tier_info
        return "REJECTED", SCORE_TIERS["REJECTED"]

    # ============================================================
    # Explainability (SHAP-like)
    # ============================================================

    def _generate_explanations(self, feature_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Générer des explications humaines du score.

        Style: "Ton score est élevé grâce à: Régularité (40%), ..."
        Exigence réglementaire COBAC + outil de rétention UX.
        """
        scores = feature_data.get("category_scores", {})
        explanations = []

        # Trier par impact
        score_items = [
            ("Discipline d'épargne", scores.get("savings_discipline_score", 0), "💰", 0.40),
            ("Activité Mobile Money", scores.get("momo_activity_score", 0), "📱", 0.25),
            ("Stabilité Télécom", scores.get("telco_stability_score", 0), "📶", 0.20),
            ("Comportement financier", scores.get("behavioral_score", 0), "🎯", 0.15),
        ]

        for name, score, icon, weight in sorted(score_items, key=lambda x: x[1] * x[3], reverse=True):
            impact = score * weight
            if score >= 0.7:
                sentiment = "excellent"
                advice = "Continue comme ça!"
            elif score >= 0.4:
                sentiment = "bon"
                advice = "Encore un peu d'effort pour atteindre l'excellence."
            else:
                sentiment = "à améliorer"
                advice = "Concentre-toi sur ce domaine pour booster ton score."

            explanations.append({
                "category": name,
                "icon": icon,
                "score": round(score, 2),
                "weight_percentage": int(weight * 100),
                "impact": round(impact, 3),
                "sentiment": sentiment,
                "advice": advice,
            })

        return explanations

    # ============================================================
    # Persistence
    # ============================================================

    async def _save_score(
        self,
        user_id: str,
        trust_score: int,
        tier: str,
        max_loan: int,
        category_scores: Dict,
        observation_days: int,
    ) -> Dict[str, Any]:
        """Sauvegarder le score en base de données."""
        from dataclasses import asdict

        score = CreditScore(
            user_id=user_id,
            trust_score=trust_score,
            tier=ScoreTier(tier),
            max_loan_fcfa=max_loan,
            savings_discipline_score=category_scores.get("savings_discipline_score", 0),
            telco_stability_score=category_scores.get("telco_stability_score", 0),
            momo_activity_score=category_scores.get("momo_activity_score", 0),
            behavioral_score=category_scores.get("behavioral_score", 0),
            observation_days=observation_days,
            last_calculated_at=datetime.utcnow(),
        )
        return await db.insert("credit_scores", asdict(score))

    def _ineligible_result(self, user_id: str, days: int, reason: str) -> Dict:
        """Résultat pour un utilisateur non éligible."""
        return {
            "user_id": user_id,
            "trust_score": 0,
            "tier": "INELIGIBLE",
            "tier_label": "En observation",
            "max_loan_fcfa": 0,
            "observation_days": days,
            "days_remaining": settings.MIN_OBSERVATION_DAYS - days,
            "reason": reason,
            "message": f"Continue d'épargner! Plus que {settings.MIN_OBSERVATION_DAYS - days} jours avant de pouvoir débloquer ton crédit. 💪",
        }

    # ============================================================
    # Training (Production)
    # ============================================================

    async def train(self, training_data: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Entraîner le modèle XGBoost.

        En production: appelé hebdomadairement avec les données
        fraîches (remboursements confirmés vs défauts).
        """
        # TODO: Implémenter l'entraînement XGBoost réel
        # import xgboost as xgb
        # self._model = xgb.XGBClassifier(
        #     learning_rate=0.1, max_depth=6, n_estimators=200,
        #     objective='binary:logistic', eval_metric='auc'
        # )
        # self._model.fit(X_train, y_train)
        # self._is_ml_model = True

        return {
            "status": "training_not_available",
            "model_version": self._model_version,
            "message": "Le modèle ML sera entraîné quand suffisamment de données seront disponibles.",
        }


# Singleton
scorai_model = ScorAIModel()
