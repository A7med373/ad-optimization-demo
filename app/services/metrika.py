from app.core.config import get_settings
from app.models.attribution import Attribution


class MetrikaOfflineConversionClient:
    """Demo adapter. Production code would batch and retry calls to Yandex Metrika."""

    def __init__(self) -> None:
        self.settings = get_settings()

    def export_conversion(self, attribution: Attribution) -> dict[str, str | float]:
        return {
            "counter_id": self.settings.yandex_metrika_counter_id,
            "click_id": attribution.click_id,
            "order_id": attribution.order_id,
            "confidence": attribution.confidence,
            "status": "queued_for_demo",
        }

