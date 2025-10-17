from __future__ import annotations

from typing import List, Dict, Any
from database.sync import SessionLocalSync
from scheduling.repositories.adapters.queries import QueriesAdapter


class ObservabilityService:
    """Service for querying observability data (outbox and runs)."""

    def get_recent_outbox(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch recent outbox entries.
        
        Args:
            limit: Maximum number of entries to fetch
            
        Returns:
            List of outbox entries with id, status, event_type, created_at, attempts
        """
        with SessionLocalSync() as db:
            queries = QueriesAdapter(db)
            return queries.list_outbox(status=None, limit=limit, offset=0)

    def get_recent_runs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch recent runs.
        
        Args:
            limit: Maximum number of runs to fetch
            
        Returns:
            List of runs with id, status, run_kind, subscription_id, started_at, ended_at
        """
        with SessionLocalSync() as db:
            queries = QueriesAdapter(db)
            return queries.list_runs(limit=limit, offset=0)

    def get_observability_snapshot(self, limit: int = 50) -> Dict[str, Any]:
        """Get a snapshot of both outbox and runs data.
        
        Args:
            limit: Maximum number of entries for each type
            
        Returns:
            Dictionary with 'outbox' and 'runs' keys containing lists of entries
        """
        return {
            "outbox": self.get_recent_outbox(limit),
            "runs": self.get_recent_runs(limit),
        }
