from __future__ import annotations

from typing import Protocol, List, Optional, Dict, Any


class QueriesPort(Protocol):
    def list_subscriptions(self, status: Optional[str], limit: int, offset: int) -> List[Dict[str, Any]]:
        ...

    def list_runs(self, limit: int, offset: int) -> List[Dict[str, Any]]:
        ...

    def list_outbox(self, status: Optional[str], limit: int, offset: int) -> List[Dict[str, Any]]:
        ...


