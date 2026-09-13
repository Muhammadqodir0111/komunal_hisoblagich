# Avtomatik eslatma va ogohlantirish vazifalari
from celery import shared_task
import asyncio
from datetime import datetime
from aiogram import Bot

from .bot_config import BOT_TOKEN
from subscribers.models import Meter
from billing.models import Reading, Invoice


async def _send_message(telegram_id, text):
    bot = Bot(token=BOT_TOKEN)
    try:
        await bot.send_message(telegram_id, text)
    except Exception:
        pass
    await bot.session.close()


def _get_unsent_subscribers(period):
    meters = Meter.objects.filter(is_active=True).select_related('subscriber__user')
    unsent = []
    for meter in meters:
        has_reading = Reading.objects.filter(meter=meter, period=period).exists()
        if not has_reading:
            user = getattr(meter.subscriber, 'user', None)
            if user and user.telegram_id:
                unsent.append(user.telegram_id)
    return list(set(unsent))


@shared_task
def send_reading_reminder():
    period = datetime.now().strftime("%Y-%m")
    telegram_ids = _get_unsent_subscribers(period)

    for tg_id in telegram_ids:
        asyncio.run(_send_message(
            tg_id,
            f"Eslatma: {period} oyi uchun hisoblagich ko'rsatkichini hali yubormadingiz."
        ))

    return f"{len(telegram_ids)} ta abonentga eslatma yuborildi"


@shared_task
def send_debt_warning():
    debtors = Invoice.objects.filter(is_paid=False).select_related('subscriber__user')
    warned = 0

    for invoice in debtors:
        user = getattr(invoice.subscriber, 'user', None)
        if user and user.telegram_id:
            asyncio.run(_send_message(
                user.telegram_id,
                f"Sizda to'lanmagan qarz bor: {invoice.period} oyi uchun {invoice.amount} so'm."
            ))
            warned += 1

    return f"{warned} ta abonentga qarz haqida ogohlantirish yuborildi"