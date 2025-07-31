import json
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import get_db
from models import Product
from aiogram.filters import StateFilter
from aiogram.types import InputMediaPhoto
from keyboards import admin_menu, skip_images_keyboard , cancel_keyboard, product_inline_controls
from sqlalchemy import select
from aiogram.types import CallbackQuery
from aiogram import F

router = Router()

product_pages = {}
product_indices = {}


class ProductCreation(StatesGroup):
    WAITING_FOR_IMAGES = State()
    WAITING_FOR_PRICE = State()
    WAITING_FOR_QUANTITY = State()

@router.message(lambda m: m.text == "🆕 Mahsulot yaratish")
async def start_creation(message: Message, state: FSMContext):
    await state.set_state(ProductCreation.WAITING_FOR_IMAGES)
    await state.update_data(images=[])
    await message.answer(
        "Ixtiyoriy rasmlarni yuboring (3 tagacha). Davom etish uchun pastdagi tugmani bosing.",
        reply_markup=skip_images_keyboard()
    )

@router.message(StateFilter(ProductCreation.WAITING_FOR_IMAGES))
async def collect_images(message: Message, state: FSMContext):
    if message.text == "⏭️ Davom etish":
        await state.set_state(ProductCreation.WAITING_FOR_PRICE)
        return await message.answer("Rasmlarsiz davom etyapmiz. Endi mahsulot narxini kiriting.")

    if not message.photo:
        return await message.answer("Iltimos, rasm yuboring yoki \"⏭️ Davom etish\" tugmasini bosing.")

    data = await state.get_data()
    images = data.get("images", [])
    images.append(message.photo[-1].file_id)
    await state.update_data(images=images)

    if len(images) >= 3:
        await state.set_state(ProductCreation.WAITING_FOR_PRICE)
        return await message.answer("3 ta rasm qabul qilindi. Endi mahsulot narxini kiriting.")

    return await message.answer(f"{len(images)} rasm qabul qilindi. Yana yuboring yoki \"⏭️ Davom etish\" tugmasini bosing.")

@router.message(ProductCreation.WAITING_FOR_PRICE)
async def collect_price(message: Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("Iltimos, faqat son kiriting.")
    await state.update_data(price=float(message.text))
    await state.set_state(ProductCreation.WAITING_FOR_QUANTITY)
    await message.answer("Mahsulot sonini kiriting.")

@router.message(StateFilter(ProductCreation.WAITING_FOR_QUANTITY))
async def collect_quantity(message: Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("Iltimos, faqat son kiriting.")

    data = await state.get_data()
    quantity = int(message.text)
    images = data.get("images", [])
    price = data["price"]
    user_id = message.from_user.id

    async for db in get_db():
        new_product = Product(
            images=json.dumps(images),
            price=price,
            quantity=quantity,
            created_by=user_id
        )
        db.add(new_product)
        await db.commit()
        await db.refresh(new_product)

    caption = (
        "🆕 <b>Yangi mahsulot tayyor:</b>\n"
        f"💰 <b>Narxi:</b> {price}\n"
        f"📦 <b>Soni:</b> {quantity}\n"
        f"👤 <b>Yaratgan:</b> @{message.from_user.username or 'Noma’lum'}"
    )

    media = []
    if images:
        for idx, file_id in enumerate(images):
            if idx == 0:
                media.append(InputMediaPhoto(media=file_id, caption=caption, parse_mode="HTML"))
            else:
                media.append(InputMediaPhoto(media=file_id))
        await message.answer_media_group(media=media)
    else:
        await message.answer(caption, parse_mode="HTML")

    await message.answer("Mahsulot muvaffaqiyatli yaratildi!", reply_markup=admin_menu())
    await state.clear()



@router.message(lambda m: m.text == "📦 Mening mahsulotlarim")
async def show_my_products(message: Message):
    user_id = message.from_user.id
    async for db in get_db():
        result = await db.execute(select(Product).filter_by(created_by=user_id))
        products = result.scalars().all()

    if not products:
        return await message.answer("Sizda hozircha hech qanday mahsulot yo'q.", reply_markup=admin_menu())

    product_pages[user_id] = products
    product_indices[user_id] = 0
    await send_product_page(message, user_id, 0)

async def send_product_page(event, user_id: int, index: int):
    products = product_pages[user_id]
    product_indices[user_id] = index
    product = products[index]
    images = json.loads(product.images)

    caption = (
        f"🆔 <b>ID:</b> {product.id}\n"
        f"💰 <b>Narxi:</b> {product.price}\n"
        f"📦 <b>Soni:</b> {product.quantity}\n"
        f"📅 <b>Yaratilgan:</b> {product.created_at.strftime('%Y-%m-%d')}"
    )

    has_prev = index > 0
    has_next = index < len(products) - 1

    if isinstance(event, Message):
        await event.answer_photo(photo=images[0], caption=caption, parse_mode="HTML",
                                 reply_markup=product_inline_controls(product.id, has_next, has_prev))
    else:
        await event.message.edit_media(
            media=InputMediaPhoto(media=images[0], caption=caption, parse_mode="HTML"),
            reply_markup=product_inline_controls(product.id, has_next, has_prev)
        )

@router.callback_query(F.data.startswith("next:"))
async def show_next_product(callback: CallbackQuery):
    user_id = callback.from_user.id
    index = product_indices.get(user_id, 0)
    if user_id in product_pages and index + 1 < len(product_pages[user_id]):
        await send_product_page(callback, user_id, index + 1)
    await callback.answer()

@router.callback_query(F.data.startswith("prev:"))
async def show_prev_product(callback: CallbackQuery):
    user_id = callback.from_user.id
    index = product_indices.get(user_id, 0)
    if user_id in product_pages and index - 1 >= 0:
        await send_product_page(callback, user_id, index - 1)
    await callback.answer()

@router.callback_query(F.data.startswith("edit:"))
async def edit_product(callback: CallbackQuery):
    product_id = int(callback.data.split(":")[1])
    await callback.answer(f"✏️ Tahrirlash funksiyasi hali yo‘q. (ID: {product_id})")

@router.callback_query(F.data.startswith("delete:"))
async def delete_product(callback: CallbackQuery):
    user_id = callback.from_user.id
    product_id = int(callback.data.split(":")[1])
    async for db in get_db():
        product = await db.get(Product, product_id)
        if product:
            await db.delete(product)
            await db.commit()
            product_pages[user_id] = [p for p in product_pages[user_id] if p.id != product_id]

    products = product_pages.get(user_id, [])
    if not products:
        await callback.message.edit_caption("✅ Mahsulot o‘chirildi. Sizda boshqa mahsulot yo‘q.", reply_markup=None)
        return await callback.answer()

    index = min(product_indices.get(user_id, 0), len(products) - 1)
    await send_product_page(callback, user_id, index)
    await callback.answer("✅ Mahsulot o‘chirildi")


