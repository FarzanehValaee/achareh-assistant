# app.py - Main FastAPI application for Achareh AI Assistant

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import json
import sqlite3
from datetime import datetime
import uuid
from typing import List, Dict
from sentence_transformers import SentenceTransformer, util
import asyncio
import os

# Load services data
SERVICES_DATA = {
    "44": [
        {"title": "اسباب کشی و حمل بار (درون و بین شهری)", "slug": "lorry"},
        {"title": "خدمات ویژه نظافت", "slug": "special-cleaning-other-cities"},
        {"title": "سیم کشی و برقکاری", "slug": "wiring"},
        {"title": "نظافت راه‌ پله", "slug": "public"}
    ],
    "217": [
        {"title": "اسباب کشی و حمل بار (درون و بین شهری)", "slug": "lorry"},
        {"title": "خدمات عادی نظافت", "slug": "cleaning-other-cities"},
        {"title": "نصب و تعمیر ماشین لباسشویی", "slug": "washing-machine"},
        {"title": "نصب و تعمیر یخچال و فریزر", "slug": "refrigerator"}
    ],
    "235": [
        {"title": "اسباب کشی و حمل بار (درون و بین شهری)", "slug": "moving-suburban"},
        {"title": "خدمات ویژه نظافت", "slug": "special-cleaning-other-cities"},
        {"title": "سیم کشی و برقکاری", "slug": "wiring"},
        {"title": "نصب و تعمیر یخچال و فریزر", "slug": "refrigerator"}
    ],
    "333": [
        {"title": "سرویس عادی نظافت", "slug": "interior"},
        {"title": "تعمیر و سرویس پکیج", "slug": "package-repair-service"},
        {"title": "سیم کشی و برقکاری", "slug": "wiring"},
        {"title": "اسباب کشی و حمل بار (درون و بین شهری)", "slug": "lorry"}
    ],
    "436": [
        {"title": "اسباب کشی و حمل بار (درون و بین شهری)", "slug": "lorry"},
        {"title": "خدمات ویژه نظافت", "slug": "special-cleaning-other-cities"},
        {"title": "سیم کشی و برقکاری", "slug": "wiring"},
        {"title": "قالیشویی", "slug": "carpet-cleaning"}
    ],
    "553": [
        {"title": "اسباب کشی و حمل بار (درون و بین شهری)", "slug": "lorry"},
        {"title": "پمپ و منبع آب", "slug": "waterpump"},
        {"title": "تعمیر کولر گازی در محل", "slug": "air-conditioner"},
        {"title": "خدمات ویژه نظافت", "slug": "special-cleaning-other-cities"}
    ],
    "786": [
        {"title": "اسباب کشی و حمل بار (درون و بین شهری)", "slug": "lorry"},
        {"title": "خدمات عادی نظافت", "slug": "cleaning-other-cities"},
        {"title": "مبل‌ شویی و شستشوی تشک", "slug": "furniture-cleaning"},
        {"title": "نصب و تعمیر یخچال و فریزر", "slug": "refrigerator"}
    ],
    "838": [
        {"title": "اسباب کشی و حمل بار (درون و بین شهری)", "slug": "lorry"},
        {"title": "خدمات عادی نظافت", "slug": "cleaning-other-cities"},
        {"title": "لوله‌ کشی آب و فاضلاب", "slug": "plumbing"},
        {"title": "نصب و تعمیر یخچال و فریزر", "slug": "refrigerator"}
    ],
    "847": [
        {"title": "خدمات عادی نظافت", "slug": "cleaning-other-cities"}
    ],
    "996": [
        {"title": "اسباب کشی و حمل بار (درون و بین شهری)", "slug": "lorry"},
        {"title": "تعمیر کولر گازی در محل", "slug": "air-conditioner"},
        {"title": "خدمات ویژه نظافت", "slug": "special-cleaning-other-cities"},
        {"title": "نصب و تعمیر یخچال و فریزر", "slug": "refrigerator"}
    ],
    "1042": [
        {"title": "تعمیر کولر گازی در محل", "slug": "air-conditioner"},
        {"title": "کاشی‌ کاری و سرامیک", "slug": "tiling"},
        {"title": "نصب و تعمیر ماشین لباسشویی", "slug": "washing-machine"},
        {"title": "نصب و تعمیر یخچال و فریزر", "slug": "refrigerator"}
    ],
    "1073": [
        {"title": "تعمیر کولر گازی در محل", "slug": "air-conditioner"},
        {"title": "تعمیر و سرویس پکیج", "slug": "package-repair-service"},
        {"title": "خدمات ویژه نظافت", "slug": "special-cleaning-other-cities"},
        {"title": "قالیشویی", "slug": "carpet-cleaning"}
    ],
    "1076": [
        {"title": "پمپ و منبع آب", "slug": "waterpump"},
        {"title": "تعمیر کامپیوتر در محل", "slug": "computer"},
        {"title": "خدمات عادی نظافت", "slug": "cleaning-other-cities"},
        {"title": "نصب و تعمیر ماشین ظرفشویی", "slug": "dishwasher"}
    ],
    "1113": [
        {"title": "بنایی", "slug": "masonry"},
        {"title": "جوشکاری و آهنگری", "slug": "welding"},
        {"title": "خدمات ویژه نظافت", "slug": "special-cleaning-other-cities"},
        {"title": "نصب شیرآلات و تعمیر سیفون", "slug": "faucet"}
    ],
    "1134": [
        {"title": "خدمات عادی نظافت", "slug": "cleaning-other-cities"},
        {"title": "کارگر ساده", "slug": "laborer"},
        {"title": "نظافت راه‌ پله", "slug": "public"}
    ],
    "1198": [
        {"title": "خدمات عادی نظافت", "slug": "cleaning-other-cities"},
        {"title": "نصب شیرآلات و تعمیر سیفون", "slug": "faucet"},
        {"title": "نصب و تعمیر اجاق گاز", "slug": "oven"},
        {"title": "نصب و تعمیر یخچال و فریزر", "slug": "refrigerator"}
    ],
    "1216": [
        {"title": "اسباب کشی و حمل بار (درون و بین شهری)", "slug": "lorry"},
        {"title": "خدمات عادی نظافت", "slug": "cleaning-other-cities"},
        {"title": "نصب و تعمیر آیفون تصویری", "slug": "doorbell-camera"},
        {"title": "نصب و تعمیر یخچال و فریزر", "slug": "refrigerator"}
    ],
    "3797": [
        {"title": "تخلیه چاه و لوله بازکنی", "slug": "drain"},
        {"title": "تعمیر کولر گازی در محل", "slug": "air-conditioner"},
        {"title": "خدمات ویژه نظافت", "slug": "special-cleaning-other-cities"},
        {"title": "نصب و تعمیر یخچال و فریزر", "slug": "refrigerator"}
    ]
}

# City ID to name mapping
CITY_MAP = {
    "44": "tabriz",
    "217": "isfahan",
    "235": "karaj",
    "333": "tehran",
    "436": "mashhad",
    "553": "ahvaz",
    "786": "qom",
    "838": "kerman",
    "847": "kerman",
    "996": "rasht",
    "1042": "general",
    "1073": "general",
    "1076": "amol",
    "1113": "general",
    "1134": "bandar-abbas",
    "1198": "general",
    "1216": "shiraz",
    "3797": "general"
}

CITY_NAME_TO_ID = {v.lower(): k for k, v in CITY_MAP.items()}

PERSIAN_CITIES = {
    "tabriz": "تبریز",
    "isfahan": "اصفهان",
    "karaj": "کرج",
    "tehran": "تهران",
    "mashhad": "مشهد",
    "ahvaz": "اهواز",
    "qom": "قم",
    "kerman": "کرمان",
    "rasht": "رشت",
    "shiraz": "شیراز",
    "bandar-abbas": "بندرعباس",
    "amol": "آمل",
    "general": "عمومی"
}

model = SentenceTransformer(
    'xmanii/maux-gte-persian',
    trust_remote_code=True
)

PRICING_MOCK = {
    "lorry": "قیمت اسباب‌کشی بر اساس مسافت و حجم بار محاسبه می‌شود. حداقل 500,000 تومان.",
    "special-cleaning-other-cities": "نظافت ویژه: ساعتی 100,000 تومان.",
    "wiring": "سیم‌کشی: بازدید رایگان، تعمیر از 200,000 تومان.",
    "public": "نظافت راه‌پله: بر اساس تعداد طبقات، از 150,000 تومان.",
    "cleaning-other-cities": "نظافت عادی: ساعتی 80,000 تومان.",
    "washing-machine": "تعمیر لباسشویی: از 300,000 تومان.",
    "refrigerator": "تعمیر یخچال: از 400,000 تومان.",
    "moving-suburban": "اسباب‌کشی برون شهری: بر اساس مسافت.",
    "interior": "نظافت داخلی: ساعتی 90,000 تومان.",
    "package-repair-service": "سرویس پکیج: از 250,000 تومان.",
    "carpet-cleaning": "قالیشویی: متر مربعی 20,000 تومان.",
    "waterpump": "پمپ آب: نصب از 200,000 تومان.",
    "air-conditioner": "تعمیر کولر گازی: از 350,000 تومان.",
    "furniture-cleaning": "مبل‌شویی: از 300,000 تومان.",
    "plumbing": "لوله‌کشی: بازدید رایگان.",
    "tiling": "کاشی‌کاری: متر مربعی 50,000 تومان.",
    "computer": "تعمیر کامپیوتر: از 200,000 تومان.",
    "dishwasher": "تعمیر ظرفشویی: از 300,000 تومان.",
    "masonry": "بنایی: بر اساس پروژه.",
    "welding": "جوشکاری: ساعتی 100,000 تومان.",
    "faucet": "نصب شیرآلات: از 150,000 تومان.",
    "laborer": "کارگر ساده: روزانه 500,000 تومان.",
    "oven": "تعمیر اجاق گاز: از 250,000 تومان.",
    "doorbell-camera": "نصب آیفون: از 200,000 تومان.",
    "drain": "تخلیه چاه: بر اساس حجم."
}

# Mock orders
MOCK_ORDERS = {
    "user1": [{"id": 123, "status": "در حال انجام", "service": "نظافت منزل"}]
}

app = FastAPI()

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Database setup
conn = sqlite3.connect('conversations.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY,
    timestamp DATETIME,
    user_message TEXT,
    bot_response TEXT
)
''')
conn.commit()

def detect_service(user_input: str, city_id: str) -> Dict:
    if city_id not in SERVICES_DATA:
        return {"slug": None, "available": False}
    
    services = SERVICES_DATA[city_id]
    service_titles = [s["title"] for s in services]
    
    user_embedding = model.encode(user_input)
    service_embeddings = model.encode(service_titles)
    
    similarities = util.cos_sim(user_embedding, service_embeddings)[0]
    best_idx = similarities.argmax()
    if similarities[best_idx] > 0.5:
        return {"slug": services[best_idx]["slug"], "title": services[best_idx]["title"], "available": True}
    return {"slug": None, "available": False}

def get_pricing(slug: str) -> str:
    return PRICING_MOCK.get(slug, "قیمت موجود نیست. لطفاً با پشتیبانی تماس بگیرید.")

def track_order(user_id: str) -> str:
    orders = MOCK_ORDERS.get(user_id, [])
    if not orders:
        return "سفارشی یافت نشد."
    return "\n".join([f"سفارش {o['id']}: {o['status']}" for o in orders])

def store_conversation(convo_id: str, user_msg: str, bot_resp: str):
    cursor.execute('''
    INSERT OR REPLACE INTO conversations (id, timestamp, user_message, bot_response)
    VALUES (?, ?, ?, ?)
    ''', (convo_id, datetime.now(), user_msg, bot_resp))
    conn.commit()

@app.get("/", response_class=HTMLResponse)
async def get_ui():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>دستیار آچاره</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Tahoma, Arial, sans-serif; direction: rtl; margin: 20px; background: #f4f4f9; }
            #chat { border: 1px solid #ddd; height: 400px; overflow-y: auto; padding: 15px; background: white; border-radius: 8px; margin-bottom: 10px; }
            #input { width: 78%; padding: 12px; font-size: 16px; border: 1px solid #ccc; border-radius: 8px; }
            button { width: 20%; padding: 12px; font-size: 16px; background: #007bff; color: white; border: none; border-radius: 8px; cursor: pointer; }
            button:hover { background: #0056b3; }
            .message { margin: 8px 0; padding: 8px; border-radius: 8px; }
            .user { background: #e3f2fd; text-align: left; direction: ltr; }
            .bot { background: #f0f0f0; }
        </style>
    </head>
    <body>
        <h1 style="text-align: center;">دستیار هوشمند آچاره</h1>
        <div id="chat"></div>
        <input type="text" id="input" placeholder="نام شهر خود را به انگلیسی وارد کنید (مثل tehran)...">
        <button onclick="sendMessage()">ارسال</button>

        <script>
            console.log("Connecting to WebSocket...");
            const ws = new WebSocket("ws://" + window.location.host + "/ws");
            const chat = document.getElementById("chat");
            const input = document.getElementById("input");

            ws.onopen = () => {
                console.log("WebSocket connected!");
                addMessage("بات: سلام! نام شهر خود را وارد کنید (مثلاً تهران، تبریز، اصفهان و...).", "bot");
            };

            ws.onmessage = (event) => {
                console.log("Message from server:", event.data);
                addMessage("بات: " + event.data, "bot");
            };

            ws.onerror = (error) => {
                console.error("WebSocket error:", error);
                addMessage("خطا: اتصال به سرور قطع شد.", "bot");
            };

            ws.onclose = () => {
                console.log("WebSocket closed.");
                addMessage("اتصال قطع شد.", "bot");
            };

            function addMessage(text, type) {
                const div = document.createElement("div");
                div.className = "message " + type;
                div.innerHTML = "<strong>" + (type === "user" ? "شما" : "بات") + ":</strong> " + text;
                chat.appendChild(div);
                chat.scrollTop = chat.scrollHeight;
            }

            function sendMessage() {
                const msg = input.value.trim();
                if (!msg) return;
                addMessage(msg, "user");
                ws.send(msg);
                input.value = "";
            }

            input.addEventListener("keypress", (e) => {
                if (e.key === "Enter") sendMessage();
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    convo_id = str(uuid.uuid4())
    state = {"city_id": None, "user_id": "user1"}  # Mock, replace with auth
    
    await websocket.send_text("سلام! نام شهر خود را وارد کنید (مثلاً تهران، تبریز، اصفهان و...).")
    
    try:
        while True:
            user_input = await websocket.receive_text()
            store_conversation(convo_id, user_input, "")  
            
            if state["city_id"] is None:
                normalized_input = user_input.strip().lower()
                
                if normalized_input in CITY_NAME_TO_ID:
                    state["city_id"] = CITY_NAME_TO_ID[normalized_input]
                    city_english = CITY_MAP[state["city_id"]]
                    persian_name = PERSIAN_CITIES.get(city_english, city_english)
                    response = f"شهر {persian_name} تنظیم شد. حالا نیاز خود را بیان کنید (مثلاً 'نظافت منزل')."
                
                elif user_input in SERVICES_DATA:
                    state["city_id"] = user_input
                    city_english = CITY_MAP.get(user_input, "ناشناخته")
                    persian_name = PERSIAN_CITIES.get(city_english, city_english)
                    response = f"شهر با کد {user_input} ({persian_name}) تنظیم شد. نیاز خود را بیان کنید."
                
                else:
                    available_cities = "تهران، تبریز، اصفهان، کرج، مشهد، اهواز، قم، کرمان، رشت، شیراز، بندرعباس، آمل"
                    response = f"نام یا کد شهر نامعتبر است. شهرهای موجود: {available_cities}"
            
            else:
                if "پیگیری سفارش" in user_input or "وضعیت سفارش" in user_input:
                    response = track_order(state["user_id"])
                else:
                    service = detect_service(user_input, state["city_id"])
                    if service["available"]:
                        slug = service["slug"]
                        response = f"سرویس شناسایی شد: {service['title']} (اسلاگ: {slug})\n"
                        response += f"قیمت: {get_pricing(slug)}"
                    else:
                        response = "سرویس مورد نظر در شهر شما موجود نیست."
            
            store_conversation(convo_id, user_input, response)  
            await websocket.send_text(response)
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_text(f"خطا: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)