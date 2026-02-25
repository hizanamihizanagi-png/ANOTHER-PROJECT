"""ScorAI — Analytics & Growth API Routes (Agent 10)."""

from fastapi import APIRouter
from typing import Optional
from datetime import datetime
import uuid

from backend.core.database import db


analytics_router = APIRouter()


@analytics_router.get("/analytics/dashboard")
async def get_dashboard():
    """Dashboard analytics — métriques clés en temps réel."""
    users = await db.select("users", {})
    wallets = await db.select("wallets", {})
    loans = await db.select("loans", {})
    triggers = await db.select("user_triggers", {"status": "ACTIVE"})
    referrals = await db.select("referrals", {})

    total_users = len(users)
    active_savers = len([w for w in wallets if w.get("total_saved_fcfa", 0) > 0])
    total_saved = sum(w.get("total_saved_fcfa", 0) for w in wallets)
    total_loans = len(loans)
    total_disbursed = sum(l.get("amount_fcfa", 0) for l in loans if l.get("status") != "PENDING")
    repaid = len([l for l in loans if l.get("status") == "REPAID"])
    defaulted = len([l for l in loans if l.get("status") == "DEFAULTED"])
    npl_rate = (defaulted / max(total_loans, 1)) * 100

    # ARPU
    total_interest = sum(l.get("interest_fcfa", 0) for l in loans if l.get("status") == "REPAID")
    arpu = total_interest / max(total_users, 1)

    return {
        "users": {
            "total": total_users,
            "active_savers": active_savers,
            "conversion_rate": round(active_savers / max(total_users, 1) * 100, 1),
        },
        "savings": {
            "total_saved_fcfa": total_saved,
            "avg_per_user_fcfa": round(total_saved / max(active_savers, 1)),
            "active_triggers": len(triggers),
        },
        "credit": {
            "total_loans": total_loans,
            "total_disbursed_fcfa": total_disbursed,
            "repaid": repaid,
            "defaulted": defaulted,
            "npl_rate": round(npl_rate, 2),
            "npl_target": 12.0,
        },
        "growth": {
            "referrals": len(referrals),
            "viral_coefficient": round(len(referrals) / max(total_users, 1), 2),
            "arpu_fcfa": round(arpu),
        },
    }


@analytics_router.get("/analytics/leaderboard")
async def get_leaderboard(limit: int = 20):
    """Classement des meilleurs épargnants (gamification sociale)."""
    wallets = await db.select("wallets", {})
    users = await db.select("users", {})

    # Map user_id → display_name
    user_map = {u.get("id"): u for u in users}

    # Trier par total épargné
    ranked = sorted(wallets, key=lambda w: w.get("total_saved_fcfa", 0), reverse=True)[:limit]

    return [
        {
            "rank": i + 1,
            "display_name": user_map.get(w.get("user_id"), {}).get("display_name", "Anonyme"),
            "team": user_map.get(w.get("user_id"), {}).get("favorite_team_name", ""),
            "total_saved_fcfa": w.get("total_saved_fcfa", 0),
            "streak_days": w.get("current_streak_days", 0),
        }
        for i, w in enumerate(ranked)
    ]


@analytics_router.post("/analytics/track")
async def track_event(user_id: str, event_type: str, data: dict = {}):
    """Tracker un événement analytics."""
    await db.insert("analytics_events", {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "event_type": event_type,
        "event_data": data,
        "created_at": datetime.utcnow(),
    })
    return {"tracked": True, "event_type": event_type}


@analytics_router.get("/analytics/events/{user_id}")
async def get_user_events(user_id: str, limit: int = 50):
    """Événements analytics d'un utilisateur."""
    return await db.select(
        "analytics_events",
        {"user_id": user_id},
        order_by="-created_at",
        limit=limit,
    )
