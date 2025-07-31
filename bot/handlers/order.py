from aiogram import Router
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards import cancel_keyboard
from aiogram.filters import Command

router = Router()

class OrderProcess(StatesGroup):
    WAITING_PRODUCT_ID = State()
    WAITING_AMOUNT = State()
    WAITING_PHONE = State()
    WAITING_LOCATION = State()

@router.message(Command("order"))
async def cmd_order(message: Message, state: FSMContext):
    await state.set_state(OrderProcess.WAITING_PRODUCT_ID)
    await message.answer("Buyurtma berish: Mahsulot ID kiriting:", reply_markup=cancel_keyboard())

