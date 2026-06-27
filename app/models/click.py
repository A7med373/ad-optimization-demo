from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AdClick(Base):
    __tablename__ = "ad_clicks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    click_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    campaign_id: Mapped[str] = mapped_column(String(128), index=True)
    product_sku: Mapped[str] = mapped_column(String(128), index=True)
    region_code: Mapped[str] = mapped_column(String(32), index=True)
    user_hash: Mapped[str | None] = mapped_column(String(128), index=True)
    click_price: Mapped[float] = mapped_column(Float, default=0.0)
    clicked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

