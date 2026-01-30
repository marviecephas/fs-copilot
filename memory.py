import sqlite3

DB_NAME = "chat_history.db"

def init_db():
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute('''CREATE TABLE IF NOT EXISTS chat_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id TEXT,
  role TEXT,
  content TEXT,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
  ''')
  conn.commit()
  conn.close()

def add_message(session_id, role, content):
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute(
    "INSERT INTO chat_history (session_id, role, content) VALUES (?, ?, ?)", (session_id, role, content)
  )
  conn.commit()
  conn.close()

def get_history(session_id):
  history = []
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute(
    "SELECT role, content FROM chat_history WHERE session_id = ? ORDER BY timestamp ASC", (session_id,)
  )
  rows = cursor.fetchall()
  conn.close()

  for row in rows:
    history.append({"role":row[0], "parts":row[1]})
    
  return history
