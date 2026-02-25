"""ScorAI — Sports Trigger API Routes."""

from fastapi import APIRouter
from pydantic import BaseModel

from backend.services.sports_trigger import sports_trigger


trigger_router = APIRouter()


class CreateTriggerRequest(BaseModel):
    user_id: str
    team_id: int
    team_name: str
    event_type: str   # WIN, GOAL, CLEAN_SHEET, DRAW
    amount_fcfa: int


@trigger_router.post("/triggers/create")
async def create_trigger(req: CreateTriggerRequest):
    """Créer un déclencheur d'épargne sportif."""
    return await sports_trigger.create_trigger(
        user_id=req.user_id,
        team_id=req.team_id,
        team_name=req.team_name,
        event_type=req.event_type,
        amount_fcfa=req.amount_fcfa,
    )


@trigger_router.get("/triggers/mine/{user_id}")
async def get_my_triggers(user_id: str):
    """Récupérer mes triggers actifs."""
    return await sports_trigger.get_user_triggers(user_id)


@trigger_router.get("/triggers/teams")
async def get_teams():
    """Liste des équipes populaires pour l'onboarding."""
    return sports_trigger.get_popular_teams()


@trigger_router.post("/triggers/check-results")
async def check_results():
    """Vérifier les résultats de matchs et déclencher les triggers (scheduler)."""
    return await sports_trigger.check_match_results()


@trigger_router.put("/triggers/pause/{trigger_id}")
async def pause_trigger(trigger_id: str, user_id: str):
    """Mettre en pause un trigger."""
    return await sports_trigger.pause_trigger(trigger_id, user_id)


@trigger_router.delete("/triggers/{trigger_id}")
async def delete_trigger(trigger_id: str, user_id: str):
    """Supprimer un trigger."""
    return await sports_trigger.delete_trigger(trigger_id, user_id)
