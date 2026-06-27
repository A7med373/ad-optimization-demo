from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.attribution import Attribution
from app.models.click import AdClick
from app.models.order import MarketplaceOrder
from app.schemas.events import AttributionOut, ClickIn, OrderIn
from app.workers.tasks import attribute_pending_orders

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/events/clicks", status_code=201)
def ingest_click(payload: ClickIn, db: Session = Depends(get_db)) -> dict[str, str]:
    db.add(AdClick(**payload.model_dump()))
    db.commit()
    return {"status": "accepted", "click_id": payload.click_id}


@router.post("/events/orders", status_code=201)
def ingest_order(payload: OrderIn, db: Session = Depends(get_db)) -> dict[str, str]:
    db.add(MarketplaceOrder(**payload.model_dump()))
    db.commit()
    attribute_pending_orders.delay()
    return {"status": "accepted", "order_id": payload.order_id}


@router.get("/attributions", response_model=list[AttributionOut])
def list_attributions(db: Session = Depends(get_db)) -> list[Attribution]:
    return db.query(Attribution).order_by(Attribution.created_at.desc()).limit(100).all()

