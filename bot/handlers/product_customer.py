from aiogram import Router, F
from aiogram.types import Message, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton, Location, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards import admin_menu
from models import Order
from database import get_db
import json

router = Router()

class OrderFSM(StatesGroup):
    AWAITING_PHONE = State()
    AWAITING_LOCATION = State()

@router.message(F.text == "/start")
async def customer_start(message: Message, state: FSMContext):
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]],
        resize_keyboard=True
    )
    await state.set_state(OrderFSM.AWAITING_PHONE)
    await message.answer("Ro'yxatdan o'tish uchun telefon raqamingizni yuboring:", reply_markup=kb)

@router.message(OrderFSM.AWAITING_PHONE)
async def receive_phone(message: Message, state: FSMContext):
    if not message.contact:
        return await message.answer("Iltimos, tugmani bosib telefon raqamingizni yuboring.")

    phone = message.contact.phone_number
    await state.update_data(phone_number=phone)

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛍 Mahsulotlarni ko‘rish", web_app=WebAppInfo(url="https://your-webapp-url.com"))]
        ],
        resize_keyboard=True
    )
    await message.answer("Ro'yxatdan o'tdingiz! Endi mahsulotlarni ko‘rishingiz mumkin:", reply_markup=kb)

@router.message(F.web_app_data)
async def process_order_from_webapp(message: Message, state: FSMContext):
    try:
        order_data = json.loads(message.web_app_data.data)
        await state.update_data(order_data=order_data)
        await state.set_state(OrderFSM.AWAITING_LOCATION)
        await message.answer("Buyurtmani qabul qildik. Endi yetkazib berish manzilingizni yuboring:",
                             reply_markup=ReplyKeyboardMarkup(
                                 keyboard=[[KeyboardButton(text="📍 Lokatsiyani yuborish", request_location=True)]],
                                 resize_keyboard=True
                             ))
    except Exception as e:
        await message.answer("Buyurtma ma'lumotlarini qabul qilishda xatolik yuz berdi.")

@router.message(OrderFSM.AWAITING_LOCATION)
async def finalize_order(message: Message, state: FSMContext):
    if not message.location:
        return await message.answer("Iltimos, lokatsiyani yuboring.")

    data = await state.get_data()
    order_data = data.get("order_data")
    phone_number = data.get("phone_number")

    async for db in get_db():
        new_order = Order(
            product_id=order_data["product_id"],
            amount=order_data["amount"],
            phone_number=phone_number,
            telegram_id=message.from_user.id,
            location=f"{message.location.latitude},{message.location.longitude}"
        )
        db.add(new_order)
        await db.commit()

    await message.answer("✅ Buyurtma muvaffaqiyatli qabul qilindi! Tez orada siz bilan bog‘lanamiz.")
    await state.clear()