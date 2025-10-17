from celery import Celery


app = Celery(
    "better-comply",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/1",
    include=[
        "tasks.scheduler",
        "tasks.compute_next_run",
        "tasks.outbox_dispatcher",
        "jobs_engine.tasks.crawl_tasks",
        "jobs_engine.tasks.run_status_tasks",
    ],
)

app.conf.update(
    task_routes={
        "tasks.scheduler.tick": {"queue": "control"},
        "tasks.compute_next_run.compute_next_run": {"queue": "control"},
        "tasks.outbox_dispatcher.dispatch_outbox": {"queue": "control"},
    },
    beat_schedule={
        "tick_due_subscriptions": {
            "task": "tasks.scheduler.tick",
            "schedule": 10.0,
            "options": {"queue": "control", "priority": 9},
        },
        "compute_next": {
            "task": "tasks.compute_next_run.compute_next_run",
            "schedule": 5.0,
            "options": {"queue": "control", "priority": 9},
        },
        "dispatch_outbox": {
            "task": "tasks.outbox_dispatcher.dispatch_outbox",
            "schedule": 2.0,
            "options": {"queue": "control", "priority": 9},
        },
    },
)


