import sqlite3
from dotenv import load_dotenv
import os
import sqlitecloud

#DB_NAME = "users.db"
# Load environment variables from .env file
load_dotenv()
DB_NAME = os.getenv("DB_NAME")

USERS_TABLE = "users"
ROLES_TABLE = "roles"

def create_table():
    with sqlitecloud.connect(DB_NAME) as conn:
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
        with sqlitecloud.connect(DB_NAME) as conn:
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

    except sqlitecloud.Error as e:
        return [500, {"error": str(e)}]
    
def get_users():
    try:
        data = None

        with sqlitecloud.connect(DB_NAME) as conn:
            conn.row_factory = sqlitecloud.Row
            cur = conn.cursor()
            
            cur.execute(f'SELECT * FROM {USERS_TABLE}')
            data = cur.fetchall()
            
            if not data:
                return [404, {"message": "No users found"}]

        newData = []
        for user in data:
            status, roles = get_roles(user['id'], conn)
            
            newData.append({
                'id': user['id'],
                'email': user['email'],
                'roles': roles if status == 200 else []
            })

        return [200, newData]

    except sqlitecloud.Error as e:
        return [500, {"error": str(e)}]

def get_user(id):
    try:
        data = None

        with sqlitecloud.connect(DB_NAME) as conn:
            conn.row_factory = sqlitecloud.Row
            cur = conn.cursor()
            
            cur.execute(f'SELECT * FROM {USERS_TABLE} WHERE id = ?', (id,))
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

    except sqlitecloud.Error as e:
        return [500, {"error": str(e)}]

def get_user_by_email(email):
    try:
        data = None

        with sqlitecloud.connect(DB_NAME) as conn:
            conn.row_factory = sqlitecloud.Row
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

    except sqlitecloud.Error as e:
        return [500, {"error": str(e)}]

def get_user_password(id):
    try:
        with sqlitecloud.connect(DB_NAME) as conn:
            conn.row_factory = sqlitecloud.Row
            cur = conn.cursor()
            
            cur.execute(f'SELECT password FROM {USERS_TABLE} WHERE id = ?', (id,))
            data = cur.fetchone()
            
            if not data:
                return [404, {"message": "User not found"}]

            return [200, data["password"]]

    except sqlitecloud.Error as e:
        return [500, {"error": str(e)}]

def update_user(id, data):
    try:
        with sqlitecloud.connect(DB_NAME) as conn:
            cur = conn.cursor()
            
            query = f'''
            UPDATE {USERS_TABLE}
            SET '''

            i = 0
            values = []
            for key,value in data.items():
                if key not in query:
                    if i > 0:
                        query+= ", "

                    query += f'{key} = ?'
                    values.append(value)
                    i += 1

            query += f" WHERE id = {id}"
            print(query)

            cur.execute(query, (values))
            if cur.rowcount == 0:
                return [404, {"message": "User not found."}]
            
            return [200, {"message": "User updated successfully."}]

    except sqlitecloud.Error as e:
        return [500, {"error": str(e)}]
    
def delete_user(id):
    try:
        with sqlitecloud.connect(DB_NAME) as conn:
            cur = conn.cursor()
            
            cur.execute(
                f'DELETE FROM {USERS_TABLE} WHERE id = ?',
                (id,)
            )
            cur.execute(
                f'DELETE FROM {ROLES_TABLE} WHERE user_id = ?',
                (id,)
            )
            return [201, {"message": "User removed from database"}]
            
    except sqlitecloud.Error as e:
        return [500, {"error": str(e)}]

def add_role(email, role):
    try:
        status, result = get_user_by_email(email)

        if status != 200:
            return [404, {"message": "User not found"}]

        with sqlitecloud.connect(DB_NAME) as conn:
            cur = conn.cursor()
            
            cur.execute(
                f'INSERT OR IGNORE INTO {ROLES_TABLE} (user_id, role) VALUES (?, ?)',
                (result['id'], role)
            )
            return [201, {"message": "New user role added to database"}]
            
    except sqlitecloud.Error as e:
        return [500, {"error": str(e)}]

def remove_role(email, role):
    try:
        status, result = get_user_by_email(email)

        if status != 200:
            return [404, {"message": "User not found"}]

        with sqlitecloud.connect(DB_NAME) as conn:
            cur = conn.cursor()
            
            cur.execute(
                f'DELETE FROM {ROLES_TABLE} WHERE user_id = ? and role = ?',
                (result['id'], role)
            )
            return [201, {"message": "User role removed from database"}]
            
    except sqlitecloud.Error as e:
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

    except sqlitecloud.Error as e:
        return [500, {"error": str(e)}]
    
#create_table()