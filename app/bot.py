from app.core.config import get_settings
from app.db.session import SessionLocal, init_db
from app.models.attribution import Attribution
from app.models.click import AdClick
from app.models.order import MarketplaceOrder
from app.services.matching import find_best_click
from sqlalchemy import func
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

settings = get_settings()


def _stats() -> dict[str, int]:
    db = SessionLocal()
    try:
        return {
            "clicks": db.query(func.count(AdClick.id)).scalar() or 0,
            "orders": db.query(func.count(MarketplaceOrder.id)).scalar() or 0,
            "attributions": db.query(func.count(Attribution.id)).scalar() or 0,
        }
    finally:
        db.close()


def _is_admin(update: Update) -> bool:
    chat = update.effective_chat
    return bool(chat and chat.id == settings.telegram_admin_chat_id)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Ad Optimization Demo\n"
        "/summary - статистика\n"
        "/recompute - пересчитать матчинги"
    )


async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    stats = _stats()
    await update.message.reply_text(
        "Статистика\n"
        f"Кликов: {stats['clicks']}\n"
        f"Заказов: {stats['orders']}\n"
        f"Матчингов: {stats['attributions']}\n"
        f"Порог: {settings.match_threshold:.2f}"
    )


async def recompute(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_admin(update):
        await update.message.reply_text("Недостаточно прав.")
        return

    db = SessionLocal()
    try:
        orders = db.query(MarketplaceOrder).all()
        clicks = db.query(AdClick).all()
        created = 0

        for order in orders:
            existing = db.query(Attribution).filter(Attribution.order_id == order.order_id).first()
            if existing is not None:
                continue

            match = find_best_click(order, clicks, window_hours=settings.attribution_window_hours)
            if match is None:
                continue

            click, confidence = match
            db.add(Attribution(order_id=order.order_id, click_id=click.click_id, confidence=confidence))
            created += 1

        db.commit()
    finally:
        db.close()

    await update.message.reply_text(f"Пересчитано матчингов: {created}")


def main() -> None:
    init_db()
    application = Application.builder().token(settings.telegram_bot_token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("summary", summary))
    application.add_handler(CommandHandler("recompute", recompute))
    application.run_polling()


if __name__ == "__main__":
    main()
