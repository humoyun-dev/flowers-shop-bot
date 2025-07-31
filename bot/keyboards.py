from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def contact_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Telefon raqamni yuborish", request_contact=True)]
        ],
        resize_keyboard=True
    )


def admin_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🆕 Mahsulot yaratish")],
            [KeyboardButton(text="📦 Mening mahsulotlarim")]
        ],
        resize_keyboard=True
    )


def cancel_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Bekor qilish")]
        ],
        resize_keyboard=True
    )


def product_inline_controls(product_id: int, has_next: bool, has_prev: bool) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="📝 Tahrirlash", callback_data=f"edit:{product_id}"),
            InlineKeyboardButton(text="❌ O‘chirish", callback_data=f"delete:{product_id}")
        ]
    ]

    nav_buttons = []
    if has_prev:
        nav_buttons.append(InlineKeyboardButton(text="◀️ Oldingisi", callback_data=f"prev:{product_id}"))
    if has_next:
        nav_buttons.append(InlineKeyboardButton(text="▶️ Keyingisi", callback_data=f"next:{product_id}"))
    if nav_buttons:
        buttons.append(nav_buttons)

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def skip_images_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⏭️ Davom etish")],
            [KeyboardButton(text="Bekor qilish")]
        ],
        resize_keyboard=True
    )
