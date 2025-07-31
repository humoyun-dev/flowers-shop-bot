from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from dotenv import load_dotenv
from database import AsyncSessionLocal
from models import Product
import os
import json
import requests

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN_SELLER")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@app.get("/products")
async def get_products(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product))
    products = result.scalars().all()
    product_list = []

    for p in products:
        try:
            image_list = json.loads(p.images)
            image = image_list[0] if image_list else f"/placeholder.svg?text=Product-{p.id}"
        except Exception:
            image = f"/placeholder.svg?text=Product-{p.id}"

        product_list.append({
            "id": p.id,
            "price": p.price,
            "image": image,
            "count": p.quantity
        })

    return product_list

@app.post("/order")
async def submit_order(order: dict):
    print("Buyurtma keldi:", order)
    return {"message": "Buyurtma qabul qilindi"}

@app.get("/file/{file_id}")
def get_telegram_file_url(file_id: str):
    file_info_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getFile?file_id={file_id}"
    try:
        response = requests.get(file_info_url)
        response.raise_for_status()
        file_path = response.json()["result"]["file_path"]
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"
        return {"url": file_url}
    except Exception as e:
        return {"error": f"File not found or request failed: {str(e)}"}
