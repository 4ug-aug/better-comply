"""JSON Patch RFC 6902 diff generation for document versions."""

import json
import logging
from typing import Any, Dict, List

import jsonpatch

logger = logging.getLogger(__name__)


def compute_json_patch_diff(old_doc: Dict[str, Any], new_doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Compute JSON Patch RFC 6902 diff between two documents.

    Args:
        old_doc: Previous version of parsed document (dict)
        new_doc: New version of parsed document (dict)

    Returns:
        List of RFC 6902 patch operations (op, path, value, etc.)

    Example:
        old = {"sections": [{"heading": "A"}]}
        new = {"sections": [{"heading": "B"}]}
        patch = compute_json_patch_diff(old, new)
        # Returns: [{"op": "replace", "path": "/sections/0/heading", "value": "B"}]
    """
    try:
        # Create JSON Patch from old to new
        patch = jsonpatch.JsonPatch.from_diff(old_doc, new_doc)

        # Convert to list of dicts for serialization
        operations = list(patch)

        logger.info(
            f"Computed JSON Patch diff: {len(operations)} operations "
            f"from {len(json.dumps(old_doc).encode())} bytes to "
            f"{len(json.dumps(new_doc).encode())} bytes"
        )

        return operations

    except Exception as e:
        logger.exception(f"Error computing JSON Patch diff: {e}")
        raise ValueError(f"Failed to compute diff: {e}")


def apply_json_patch(base_doc: Dict[str, Any], patch: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Apply JSON Patch RFC 6902 operations to a document.

    Useful for testing/validation.

    Args:
        base_doc: Base document to apply patch to
        patch: List of RFC 6902 patch operations

    Returns:
        Patched document

    Raises:
        ValueError: If patch cannot be applied
    """
    try:
        json_patch = jsonpatch.JsonPatch(patch)
        result = json_patch.apply(base_doc)
        logger.info(f"Applied JSON Patch: {len(patch)} operations")
        return result
    except Exception as e:
        logger.exception(f"Error applying JSON Patch: {e}")
        raise ValueError(f"Failed to apply patch: {e}")
