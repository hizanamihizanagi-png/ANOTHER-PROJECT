"""
ScorAI — Database Layer (Supabase Client).
Connexion centralisée à Supabase pour toutes les opérations CRUD.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import json


class SupabaseClient:
    """
    Client Supabase centralisé pour ScorAI.
    Encapsule toutes les opérations de base de données.

    En production, utilise le SDK supabase-py.
    En développement, utilise un store in-memory pour les tests.
    """

    def __init__(self, url: str = "", key: str = "", use_memory: bool = True):
        self.url = url
        self.key = key
        self.use_memory = use_memory

        # In-memory store pour développement/tests
        self._store: Dict[str, List[Dict[str, Any]]] = {
            "users": [],
            "wallets": [],
            "virtual_transactions": [],
            "batch_settlements": [],
            "user_triggers": [],
            "credit_scores": [],
            "loans": [],
            "kyc_records": [],
            "analytics_events": [],
            "referrals": [],
        }

    # ============================================================
    # CRUD Operations
    # ============================================================

    async def insert(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insérer un enregistrement dans une table."""
        if self.use_memory:
            # Sérialiser les datetimes et enums
            serialized = self._serialize(data)
            self._store.setdefault(table, []).append(serialized)
            return serialized
        # TODO: Supabase SDK call
        # return self.client.table(table).insert(data).execute().data[0]
        raise NotImplementedError("Supabase SDK not yet configured")

    async def select(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Sélectionner des enregistrements avec filtres optionnels."""
        if self.use_memory:
            results = self._store.get(table, [])
            if filters:
                for key, value in filters.items():
                    results = [r for r in results if r.get(key) == value]
            if order_by:
                desc = order_by.startswith("-")
                field_name = order_by.lstrip("-")
                results = sorted(
                    results,
                    key=lambda x: x.get(field_name, ""),
                    reverse=desc,
                )
            if limit:
                results = results[:limit]
            return results
        raise NotImplementedError("Supabase SDK not yet configured")

    async def select_one(
        self, table: str, filters: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Sélectionner un seul enregistrement."""
        results = await self.select(table, filters, limit=1)
        return results[0] if results else None

    async def update(
        self, table: str, filters: Dict[str, Any], data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Mettre à jour des enregistrements correspondant aux filtres."""
        if self.use_memory:
            updated = []
            serialized = self._serialize(data)
            for record in self._store.get(table, []):
                if all(record.get(k) == v for k, v in filters.items()):
                    record.update(serialized)
                    updated.append(record)
            return updated
        raise NotImplementedError("Supabase SDK not yet configured")

    async def delete(self, table: str, filters: Dict[str, Any]) -> int:
        """Supprimer des enregistrements correspondant aux filtres."""
        if self.use_memory:
            before = len(self._store.get(table, []))
            self._store[table] = [
                r
                for r in self._store.get(table, [])
                if not all(r.get(k) == v for k, v in filters.items())
            ]
            return before - len(self._store[table])
        raise NotImplementedError("Supabase SDK not yet configured")

    async def count(self, table: str, filters: Optional[Dict[str, Any]] = None) -> int:
        """Compter les enregistrements."""
        results = await self.select(table, filters)
        return len(results)

    async def aggregate_sum(
        self, table: str, field: str, filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """Somme d'un champ numérique."""
        results = await self.select(table, filters)
        return sum(r.get(field, 0) for r in results)

    # ============================================================
    # Helpers
    # ============================================================

    def _serialize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sérialiser les types Python complexes pour le stockage."""
        result = {}
        for key, value in data.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            elif hasattr(value, "value"):  # Enum
                result[key] = value.value
            else:
                result[key] = value
        return result

    def reset(self):
        """Reset le store in-memory (pour les tests)."""
        for table in self._store:
            self._store[table] = []


# ============================================================
# Singleton Database Instance
# ============================================================

db = SupabaseClient(use_memory=True)
