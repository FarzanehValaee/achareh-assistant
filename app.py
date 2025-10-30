from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from database import save_message, get_conversations
import json
import re

app = FastAPI()

# Hardcoded data (mock APIs)
SERVICES = {
    "نظافت منزل": "nazafat-manzel",
    "تعمیر کولر": "tamir-kooler",
    # Add more as needed
}

CITIES_AVAILABLE = ["تهران"]  # Mock: only Tehran

PRICING_RULES = {
    "nazafat-manzel": "قیمت پایه ۲۰۰۰۰۰ تومان برای ۴ ساعت، هر ساعت اضافه ۵۰۰۰۰ تومان.",
    "tamir-kooler": "قیمت بازدید ۱۰۰۰۰۰ تومان، تعمیر بسته به مشکل از ۳۰۰۰۰۰ تومان.",
}

MOCK_ORDERS = {  # User ID to orders
    "user1": [
        {"id": 123, "service": "nazafat-manzel", "status": "در حال انجام"},
        {"id": 456, "service": "tamir-kooler", "status": "کامل شده"},
    ]
}

def detect_service(message: str) -> str:
    # Simple keyword matching (no OpenAI)
    message = message.lower()
    if re.search(r"نظافت|تمیز|شستشو", message):
        return "nazafat-manzel"
    elif re.search(r"تعمیر کولر|کولر|ac", message):
        return "tamir-kooler"
    return None

def check_availability(city: str) -> bool:
    return city in CITIES_AVAILABLE

def get_pricing(slug: str) -> str:
    return PRICING_RULES.get(slug, "اطلاعات قیمت موجود نیست.")

def get_order_status(user_id: str) -> str:
    orders = MOCK_ORDERS.get(user_id, [])
    if not orders:
        return "سفارشی یافت نشد."
    return "\n".join([f"سفارش {o['id']}: سرویس {o['service']}, وضعیت: {o['status']}" for o in orders])

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            save_message(user_id, data, "")  # Save user message

            # Assume city is Tehran for simplicity; in upgrade, ask user or from profile
            city = "تهران"

            response = ""
            if "وضعیت سفارش" in data:
                response = get_order_status(user_id)
            else:
                slug = detect_service(data)
                if slug:
                    if check_availability(city):
                        response = f"سرویس شناسایی شده: {slug}\n"
                        response += get_pricing(slug)
                    else:
                        response = f"سرویس در شهر {city} موجود نیست."
                else:
                    response = "سرویس مورد نظر شناسایی نشد. لطفا جزئیات بیشتری بدهید."

            await websocket.send_text(response)
            save_message(user_id, "", response)  # Save bot response
    except WebSocketDisconnect:
        print("Client disconnected")

# For testing: run uvicorn app:app --reload
# Test websocket: wscat -c ws://localhost:8000/ws/user1
# Send messages like "نظافت منزل میخوام" or "وضعیت سفارش من چیه؟"