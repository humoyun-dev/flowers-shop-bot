import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN_SELLER
from handlers.start import router as start_router
from handlers.product import router as product_router
from handlers.order import router as order_router
from database import engine
from models import Base

async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    bot = Bot(token=BOT_TOKEN_SELLER)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start_router)
    dp.include_router(product_router)
    dp.include_router(order_router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
