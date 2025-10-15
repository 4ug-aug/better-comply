# app/celery_app.py
from celery import Celery

app = Celery(
    "better-comply",
    broker="redis://redis:6379/0",     # or amqp://
    backend="redis://redis:6379/1",
    include=["backend.tasks.scheduler"],
)

# add to app.conf
# HA Redis
# app.conf["redbeat_redis_url"] = "redis://redis:6379/2"
# app.conf["beat_scheduler"] = "redbeat.RedBeatScheduler"


app.conf.update(
    timezone="UTC",
    enable_utc=True,
    worker_prefetch_multiplier=4,
    task_acks_late=True,
    task_time_limit=300,
    task_soft_time_limit=240,
    task_routes={
        "backend.tasks.scheduler.tick": {"queue": "control"},
    },
    beat_schedule={
        # One job that ticks often and lets the DB decide what is due
        "subs_tick": {
            "task": "backend.tasks.scheduler.tick",
            "schedule": 10.0,     # every 10s
            "options": {"queue": "control", "priority": 9},
        },
    },
)
