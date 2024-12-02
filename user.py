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
                user_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES {USERS_TABLE} (id),
                UNIQUE (user_id, role)
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

        status, result = add_role(data.get('email'), "user")

        if (status != 201):
            return [status, {"message": f"New user added to database but could not add a role: {result}"}]

        return [201, {"message": "New user added to database"}]

    except sqlite3.Error as e:
        return [500, {"error": str(e)}]
    
def get_user(email):
    try:
        data = None

        with sqlite3.connect(DB_NAME) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            
            cur.execute(f'SELECT * FROM {USERS_TABLE} WHERE email = ?', (email,))
            data = cur.fetchone()
            
            if not data:
                return [404, {"message": "User not found"}]
            
        status, roles = get_roles(data['id'], conn)
                
        return [200, {
            'id': data['id'],
            'email': data['email'],
            'password': data['password'],
            'roles': roles if status == 200 else []
        }]

    except sqlite3.Error as e:
        return [500, {"error": str(e)}]
    
    
def add_role(email, role):
    try:
        status, result = get_user(email)

        if status != 200:
            return [404, {"message": "User not found"}]

        with sqlite3.connect(DB_NAME) as conn:
            cur = conn.cursor()
            
            cur.execute(
                f'INSERT OR IGNORE INTO {ROLES_TABLE} (user_id, role) VALUES (?, ?)',
                (result['id'], role)
            )
            return [201, {"message": "New user role added to database"}]
            
    except sqlite3.Error as e:
        return [500, {"error": str(e)}]
    
def get_roles(user_id, conn):
    try:
        cur = conn.cursor()
        cur.execute('SELECT role FROM roles WHERE user_id = ?', (user_id,))
        data = cur.fetchall()

        if data:
            return [200, [row[0] for row in data]]  # Extract roles into a list
        else:
            return [404, {"message": "No roles found"}]

    except sqlite3.Error as e:
        return [500, {"error": str(e)}]
    
#create_table()