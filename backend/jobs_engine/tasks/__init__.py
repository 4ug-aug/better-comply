"""Task package initializer.

Import submodules so Celery decorators execute at import time and task
registrations/logging occur during worker startup.
"""

# Import task modules to trigger decorator registration
from . import _example  # noqa: F401


