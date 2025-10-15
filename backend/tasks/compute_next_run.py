from celery import shared_task
from backend.database.connection import SessionLocal

@shared_task
def compute_next_run():
    from croniter import croniter
    from sqlalchemy import text
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        rows = db.execute(text("""
          SELECT id, cron_expr, coalesce(last_run_at, :now) AS base
          FROM subscription
          WHERE next_run_at IS NULL AND enabled = true
          LIMIT 500
        """), {"now": now}).mappings().all()

        for r in rows:
            itr = croniter(r["cron_expr"], r["base"])
            nxt = itr.get_next(datetime)
            db.execute(text("UPDATE subscription SET next_run_at=:nxt WHERE id=:id"),
                       {"nxt": nxt, "id": r["id"]})
        db.commit()
