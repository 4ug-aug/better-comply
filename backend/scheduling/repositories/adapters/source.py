from __future__ import annotations

from sqlalchemy import select

from models.source import Source

class SourcesAdapter:
    def __init__(self, db):
        self.db = db

    def list_sources(self, limit: int, offset: int) -> list[Source]:
        q = select(Source).order_by(Source.id.desc()).limit(limit).offset(offset)
        return self.db.execute(q).scalars().all()

    def get_source(self, source_id: int) -> Source:
        return self.db.get(Source, source_id)

    def create_source(self, source: Source) -> Source:
        self.db.add(source)
        self.db.flush()
        return source

    def update_source(self, source_id: int, source: Source) -> Source:
        self.db.merge(source)
        self.db.flush()
        return source