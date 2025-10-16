from __future__ import annotations

from typing import Protocol, Optional
from models.source import Source

class SourcesPort(Protocol):
    def list_sources(self, limit: int, offset: int) -> list[Source]:
        ...

    def get_source(self, source_id: int) -> Optional[Source]:
        ...

    def create_source(self, source: Source) -> Source:
        ...

    def update_source(self, source_id: int, source: Source) -> Optional[Source]:
        ...

    def delete_source(self, source_id: int) -> bool:
        ...

