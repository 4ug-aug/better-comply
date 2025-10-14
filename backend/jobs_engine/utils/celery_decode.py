"""Utility for decoding Celery binary blobs (args, kwargs, result)."""

import json
import pickle
import zlib
from typing import Any, Optional


def decode_celery_blob(blob: Optional[bytes]) -> Optional[Any]:
    """Decode a Celery binary blob using multiple strategies.
    
    Args:
        blob: Binary data from Celery's args/kwargs/result columns
        
    Returns:
        Decoded Python object or None if decoding fails
    """
    if not blob:
        return None
    
    # Try different decoding strategies in order of likelihood
    for attempt in (
        lambda b: json.loads(b.decode("utf-8")),
        lambda b: pickle.loads(b),
        lambda b: pickle.loads(zlib.decompress(b)),
    ):
        try:
            return attempt(blob)
        except Exception:
            pass
    
    return None
