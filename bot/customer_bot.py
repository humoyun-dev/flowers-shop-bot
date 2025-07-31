from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN_CUSTOMER
from handlers.product_customer import router as customer_router
import asyncio

async def main():
    bot = Bot(token=BOT_TOKEN_CUSTOMER)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(customer_router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
