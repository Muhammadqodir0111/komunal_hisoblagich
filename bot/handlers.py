# Botning barcha xabar va callback handlerlari shu yerda

from pathlib import Path
from aiogram.types import FSInputFile
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from datetime import datetime 

from .api_client import api_client
from .states import ReadingStates, RejectStates
from .keyboards import (
    main_menu_keyboard, nazoratchi_menu_keyboard,
    meters_keyboard, confirm_keyboard, review_keyboard
)
from .bot_config import BOT_API_USERNAME, BOT_API_PASSWORD

BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_ROOT = BASE_DIR / 'media'

router = Router()

async def ensure_login():
    if not api_client.token:
        await api_client.login(BOT_API_USERNAME, BOT_API_PASSWORD)

user_subscribers = {}


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()

    if not api_client.token:
        await api_client.login(BOT_API_USERNAME, BOT_API_PASSWORD)

    await message.answer(
        "Assalomu alaykum!\n\nHisob raqamingizni kiriting:"
    )
    await state.set_state(ReadingStates.waiting_account_number)


@router.message(ReadingStates.waiting_account_number)
async def process_account_number(message: Message, state: FSMContext):
    account_number = message.text.strip()

    result = await api_client.get_subscriber_by_account(account_number)
    subscribers = result.get('data', [])

    if not subscribers:
        await message.answer("Bunday hisob raqami topilmadi. Qaytadan urinib ko'ring:")
        return

    subscriber = subscribers[0]
    user_subscribers[message.from_user.id] = subscriber['id']

    await state.clear()
    await message.answer(
        f"Xush kelibsiz, {subscriber['full_name']}!",
        reply_markup=main_menu_keyboard()
    )


@router.message(F.text == "Ko'rsatkich yuborish")
async def start_reading(message: Message, state: FSMContext):
    subscriber_id = user_subscribers.get(message.from_user.id)

    if not subscriber_id:
        await message.answer("Avval /start bosing.")
        return

    result = await api_client.get_meters(subscriber_id)
    meters = result.get('data', [])

    active_meters = [m for m in meters if m['is_active']]

    if not active_meters:
        await message.answer("Sizda faol hisoblagich topilmadi.")
        return

    await message.answer(
        "Hisoblagichni tanlang:",
        reply_markup=meters_keyboard(active_meters)
    )
    await state.set_state(ReadingStates.choosing_meter)


@router.callback_query(F.data.startswith("meter_"))
async def choose_meter(callback: CallbackQuery, state: FSMContext):
    meter_id = int(callback.data.split("_")[1])
    await state.update_data(meter_id=meter_id)

    result = await api_client.get_last_reading(meter_id)
    readings = result.get('data', [])

    if readings:
        last_value = readings[-1]['value']
        await callback.message.answer(
            f"Oldingi ko'rsatkich: {last_value}\n\nYangi ko'rsatkichni kiriting:"
        )
    else:
        await callback.message.answer("Yangi ko'rsatkichni kiriting:")

    await state.set_state(ReadingStates.waiting_value)
    await callback.answer()


@router.message(ReadingStates.waiting_value)
async def process_value(message: Message, state: FSMContext):
    try:
        value = float(message.text.strip())
    except ValueError:
        await message.answer("Iltimos, faqat raqam kiriting:")
        return

    await state.update_data(value=value)
    await message.answer("Endi hisoblagich suratini yuboring:")
    await state.set_state(ReadingStates.waiting_photo)


@router.message(ReadingStates.waiting_photo, F.photo)
async def process_photo(message: Message, state: FSMContext):
    photo = message.photo[-1]
    await state.update_data(photo_file_id=photo.file_id)

    data = await state.get_data()

    text = (
        f"Tekshiring:\n\n"
        f"Yangi ko'rsatkich: {data['value']}\n\n"
        f"To'g'rimi?"
    )
    await message.answer_photo(photo.file_id, caption=text, reply_markup=confirm_keyboard())
    await state.set_state(ReadingStates.confirming)


@router.message(ReadingStates.waiting_photo)
async def wrong_photo(message: Message):
    await message.answer("Iltimos, surat yuboring (hujjat sifatida emas).")


@router.callback_query(F.data == "confirm_cancel")
async def cancel_reading(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Bekor qilindi.", reply_markup=main_menu_keyboard())
    await callback.answer()


@router.callback_query(F.data == "confirm_send")
async def send_reading(callback: CallbackQuery, state: FSMContext, bot):
    await callback.answer()

    data = await state.get_data()

    file = await bot.get_file(data['photo_file_id'])
    photo_bytes = await bot.download_file(file.file_path)

    period = datetime.now().strftime("%Y-%m")

    result = await api_client.submit_reading(
        meter_id=data['meter_id'],
        period=period,
        value=data['value'],
        photo_bytes=photo_bytes.read(),
        filename="reading.jpg"
    )

    await state.clear()

    if result.get('success'):
        await callback.message.answer(
            "Qabul qilindi, nazoratchi tekshirgach hisob chiqadi.",
            reply_markup=main_menu_keyboard()
        )
    else:
        error_text = str(result)
        await callback.message.answer(
            f"Xatolik yuz berdi:\n{error_text}",
            reply_markup=main_menu_keyboard()
        )

@router.message(F.text == "Mening hisoblarim")
async def my_invoices(message: Message):
    subscriber_id = user_subscribers.get(message.from_user.id)
    if not subscriber_id:
        await message.answer("Avval /start bosing.")
        return

    result = await api_client.get_my_invoices(subscriber_id)
    data = result.get('data', {})
    invoices = data.get('invoices', [])

    if not invoices:
        await message.answer("Hisoblar topilmadi.")
        return

    text = "Oxirgi hisoblaringiz:\n\n"
    for inv in invoices:
        paid_text = "To'langan" if inv['is_paid'] else "To'lanmagan"
        text += f"{inv['period']}: {inv['consumption']} birlik - {inv['amount']} so'm ({paid_text})\n"

    await message.answer(text)


@router.message(F.text == "Qarzim")
async def my_debt(message: Message):
    subscriber_id = user_subscribers.get(message.from_user.id)
    if not subscriber_id:
        await message.answer("Avval /start bosing.")
        return

    result = await api_client.get_my_invoices(subscriber_id)
    data = result.get('data', {})
    debt = data.get('total_debt', 0)

    if debt and float(debt) > 0:
        await message.answer(f"Sizning umumiy qarzingiz: {debt} so'm")
    else:
        await message.answer("Sizda qarz yo'q.")


@router.message(F.text == "/nazoratchi")
async def nazoratchi_panel(message: Message):
    await message.answer(
        "Nazoratchi paneli",
        reply_markup=nazoratchi_menu_keyboard()
    )


@router.message(F.text == "Tekshirilmagan ko'rsatkichlar")
async def pending_readings(message: Message):
    await ensure_login()
    result = await api_client.get_pending_readings()
    readings = result.get('data', [])

    if not readings:
        await message.answer("Tekshirilmagan ko'rsatkichlar yo'q.")
        return

    for reading in readings:
        text = (
            f"Davr: {reading['period']}\n"
            f"Ko'rsatkich: {reading['value']}\n"
            f"Meter ID: {reading['meter']}"
        )
        photo_path = reading.get('photo')

        if photo_path:
            relative_path = photo_path.split('/media/')[-1]
            file_path = MEDIA_ROOT / relative_path

            if file_path.exists():
                photo_file = FSInputFile(str(file_path))
                await message.answer_photo(
                    photo_file,
                    caption=text,
                    reply_markup=review_keyboard(reading['id'])
                )
            else:
                await message.answer(
                    text + "\n\n(surat topilmadi)",
                    reply_markup=review_keyboard(reading['id'])
                )
        else:
            await message.answer(text, reply_markup=review_keyboard(reading['id']))

@router.callback_query(F.data.startswith("approve_"))
async def approve_callback(callback: CallbackQuery):
    await callback.answer()

    reading_id = int(callback.data.split("_")[1])
    result = await api_client.approve_reading(reading_id)

    if result.get('success'):
        await callback.message.answer("Tasdiqlandi, hisob chiqarildi.")
    else:
        await callback.message.answer(f"Xatolik: {result}")


@router.callback_query(F.data.startswith("reject_"))
async def reject_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    reading_id = int(callback.data.split("_")[1])
    await state.update_data(reject_reading_id=reading_id)
    await callback.message.answer("Rad etish sababini yozing:")
    await state.set_state(RejectStates.waiting_reason)


@router.message(RejectStates.waiting_reason)
async def reject_reason(message: Message, state: FSMContext):
    data = await state.get_data()
    reading_id = data['reject_reading_id']

    result = await api_client.reject_reading(reading_id, message.text)

    await state.clear()

    if result.get('success'):
        await message.answer("Rad etildi.")
    else:
        await message.answer(f"Xatolik: {result}")