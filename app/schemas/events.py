from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ClickIn(BaseModel):
    click_id: str
    campaign_id: str
    product_sku: str
    region_code: str
    user_hash: str | None = None
    click_price: float = Field(default=0, ge=0)
    clicked_at: datetime


class OrderIn(BaseModel):
    order_id: str
    marketplace: str
    product_sku: str
    region_code: str
    user_hash: str | None = None
    revenue: float = Field(default=0, ge=0)
    ordered_at: datetime


class AttributionOut(BaseModel):
    order_id: str
    click_id: str
    confidence: float
    strategy: str = "heuristic_v1"

    model_config = ConfigDict(from_attributes=True)
