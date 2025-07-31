from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards import contact_keyboard, admin_menu

router = Router()

class UserState(StatesGroup):
    AWAITING_PHONE = State()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await message.answer("Salom! Iltimos, telefon raqamingizni yuboring", reply_markup=contact_keyboard())
    await state.set_state(UserState.AWAITING_PHONE)

@router.message(UserState.AWAITING_PHONE)
async def process_phone(message: Message, state: FSMContext):
    if not message.contact:
        return await message.answer("Iltimos, telefon raqamni tugmalar orqali yuboring.", reply_markup=contact_keyboard())
    user_id = message.from_user.id
    phone = message.contact.phone_number
    # TODO: Saqlash yoki ro'yxatga olish
    await message.answer("Ro‘yxatdan o‘tdingiz!", reply_markup=admin_menu())
    await state.clear()