import requests

BASE_URL = "https://api.achareh.co/v2"

def get_service_slug(user_message, llm):
    # Use LLM to extract slug from message
    prompt = f"از پیام کاربر '{user_message}' سرویس را تشخیص بده و slug انگلیسی را برگردان (e.g., نظافت: cleaning)"
    response = llm(prompt)  # OpenAI call
    return response.strip()  # e.g., "cleaning"

def check_availability(slug, city_id):
    url = f"{BASE_URL}/services/{slug}/availability?city_id={city_id}"
    resp = requests.get(url)
    if resp.status_code == 200:
        data = resp.json()
        if not data['available']:
            return "سرویس در شهر شما موجود نیست."
    return None  # Available

def get_pricing(slug):
    url = f"{BASE_URL}/services/{slug}/pricing"
    resp = requests.get(url)
    if resp.status_code == 200:
        return resp.json()['rules']  # Explain rules
    return "خطا در دریافت قیمت."

def get_orders(user_id, token):
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}/orders?user_id={user_id}"
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        return resp.json()  # Status of orders
    return "خطا در دریافت سفارش‌ها."