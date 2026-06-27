import json
import time

from kafka import KafkaConsumer
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import SessionLocal, init_db
from app.models.click import AdClick
from app.models.order import MarketplaceOrder
from app.schemas.events import ClickIn, OrderIn

settings = get_settings()


def handle_message(db: Session, topic: str, payload: dict) -> None:
    if topic == settings.kafka_topic_clicks:
        event = ClickIn.model_validate(payload)
        db.add(AdClick(**event.model_dump()))
    elif topic == settings.kafka_topic_orders:
        event = OrderIn.model_validate(payload)
        db.add(MarketplaceOrder(**event.model_dump()))
    else:
        return

    db.commit()


def main() -> None:
    init_db()

    while True:
        try:
            consumer = KafkaConsumer(
                settings.kafka_topic_clicks,
                settings.kafka_topic_orders,
                bootstrap_servers=settings.kafka_bootstrap_servers,
                value_deserializer=lambda raw: json.loads(raw.decode("utf-8")),
                group_id="ad-optimization-demo",
                auto_offset_reset="earliest",
            )
            break
        except Exception:
            time.sleep(5)

    db = SessionLocal()
    try:
        for message in consumer:
            handle_message(db, message.topic, message.value)
    finally:
        db.close()


if __name__ == "__main__":
    main()

