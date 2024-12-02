import sqlite3

DB_NAME = "users.db"
USERS_TABLE = "users"
ROLES_TABLE = "roles"

def create_table():
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()

        cur.execute(f'''CREATE TABLE {USERS_TABLE} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL
                )''')

        cur.execute(f'''CREATE TABLE {ROLES_TABLE} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTERGR NOT NULL,
                    role TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES {USERS_TABLE} (id)
                )''')
        
def register_user(data):
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cur = conn.cursor()
            
            cur.execute(
                f'''
                INSERT OR IGNORE INTO {USERS_TABLE} 
                (email, password) 
                VALUES (?, ?)
                ''',
                (
                    data.get('email'),
                    data.get('password')
                )
            )
            return [201, {"message": "New user added to database"}]

    except sqlite3.Error as e:
        return [500, {"error": str(e)}]
    
def get_user(data):
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cur = conn.cursor()
            
            cur.execute(
                f'''
                SELECT FROM {USERS_TABLE} 
                WHERE email = ? AND password = ?
                ''',
                (
                    data.get('email'),
                    data.get('password')
                )
            )
            data = cur.fetchall()
        
            if data:
                return [200, [dict(row) for row in data][0]]
            else:
                return [404, {"message": "User not found"}]

    except sqlite3.Error as e:
        return [500, {"error": str(e)}]
    