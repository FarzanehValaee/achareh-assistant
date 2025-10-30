import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('conversations.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY,
                  user_id TEXT,
                  message TEXT,
                  response TEXT,
                  timestamp TEXT)''')
    conn.commit()
    conn.close()

def save_message(user_id: str, message: str, response: str):
    conn = sqlite3.connect('conversations.db')
    c = conn.cursor()
    timestamp = datetime.now().isoformat()
    c.execute("INSERT INTO messages (user_id, message, response, timestamp) VALUES (?, ?, ?, ?)",
              (user_id, message, response, timestamp))
    conn.commit()
    conn.close()

def get_conversations(user_id: str):
    conn = sqlite3.connect('conversations.db')
    c = conn.cursor()
    c.execute("SELECT * FROM messages WHERE user_id = ? ORDER BY timestamp", (user_id,))
    return c.fetchall()

# Initialize DB
init_db()