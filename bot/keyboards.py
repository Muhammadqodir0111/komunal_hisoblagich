# Bot uchun barcha tugmalar shu yerda joylashgan


from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


def main_menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Ko'rsatkich yuborish")],
            [KeyboardButton(text="Mening hisoblarim")],
            [KeyboardButton(text="Qarzim")],
        ],
        resize_keyboard=True
    )


def nazoratchi_menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Tekshirilmagan ko'rsatkichlar")],
        ],
        resize_keyboard=True
    )


def meters_keyboard(meters):
    buttons = []
    for meter in meters:
        text = f"{meter['service']} - {meter['serial_number']}"
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"meter_{meter['id']}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def confirm_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Yuborish", callback_data="confirm_send"),
            InlineKeyboardButton(text="Bekor qilish", callback_data="confirm_cancel"),
        ]
    ])


def review_keyboard(reading_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"approve_{reading_id}"),
            InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_{reading_id}"),
        ]
    ])