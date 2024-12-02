import sqlite3

DB_NAME = "users.db"
TABLE_NAME = "users"

def create_table():
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()

        