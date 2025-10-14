"""Celery application instance for Redcrawl."""

from celery import Celery

app = Celery("redcrawl_job_handler")
app.config_from_object("jobs_engine.celeryconfig")

# Auto-discover tasks from package-local tasks module
app.autodiscover_tasks(["jobs_engine"])

