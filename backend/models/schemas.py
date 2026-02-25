"""
ScorAI — Modèles de base de données (SQLAlchemy-style pour Supabase/PostgreSQL).
Ces modèles définissent la structure des tables principales.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List
import uuid


# ============================================================
# ENUMS
# ============================================================

class TransactionStatus(str, Enum):
    PENDING = "PENDING"        # Crédit virtuel, pas encore prélevé
    BATCHED = "BATCHED"        # Inclus dans un batch en cours
    SETTLED = "SETTLED"        # Prélèvement MoMo confirmé
    FAILED = "FAILED"          # Échec du prélèvement
    CANCELLED = "CANCELLED"    # Annulé par l'utilisateur


class TriggerEventType(str, Enum):
    WIN = "WIN"
    GOAL = "GOAL"
    CLEAN_SHEET = "CLEAN_SHEET"
    DRAW = "DRAW"


class TriggerStatus(str, Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    DELETED = "DELETED"


class LoanStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DISBURSED = "DISBURSED"
    REPAID = "REPAID"
    OVERDUE = "OVERDUE"
    DEFAULTED = "DEFAULTED"


class KYCStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class ScoreTier(str, Enum):
    REJECTED = "REJECTED"
    MICRO = "MICRO"
    STANDARD = "STANDARD"
    PREMIUM = "PREMIUM"


# ============================================================
# DATA MODELS
# ============================================================

@dataclass
class User:
    """Utilisateur ScorAI"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    phone_number: str = ""
    display_name: str = ""
    favorite_team_id: Optional[int] = None
    favorite_team_name: Optional[str] = None
    kyc_status: KYCStatus = KYCStatus.NOT_STARTED
    referral_code: str = field(default_factory=lambda: uuid.uuid4().hex[:8].upper())
    referred_by: Optional[str] = None
    device_fingerprint: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True


@dataclass
class Wallet:
    """Portefeuille virtuel d'un utilisateur"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    virtual_balance_fcfa: int = 0      # Solde virtuel (instantané, UX)
    confirmed_balance_fcfa: int = 0    # Solde réel (post-settlement MoMo)
    total_saved_fcfa: int = 0          # Total cumulé épargné
    current_streak_days: int = 0       # Streak actuel
    longest_streak_days: int = 0       # Record personnel
    last_trigger_date: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class VirtualTransaction:
    """Transaction virtuelle (une par trigger sportif)"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    wallet_id: str = ""
    amount_fcfa: int = 0
    trigger_id: Optional[str] = None
    trigger_event: Optional[str] = None    # ex: "Arsenal WIN vs Chelsea"
    status: TransactionStatus = TransactionStatus.PENDING
    batch_id: Optional[str] = None         # Lien vers le batch de settlement
    created_at: datetime = field(default_factory=datetime.utcnow)
    settled_at: Optional[datetime] = None


@dataclass
class BatchSettlement:
    """Batch de prélèvement MoMo (agrégation de transactions virtuelles)"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    total_amount_fcfa: int = 0
    momo_fee_fcfa: int = 0              # Frais MoMo calculés
    net_amount_fcfa: int = 0            # Montant net après frais
    transaction_count: int = 0
    momo_transaction_id: Optional[str] = None  # ID de la transaction MoMo
    momo_provider: str = "MTN"          # MTN ou ORANGE
    status: TransactionStatus = TransactionStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    executed_at: Optional[datetime] = None


@dataclass
class UserTrigger:
    """Règle de déclenchement sportif configurée par l'utilisateur"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    team_id: int = 0                    # ID de l'équipe (API Football)
    team_name: str = ""
    event_type: TriggerEventType = TriggerEventType.WIN
    amount_fcfa: int = 500              # Montant par déclenchement
    status: TriggerStatus = TriggerStatus.ACTIVE
    times_triggered: int = 0
    total_saved_fcfa: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CreditScore:
    """Profil de scoring ScorAI Trust Index"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    trust_score: int = 0               # Score 0-1000
    tier: ScoreTier = ScoreTier.REJECTED
    max_loan_fcfa: int = 0

    # Feature breakdown (pour SHAP / explicabilité)
    savings_discipline_score: float = 0.0   # 0-1
    telco_stability_score: float = 0.0      # 0-1
    momo_activity_score: float = 0.0        # 0-1
    behavioral_score: float = 0.0           # 0-1

    observation_days: int = 0
    last_calculated_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Loan:
    """Prêt micro-crédit"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    amount_fcfa: int = 0
    interest_fcfa: int = 0              # Intérêts calculés
    total_due_fcfa: int = 0             # Montant total dû
    penalty_fcfa: int = 0               # Pénalités de retard
    interest_rate: float = 0.10
    duration_days: int = 30
    status: LoanStatus = LoanStatus.PENDING
    trust_score_at_approval: int = 0    # Score au moment de l'approbation
    disbursed_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    repaid_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class KYCRecord:
    """Vérification d'identité (e-KYC)"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    full_name: str = ""
    date_of_birth: Optional[str] = None
    national_id_number: Optional[str] = None
    selfie_url: Optional[str] = None    # Stocké dans Supabase Storage
    status: KYCStatus = KYCStatus.PENDING
    rejection_reason: Optional[str] = None
    verified_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AnalyticsEvent:
    """Événement analytics pour le tracking"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    event_type: str = ""               # signup, first_trigger, first_deposit, credit_unlock, loan_taken
    event_data: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Referral:
    """Parrainage"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    referrer_id: str = ""
    referred_id: str = ""
    bonus_credited: bool = False
    bonus_amount_fcfa: int = 500
    created_at: datetime = field(default_factory=datetime.utcnow)
