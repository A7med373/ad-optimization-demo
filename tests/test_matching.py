from datetime import datetime, timedelta, timezone

from app.models.click import AdClick
from app.models.order import MarketplaceOrder
from app.services.matching import find_best_click, score_click


def test_score_click_prefers_same_sku_region_and_user() -> None:
    now = datetime.now(timezone.utc)
    order = MarketplaceOrder(
        order_id="order-1",
        marketplace="wildberries",
        product_sku="sku-1",
        region_code="RU-MOW",
        user_hash="user-1",
        revenue=5000,
        ordered_at=now,
    )
    click = AdClick(
        click_id="click-1",
        campaign_id="campaign-1",
        product_sku="sku-1",
        region_code="RU-MOW",
        user_hash="user-1",
        click_price=10,
        clicked_at=now - timedelta(hours=4),
    )

    assert score_click(order, click) >= 0.9


def test_find_best_click_respects_threshold() -> None:
    now = datetime.now(timezone.utc)
    order = MarketplaceOrder(
        order_id="order-1",
        marketplace="ozon",
        product_sku="sku-1",
        region_code="RU-MOW",
        user_hash="user-1",
        revenue=5000,
        ordered_at=now,
    )
    weak_click = AdClick(
        click_id="click-weak",
        campaign_id="campaign-1",
        product_sku="sku-2",
        region_code="RU-SPE",
        user_hash="user-2",
        click_price=10,
        clicked_at=now - timedelta(hours=4),
    )

    assert find_best_click(order, [weak_click], threshold=0.6) is None

