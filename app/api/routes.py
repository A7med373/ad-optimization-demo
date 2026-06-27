from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.attribution import Attribution
from app.models.click import AdClick
from app.models.order import MarketplaceOrder
from app.schemas.events import AttributionOut, ClickIn, OrderIn
from app.services.matching import find_best_click

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
    order = MarketplaceOrder(**payload.model_dump())
    db.add(order)
    db.flush()

    match = find_best_click(order, db.query(AdClick).all())
    if match is not None:
        click, confidence = match
        existing = db.query(Attribution).filter(Attribution.order_id == order.order_id).first()
        if existing is None:
            db.add(
                Attribution(
                    order_id=order.order_id,
                    click_id=click.click_id,
                    confidence=confidence,
                )
            )

    db.commit()
    return {"status": "accepted", "order_id": payload.order_id}


@router.post("/attributions/recompute")
def recompute_attributions(db: Session = Depends(get_db)) -> dict[str, int]:
    orders = db.query(MarketplaceOrder).all()
    clicks = db.query(AdClick).all()
    created = 0

    for order in orders:
        existing = db.query(Attribution).filter(Attribution.order_id == order.order_id).first()
        if existing is not None:
            continue

        match = find_best_click(order, clicks)
        if match is None:
            continue

        click, confidence = match
        db.add(Attribution(order_id=order.order_id, click_id=click.click_id, confidence=confidence))
        created += 1

    db.commit()
    return {"created": created}


@router.get("/attributions", response_model=list[AttributionOut])
def list_attributions(db: Session = Depends(get_db)) -> list[Attribution]:
    return db.query(Attribution).order_by(Attribution.created_at.desc()).limit(100).all()
