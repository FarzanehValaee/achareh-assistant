from fastapi import FastAPI, WebSocket, Depends
from sqlalchemy.orm import Session
from app.db import SessionLocal, engine
from app.models import Base, Conversation
import json


Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        user_message = json.loads(data)["message"]
        user_id = "dummy_user"

        # Run agent (از agent.py)
        state = {"messages": [user_message]}
        result = agent.invoke(state)
        response = result["response"]

        # ذخیره در DB (SQLite)
        conv = Conversation(user_id=user_id, message=user_message, response=response)
        db.add(conv)
        db.commit()

        await websocket.send_text(json.dumps({"response": response}))