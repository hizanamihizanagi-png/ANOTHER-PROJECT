"""
ScorAI — Sports Trigger Service.
Agent 03 : Détection d'événements sportifs et déclenchement automatique.

Ce service connecte les résultats sportifs en temps réel aux triggers
d'épargne configurés par les utilisateurs. Quand Arsenal gagne,
1000 FCFA sont automatiquement crédités virtuellement.

Workflow:
1. L'utilisateur configure un trigger: "Arsenal WIN → 1000 FCFA"
2. Le scheduler poll l'API Football toutes les 5 min les jours de match
3. Match terminé → l'événement est détecté → trigger fired
4. VirtualLedger.credit_virtual() est appelé pour chaque trigger matché
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import asdict
import uuid

from backend.core.database import db
from backend.core.config import settings, SUPPORTED_TRIGGER_EVENTS
from backend.models.schemas import (
    UserTrigger,
    TriggerEventType,
    TriggerStatus,
)


class SportsTriggerService:
    """
    Service de déclenchement sportif — Le moteur de dopamine.

    Utilise l'API Football (api-sports.io) pour surveiller les matchs
    et déclencher automatiquement les règles d'épargne des utilisateurs.
    """

    def __init__(self):
        self._processed_matches: set = set()  # Éviter le double-déclenchement

    # ============================================================
    # Configuration des Triggers
    # ============================================================

    async def create_trigger(
        self,
        user_id: str,
        team_id: int,
        team_name: str,
        event_type: str,
        amount_fcfa: int,
    ) -> Dict[str, Any]:
        """
        Créer un déclencheur d'épargne sportif.

        Ex: "Chaque fois qu'Arsenal (team_id=42) gagne (WIN), épargne 1000 FCFA"
        """
        # Validation
        if amount_fcfa < 100:
            return {"error": "Montant minimum: 100 FCFA"}
        if amount_fcfa > 10000:
            return {"error": "Montant maximum par trigger: 10 000 FCFA"}
        if event_type not in SUPPORTED_TRIGGER_EVENTS:
            return {"error": f"Événement non supporté. Choix: {SUPPORTED_TRIGGER_EVENTS}"}

        trigger = UserTrigger(
            user_id=user_id,
            team_id=team_id,
            team_name=team_name,
            event_type=TriggerEventType(event_type),
            amount_fcfa=amount_fcfa,
        )

        record = await db.insert("user_triggers", asdict(trigger))
        return {
            "trigger_id": record["id"],
            "team_name": team_name,
            "event": event_type,
            "amount_fcfa": amount_fcfa,
            "message": f"🎯 Trigger activé: {amount_fcfa} FCFA à chaque {event_type} de {team_name}!",
        }

    async def get_user_triggers(self, user_id: str) -> List[Dict[str, Any]]:
        """Récupérer tous les triggers actifs d'un utilisateur."""
        return await db.select(
            "user_triggers",
            {"user_id": user_id, "status": "ACTIVE"},
        )

    async def pause_trigger(self, trigger_id: str, user_id: str) -> Dict[str, Any]:
        """Mettre en pause un trigger."""
        result = await db.update(
            "user_triggers",
            {"id": trigger_id, "user_id": user_id},
            {"status": TriggerStatus.PAUSED.value},
        )
        return {"trigger_id": trigger_id, "status": "PAUSED"}

    async def delete_trigger(self, trigger_id: str, user_id: str) -> Dict[str, Any]:
        """Supprimer un trigger."""
        await db.update(
            "user_triggers",
            {"id": trigger_id, "user_id": user_id},
            {"status": TriggerStatus.DELETED.value},
        )
        return {"trigger_id": trigger_id, "status": "DELETED"}

    # ============================================================
    # Détection d'Événements (Scheduler)
    # ============================================================

    async def check_match_results(self) -> List[Dict[str, Any]]:
        """
        Vérifier les résultats de matchs récents et déclencher les triggers.

        Cette méthode est appelée par le scheduler toutes les 5 minutes
        les jours de match. En production, elle appelle l'API Football.
        Pour le MVP, on simule les résultats.

        Returns:
            Liste des triggers activés.
        """
        # Récupérer les matchs terminés récemment
        finished_matches = await self._fetch_recent_results()

        triggered_events = []

        for match in finished_matches:
            match_id = match["match_id"]

            # Éviter le double-déclenchement
            if match_id in self._processed_matches:
                continue

            # Détecter les événements
            events = self._extract_events(match)

            # Pour chaque événement, chercher les triggers correspondants
            for event in events:
                triggers_fired = await self._fire_triggers(event, match)
                triggered_events.extend(triggers_fired)

            self._processed_matches.add(match_id)

        return triggered_events

    async def _fetch_recent_results(self) -> List[Dict[str, Any]]:
        """
        Récupérer les résultats de matchs terminés.

        En production: appel à l'API Football (api-sports.io).
        En dev: données simulées.
        """
        # === SIMULATION pour le MVP ===
        # En production, remplacer par un appel HTTP à l'API Football
        # response = await httpx.get(
        #     f"{settings.FOOTBALL_API_URL}/fixtures",
        #     headers={"x-apisports-key": settings.FOOTBALL_API_KEY},
        #     params={"date": datetime.utcnow().strftime("%Y-%m-%d"), "status": "FT"}
        # )

        # Données simulées pour démonstration
        simulated_matches = [
            {
                "match_id": f"sim_{datetime.utcnow().strftime('%Y%m%d')}_001",
                "home_team_id": 42,    # Arsenal
                "home_team_name": "Arsenal",
                "away_team_id": 49,    # Chelsea
                "away_team_name": "Chelsea",
                "home_score": 2,
                "away_score": 1,
                "status": "FT",        # Full Time
                "date": datetime.utcnow().isoformat(),
            },
        ]

        return simulated_matches

    def _extract_events(self, match: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extraire les événements d'un match terminé.

        Un seul match peut générer plusieurs événements:
        - WIN pour le gagnant
        - GOAL pour chaque équipe ayant marqué
        - CLEAN_SHEET si une équipe n'a pas encaissé
        - DRAW si match nul
        """
        events = []
        home_score = match["home_score"]
        away_score = match["away_score"]

        # Win / Draw
        if home_score > away_score:
            events.append({
                "event_type": "WIN",
                "team_id": match["home_team_id"],
                "team_name": match["home_team_name"],
            })
        elif away_score > home_score:
            events.append({
                "event_type": "WIN",
                "team_id": match["away_team_id"],
                "team_name": match["away_team_name"],
            })
        else:
            events.append({
                "event_type": "DRAW",
                "team_id": match["home_team_id"],
                "team_name": match["home_team_name"],
            })
            events.append({
                "event_type": "DRAW",
                "team_id": match["away_team_id"],
                "team_name": match["away_team_name"],
            })

        # Goals
        if home_score > 0:
            events.append({
                "event_type": "GOAL",
                "team_id": match["home_team_id"],
                "team_name": match["home_team_name"],
            })
        if away_score > 0:
            events.append({
                "event_type": "GOAL",
                "team_id": match["away_team_id"],
                "team_name": match["away_team_name"],
            })

        # Clean Sheet
        if away_score == 0:
            events.append({
                "event_type": "CLEAN_SHEET",
                "team_id": match["home_team_id"],
                "team_name": match["home_team_name"],
            })
        if home_score == 0:
            events.append({
                "event_type": "CLEAN_SHEET",
                "team_id": match["away_team_id"],
                "team_name": match["away_team_name"],
            })

        return events

    async def _fire_triggers(
        self, event: Dict[str, Any], match: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Déclencher tous les triggers correspondant à un événement sportif.

        Cherche toutes les règles actives pour cette équipe + type d'événement,
        et crédite le Virtual Ledger de chaque utilisateur concerné.
        """
        from backend.services.virtual_ledger import virtual_ledger

        # Trouver tous les triggers actifs pour cette équipe + événement
        matching_triggers = await db.select(
            "user_triggers",
            {
                "team_id": event["team_id"],
                "event_type": event["event_type"],
                "status": "ACTIVE",
            },
        )

        results = []

        for trigger in matching_triggers:
            # Créditer le Virtual Ledger
            event_description = (
                f"{event['team_name']} {event['event_type']} "
                f"vs {match.get('away_team_name', 'Unknown')}"
            )

            credit_result = await virtual_ledger.credit_virtual(
                user_id=trigger["user_id"],
                amount_fcfa=trigger["amount_fcfa"],
                trigger_id=trigger["id"],
                trigger_event=event_description,
            )

            # Mettre à jour les stats du trigger
            await db.update(
                "user_triggers",
                {"id": trigger["id"]},
                {
                    "times_triggered": trigger.get("times_triggered", 0) + 1,
                    "total_saved_fcfa": trigger.get("total_saved_fcfa", 0) + trigger["amount_fcfa"],
                },
            )

            results.append({
                "trigger_id": trigger["id"],
                "user_id": trigger["user_id"],
                "team_name": event["team_name"],
                "event_type": event["event_type"],
                "amount_fcfa": trigger["amount_fcfa"],
                "credit_result": credit_result,
            })

        return results

    # ============================================================
    # Équipes Populaires (pour l'onboarding)
    # ============================================================

    def get_popular_teams(self) -> List[Dict[str, Any]]:
        """
        Retourne les équipes populaires pour le choix lors de l'onboarding.

        Calibré sur les préférences de la jeunesse camerounaise.
        """
        return [
            {"id": 42, "name": "Arsenal", "league": "Premier League", "logo": "🔴"},
            {"id": 50, "name": "Manchester City", "league": "Premier League", "logo": "🔵"},
            {"id": 85, "name": "Paris Saint-Germain", "league": "Ligue 1", "logo": "🔵🔴"},
            {"id": 541, "name": "Real Madrid", "league": "La Liga", "logo": "⚪"},
            {"id": 529, "name": "Barcelona", "league": "La Liga", "logo": "🔵🔴"},
            {"id": 40, "name": "Liverpool", "league": "Premier League", "logo": "🔴"},
            {"id": 33, "name": "Manchester United", "league": "Premier League", "logo": "🔴"},
            {"id": 496, "name": "Juventus", "league": "Serie A", "logo": "⚪⚫"},
            {"id": 157, "name": "Bayern Munich", "league": "Bundesliga", "logo": "🔴"},
            {"id": 49, "name": "Chelsea", "league": "Premier League", "logo": "🔵"},
            # Équipes africaines
            {"id": 838, "name": "Coton Sport FC", "league": "Elite One 🇨🇲", "logo": "🟢"},
            {"id": 839, "name": "Canon Yaoundé", "league": "Elite One 🇨🇲", "logo": "🟡🟢"},
        ]


# Singleton
sports_trigger = SportsTriggerService()
