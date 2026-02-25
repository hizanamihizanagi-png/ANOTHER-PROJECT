"""
ScorAI — Configuration centralisée.
Toutes les variables d'environnement + constantes métier.
"""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Settings:
    """Configuration centralisée ScorAI — chargée depuis .env"""

    # --- Application ---
    APP_NAME: str = "ScorAI"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    API_PREFIX: str = "/api/v1"

    # --- Supabase ---
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # --- Mobile Money ---
    MTN_MOMO_API_URL: str = os.getenv("MTN_MOMO_API_URL", "https://sandbox.momodeveloper.mtn.com")
    MTN_MOMO_API_KEY: str = os.getenv("MTN_MOMO_API_KEY", "")
    MTN_MOMO_API_USER: str = os.getenv("MTN_MOMO_API_USER", "")
    MTN_MOMO_SUBSCRIPTION_KEY: str = os.getenv("MTN_MOMO_SUBSCRIPTION_KEY", "")
    ORANGE_MONEY_API_URL: str = os.getenv("ORANGE_MONEY_API_URL", "https://api.orange.com")
    ORANGE_MONEY_API_KEY: str = os.getenv("ORANGE_MONEY_API_KEY", "")

    # --- Sports API ---
    FOOTBALL_API_URL: str = os.getenv("FOOTBALL_API_URL", "https://v3.football.api-sports.io")
    FOOTBALL_API_KEY: str = os.getenv("FOOTBALL_API_KEY", "")

    # --- Virtual Ledger ---
    BATCH_THRESHOLD_FCFA: int = 5000  # Seuil de batching en FCFA
    BATCH_SCHEDULE_CRON: str = "0 21 * * 0"  # Dimanche 21h (fallback)
    MOMO_FEE_PERCENTAGE: float = 0.01  # 1% frais MoMo moyens

    # --- ScorAI Engine ---
    TRUST_SCORE_MIN: int = 0
    TRUST_SCORE_MAX: int = 1000
    CREDIT_UNLOCK_THRESHOLD: int = 400  # Score minimum pour le crédit
    MIN_OBSERVATION_DAYS: int = 90  # 3 mois minimum d'observation
    MIN_STREAK_DAYS: int = 60  # Streak minimum pour éligibilité

    # --- Credit ---
    FIRST_LOAN_MAX_FCFA: int = 15000  # Plafond premier prêt
    MAX_LOAN_FCFA: int = 200000  # Plafond absolu
    LOAN_INTEREST_RATE: float = 0.10  # 10% sur 30 jours
    LOAN_DURATION_DAYS: int = 30
    LATE_PENALTY_RATE: float = 0.02  # 2% pénalité de retard/semaine

    # --- Security ---
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "scorai-dev-secret-change-in-prod")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "")

    # --- Growth ---
    REFERRAL_BONUS_FCFA: int = 500  # Bonus parrainage virtuel


# Singleton
settings = Settings()


# --- Constantes ScorAI Trust Index Tiers ---
SCORE_TIERS = {
    "REJECTED": {"min": 0, "max": 399, "label": "Débutant", "max_loan": 0},
    "MICRO": {"min": 400, "max": 599, "label": "Confirmé", "max_loan": 15000},
    "STANDARD": {"min": 600, "max": 799, "label": "Expert", "max_loan": 75000},
    "PREMIUM": {"min": 800, "max": 1000, "label": "Élite", "max_loan": 200000},
}

# --- Événements Sports supportés ---
SUPPORTED_TRIGGER_EVENTS = [
    "WIN",          # Victoire de l'équipe
    "GOAL",         # But marqué
    "CLEAN_SHEET",  # Match sans but encaissé
    "DRAW",         # Match nul
]

# --- Devises ---
CURRENCY = "XAF"  # Franc CFA (CEMAC)
CURRENCY_SYMBOL = "FCFA"
