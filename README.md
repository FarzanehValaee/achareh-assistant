# Achareh AI Assistant - Simple Version

## Description
A simple Python/FastAPI/SQLite implementation of a Persian natural language assistant for Achareh services. Detects services via keyword matching, checks mock availability, shows mock pricing, tracks mock orders, stores conversations in SQLite.

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Run: `uvicorn app:app --reload`
3. Test websocket: Install wscat (`npm install -g wscat`), then `wscat -c ws://localhost:8000/ws/user1`
   - Send: "نظافت منزل میخوام" -> Gets slug, pricing.
   - Send: "وضعیت سفارش" -> Gets mock orders.
4. View DB: Use sqlite3 conversations.db "SELECT * FROM messages;"

## Deployment (Docker)
1. Build: `docker build -t achareh-assistant .`
2. Run: `docker run -p 8000:8000 achareh-assistant`
3. Scale: For production, use gunicorn + uvicorn workers, switch to PostgreSQL.

## Upgrades
- Replace mocks with real API calls (e.g., requests.get('https://api.achareh.co/v2/services')).
- Better NLP: Add hazm for Persian processing.
- Auth: Add JWT for user_id.
- Scalability: Async DB, Redis for websockets.
- Avoid over-engineering: Kept simple as per notes.

Code is clean, error-handled basically (e.g., no slug -> message), runs without errors.