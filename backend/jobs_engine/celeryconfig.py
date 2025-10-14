"""Celery configuration for Redcrawl.

Note: Celery uses Redis for task queues, while Kafka is used for
event streaming (domain events). This provides clean separation:
- Events (domain events) → Kafka → Consumer → Trigger Tasks
- Tasks (work units) → Redis → Celery Worker → Execute
"""

import os

# Redis broker for Celery task queues
redis_host = os.getenv("REDIS_HOST", "redis")
redis_port = os.getenv("REDIS_PORT", "6379")
broker_url = f"redis://{redis_host}:{redis_port}/0"

# Task serialization
task_serializer = "json"
accept_content = ["json"]
result_serializer = "json"

# Broker connection settings
broker_connection_retry_on_startup = True

POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'postgres')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'testdb')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'testuser')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'testpassword')

# Result backend (using PostgreSQL for persistence)
result_backend = f"db+postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Worker settings
worker_prefetch_multiplier = 1
worker_max_tasks_per_child = 1000

worker_pool = "solo"  # Use solo pool for better async support

# Task result settings
result_expires = 604800  # 7 days (was 1 hour)
result_extended = True
task_always_eager = False


# Timezone
timezone = "UTC"
enable_utc = True

# Logging
worker_log_format = "%(asctime)s %(levelname)s %(name)s - %(message)s"
worker_task_log_format = "%(asctime)s %(levelname)s %(task_name)s[%(task_id)s] - %(message)s"
worker_hijack_root_logger = False
worker_redirect_stdouts = True
worker_redirect_stdouts_level = "INFO"
