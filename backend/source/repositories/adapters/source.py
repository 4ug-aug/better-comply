from __future__ import annotations

from typing import Optional
from sqlalchemy import select

from models.source import Source

class SourcesAdapter:
    def __init__(self, db):
        self.db = db

    def list_sources(self, limit: int, offset: int) -> list[Source]:
        q = select(Source).order_by(Source.id.desc()).limit(limit).offset(offset)
        return self.db.execute(q).scalars().all()

    def get_source(self, source_id: int) -> Optional[Source]:
        return self.db.get(Source, source_id)

    def create_source(self, source: Source) -> Source:
        self.db.add(source)
        self.db.flush()
        return source

    def update_source(self, source_id: int, source: Source) -> Optional[Source]:
        existing_source = self.db.get(Source, source_id)
        if not existing_source:
            return None
        
        # Update fields
        for field in ['name', 'kind', 'base_url', 'auth_ref', 'robots_mode', 'rate_limit', 'enabled']:
            if hasattr(source, field):
                setattr(existing_source, field, getattr(source, field))
        
        self.db.flush()
        return existing_source

    def delete_source(self, source_id: int) -> bool:
        existing_source = self.db.get(Source, source_id)
        if not existing_source:
            return False
        
        self.db.delete(existing_source)
        self.db.flush()
        return True