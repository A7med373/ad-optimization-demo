from datetime import datetime, timedelta, timezone

from app.db.session import SessionLocal, init_db
from app.models.click import AdClick
from app.models.order import MarketplaceOrder


def main() -> None:
    init_db()
    db = SessionLocal()
    now = datetime.now(timezone.utc)

    clicks = [
        AdClick(
            click_id="yclid-demo-001",
            campaign_id="brand-search",
            product_sku="WB-DRYER-100",
            region_code="RU-MOW",
            user_hash="u-42",
            click_price=18.4,
            clicked_at=now - timedelta(hours=8),
        ),
        AdClick(
            click_id="yclid-demo-002",
            campaign_id="category-performance",
            product_sku="WB-IRON-200",
            region_code="RU-SPE",
            user_hash="u-99",
            click_price=12.1,
            clicked_at=now - timedelta(hours=18),
        ),
    ]

    orders = [
        MarketplaceOrder(
            order_id="wb-order-demo-001",
            marketplace="wildberries",
            product_sku="WB-DRYER-100",
            region_code="RU-MOW",
            user_hash="u-42",
            revenue=5290,
            ordered_at=now,
        ),
        MarketplaceOrder(
            order_id="ozon-order-demo-002",
            marketplace="ozon",
            product_sku="WB-IRON-200",
            region_code="RU-SPE",
            user_hash="u-99",
            revenue=3190,
            ordered_at=now - timedelta(hours=2),
        ),
    ]

    db.add_all(clicks + orders)
    db.commit()
    db.close()
    print("Seeded demo clicks and orders")


if __name__ == "__main__":
    main()

