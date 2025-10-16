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
    ],
)

app.conf.update(
    timezone="UTC",
    enable_utc=True,
    worker_prefetch_multiplier=4,
    task_acks_late=True,
    task_time_limit=300,
    task_soft_time_limit=240,
    beat_max_loop_interval=10.0,
    task_routes={
        "tasks.scheduler.tick": {"queue": "control"},
        "tasks.compute_next_run.compute_next_run": {"queue": "control"},
        "tasks.outbox_dispatcher.dispatch_outbox": {"queue": "control"},
        "jobs_engine.tasks.crawl_tasks.handle_subscription_scheduled": {"queue": "jobs"},
        "jobs_engine.tasks.crawl_tasks.crawl_url": {"queue": "jobs"},
        "jobs_engine.tasks.crawl_tasks.parse_crawled_content": {"queue": "jobs"},
        "jobs_engine.tasks.crawl_tasks.version_document": {"queue": "jobs"},
        "jobs_engine.tasks.crawl_tasks.deliver_document": {"queue": "jobs"},
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


