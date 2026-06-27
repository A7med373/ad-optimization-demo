from celery import Celery
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import SessionLocal, init_db
from app.models.attribution import Attribution
from app.models.click import AdClick
from app.models.order import MarketplaceOrder
from app.services.matching import find_best_click
from app.services.metrika import MetrikaOfflineConversionClient

settings = get_settings()

celery_app = Celery("ad_optimization", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.beat_schedule = {
    "attribute-orders-every-minute": {
        "task": "app.workers.tasks.attribute_pending_orders",
        "schedule": 60.0,
    },
    "export-conversions-every-minute": {
        "task": "app.workers.tasks.export_pending_conversions",
        "schedule": 60.0,
    },
}


@celery_app.task(name="app.workers.tasks.attribute_pending_orders")
def attribute_pending_orders() -> int:
    init_db()
    db: Session = SessionLocal()
    try:
        orders = db.query(MarketplaceOrder).limit(100).all()
        clicks = db.query(AdClick).limit(5000).all()
        created = 0

        for order in orders:
            existing = db.query(Attribution).filter(Attribution.order_id == order.order_id).first()
            if existing:
                continue

            match = find_best_click(
                order,
                clicks,
                window_hours=settings.attribution_window_hours,
                threshold=settings.match_threshold,
            )
            if not match:
                continue

            click, confidence = match
            db.add(Attribution(order_id=order.order_id, click_id=click.click_id, confidence=confidence))
            created += 1

        db.commit()
        return created
    finally:
        db.close()


@celery_app.task(name="app.workers.tasks.export_pending_conversions")
def export_pending_conversions() -> int:
    init_db()
    db: Session = SessionLocal()
    client = MetrikaOfflineConversionClient()
    try:
        rows = db.query(Attribution).filter(Attribution.exported_at.is_(None)).limit(100).all()
        for row in rows:
            client.export_conversion(row)
        return len(rows)
    finally:
        db.close()

