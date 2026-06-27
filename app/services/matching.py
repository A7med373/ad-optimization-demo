from datetime import timedelta
from typing import Iterable

from app.models.click import AdClick
from app.models.order import MarketplaceOrder


def score_click(order: MarketplaceOrder, click: AdClick, window_hours: int = 72) -> float:
    if click.clicked_at > order.ordered_at:
        return 0.0

    if order.ordered_at - click.clicked_at > timedelta(hours=window_hours):
        return 0.0

    score = 0.0

    if order.product_sku == click.product_sku:
        score += 0.45

    if order.region_code == click.region_code:
        score += 0.25

    if order.user_hash and click.user_hash and order.user_hash == click.user_hash:
        score += 0.20

    hours_delta = (order.ordered_at - click.clicked_at).total_seconds() / 3600
    recency_bonus = max(0.0, 0.10 * (1 - hours_delta / window_hours))

    return round(min(score + recency_bonus, 1.0), 4)


def find_best_click(
    order: MarketplaceOrder,
    clicks: Iterable[AdClick],
    window_hours: int = 72,
    threshold: float = 0.60,
) -> tuple[AdClick, float] | None:
    scored = [(click, score_click(order, click, window_hours)) for click in clicks]
    scored = [item for item in scored if item[1] >= threshold]

    if not scored:
        return None

    return max(scored, key=lambda item: item[1])

