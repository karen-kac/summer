import sqlite3
from backend.models.user import UserCreate
from pathlib import Path

DATABASE = Path(__file__).resolve().parent.parent / "users.db"

def create_user(user: UserCreate) -> bool:
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    last_name TEXT NOT NULL,
                    first_name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            ''')
            cursor.execute('''
                INSERT INTO users (last_name, first_name, email, password)
                VALUES (?, ?, ?, ?)
            ''', (user.last_name, user.first_name, user.email, user.password))
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        return False

def authenticate_user(email: str, password: str):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
        row = cursor.fetchone()
        if row:
            class User: pass
            user = User()
            user.first_name = row[2]
            return user
        return None
