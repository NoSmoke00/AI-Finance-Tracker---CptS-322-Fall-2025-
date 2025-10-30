from apscheduler.schedulers.background import BackgroundScheduler
from datetime import time
from app.database import SessionLocal
from app.services.insights_service import InsightsAI
from app.models import User


_scheduler: BackgroundScheduler | None = None


def _job_generate_all_users():
    db = SessionLocal()
    try:
        ai = InsightsAI()
        users = db.query(User).all()
        for u in users:
            try:
                ai.generate_insights_for_user(u.id, db)
            except Exception:
                continue
    finally:
        db.close()


def start_scheduler():
    global _scheduler
    if _scheduler is not None and _scheduler.running:
        return _scheduler
    scheduler = BackgroundScheduler()
    # Run daily at 06:00 UTC
    scheduler.add_job(_job_generate_all_users, 'cron', hour=6, minute=0)
    scheduler.start()
    _scheduler = scheduler
    return _scheduler


