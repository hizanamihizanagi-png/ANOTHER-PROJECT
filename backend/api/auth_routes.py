"""ScorAI — Auth & KYC API Routes (Agent 11)."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from dataclasses import asdict
import uuid

from backend.core.database import db
from backend.models.schemas import User, KYCRecord, KYCStatus, Wallet


auth_router = APIRouter()


class SignupRequest(BaseModel):
    phone_number: str
    display_name: str
    favorite_team_id: Optional[int] = None
    favorite_team_name: Optional[str] = None
    referral_code: Optional[str] = None


class KYCRequest(BaseModel):
    user_id: str
    full_name: str
    date_of_birth: str
    national_id_number: str


@auth_router.post("/auth/signup")
async def signup(req: SignupRequest):
    """Inscription par numéro de téléphone."""
    # Vérifier si l'utilisateur existe déjà
    existing = await db.select_one("users", {"phone_number": req.phone_number})
    if existing:
        return {"error": "Ce numéro est déjà inscrit", "user_id": existing["id"]}

    # Créer l'utilisateur
    user = User(
        phone_number=req.phone_number,
        display_name=req.display_name,
        favorite_team_id=req.favorite_team_id,
        favorite_team_name=req.favorite_team_name,
        referred_by=req.referral_code,
    )
    user_record = await db.insert("users", asdict(user))

    # Créer le wallet
    wallet = Wallet(user_id=user_record["id"])
    await db.insert("wallets", asdict(wallet))

    # Traiter le parrainage
    if req.referral_code:
        referrer = await db.select_one("users", {"referral_code": req.referral_code})
        if referrer:
            await db.insert("referrals", {
                "id": str(uuid.uuid4()),
                "referrer_id": referrer["id"],
                "referred_id": user_record["id"],
                "bonus_amount_fcfa": 500,
                "created_at": datetime.utcnow(),
            })

    # Tracker l'événement
    await db.insert("analytics_events", {
        "id": str(uuid.uuid4()),
        "user_id": user_record["id"],
        "event_type": "signup",
        "event_data": {"method": "phone", "has_referral": bool(req.referral_code)},
        "created_at": datetime.utcnow(),
    })

    return {
        "user_id": user_record["id"],
        "referral_code": user_record["referral_code"],
        "message": f"🎉 Bienvenue sur ScorAI, {req.display_name}!",
    }


@auth_router.get("/auth/user/{user_id}")
async def get_user(user_id: str):
    """Récupérer le profil utilisateur."""
    user = await db.select_one("users", {"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    return user


@auth_router.post("/auth/kyc")
async def submit_kyc(req: KYCRequest):
    """Soumettre une vérification d'identité (e-KYC)."""
    kyc = KYCRecord(
        user_id=req.user_id,
        full_name=req.full_name,
        date_of_birth=req.date_of_birth,
        national_id_number=req.national_id_number,
        status=KYCStatus.VERIFIED,  # Auto-verify pour le MVP
        verified_at=datetime.utcnow(),
    )
    record = await db.insert("kyc_records", asdict(kyc))

    # Mettre à jour le statut KYC de l'utilisateur
    await db.update("users", {"id": req.user_id}, {"kyc_status": "VERIFIED"})

    return {
        "kyc_id": record["id"],
        "status": "VERIFIED",
        "message": "✅ Identité vérifiée! Tu peux maintenant demander un crédit.",
    }


@auth_router.get("/auth/kyc/{user_id}")
async def get_kyc_status(user_id: str):
    """Vérifier le statut KYC d'un utilisateur."""
    kyc = await db.select_one("kyc_records", {"user_id": user_id})
    if not kyc:
        return {"user_id": user_id, "status": "NOT_STARTED"}
    return kyc
