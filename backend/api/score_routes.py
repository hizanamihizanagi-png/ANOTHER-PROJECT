"""ScorAI — Credit Score API Routes."""

from fastapi import APIRouter

from backend.ml.scorai_model import scorai_model


score_router = APIRouter()


@score_router.get("/score/{user_id}")
async def get_score(user_id: str):
    """Calculer et retourner le ScorAI Trust Index."""
    return await scorai_model.predict(user_id)


@score_router.post("/score/train")
async def train_model():
    """Déclencher l'entraînement du modèle ML (admin)."""
    return await scorai_model.train()
