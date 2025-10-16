from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List, Dict, Any

from database.sync import SessionLocalSync
from source.repositories.adapters.source import SourcesAdapter
from models.source import Source, SourceKind, RobotsMode


@dataclass
class SourceService:
    def list_sources(self, limit: int, offset: int) -> List[Dict[str, Any]]:
        with SessionLocalSync() as db:
            repo = SourcesAdapter(db)
            sources = repo.list_sources(limit=limit, offset=offset)
            return [self._source_to_dict(source) for source in sources]

    def get_source(self, source_id: int) -> Optional[Dict[str, Any]]:
        with SessionLocalSync() as db:
            repo = SourcesAdapter(db)
            source = repo.get_source(source_id)
            if not source:
                return None
            return self._source_to_dict(source)

    def create_source(self, data: Dict[str, Any]) -> Dict[str, Any]:
        with SessionLocalSync() as db:
            repo = SourcesAdapter(db)
            
            source = Source(
                name=data['name'],
                kind=SourceKind(data['kind']),
                base_url=data['base_url'],
                auth_ref=data.get('auth_ref'),
                robots_mode=RobotsMode(data.get('robots_mode', 'allow')),
                rate_limit=data.get('rate_limit', 60),
                enabled=data.get('enabled', True)
            )
            
            created_source = repo.create_source(source)
            db.commit()
            return self._source_to_dict(created_source)

    def update_source(self, source_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        with SessionLocalSync() as db:
            repo = SourcesAdapter(db)
            
            # Create a partial source object with only the fields to update
            update_data = {}
            if 'name' in data:
                update_data['name'] = data['name']
            if 'kind' in data:
                update_data['kind'] = SourceKind(data['kind'])
            if 'base_url' in data:
                update_data['base_url'] = data['base_url']
            if 'auth_ref' in data:
                update_data['auth_ref'] = data['auth_ref']
            if 'robots_mode' in data:
                update_data['robots_mode'] = RobotsMode(data['robots_mode'])
            if 'rate_limit' in data:
                update_data['rate_limit'] = data['rate_limit']
            if 'enabled' in data:
                update_data['enabled'] = data['enabled']
            
            # Create a temporary source object for the update
            temp_source = Source(**update_data)
            updated_source = repo.update_source(source_id, temp_source)
            
            if not updated_source:
                return None
            
            db.commit()
            return self._source_to_dict(updated_source)

    def delete_source(self, source_id: int) -> bool:
        with SessionLocalSync() as db:
            repo = SourcesAdapter(db)
            success = repo.delete_source(source_id)
            if success:
                db.commit()
            return success

    def _source_to_dict(self, source: Source) -> Dict[str, Any]:
        return {
            "id": source.id,
            "name": source.name,
            "kind": source.kind.value if hasattr(source.kind, 'value') else source.kind,
            "base_url": source.base_url,
            "auth_ref": source.auth_ref,
            "robots_mode": source.robots_mode.value if hasattr(source.robots_mode, 'value') else source.robots_mode,
            "rate_limit": source.rate_limit,
            "enabled": source.enabled,
            "created_at": source.created_at.isoformat() if source.created_at else None,
            "updated_at": source.updated_at.isoformat() if source.updated_at else None,
        }
