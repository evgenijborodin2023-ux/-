import sqlite3
import hashlib

class UserManager:
    def __init__(self, db_name="autoservice.db"):
        self.db_name = db_name
        
    def hash_password(self, password):
        """Хеширование пароля"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_users_with_roles(self):
        """Создание пользователей с разными ролями"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Создаем таблицу для хранения пользователей БД
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS db_users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL
            )
        ''')
        
        # Создаем пользователей с разными ролями
        users = [
            ('manager', self.hash_password('manager123'), 'Менеджер'),
            ('mechanic', self.hash_password('mechanic123'), 'Автомеханик'),
            ('client', self.hash_password('client123'), 'Заказчик')
        ]
        
        cursor.executemany('INSERT OR REPLACE INTO db_users VALUES (?,?,?)', users)
        conn.commit()
        conn.close()
        print("Пользователи БД созданы")
    
    def check_permissions(self, username, action, table):
        """Проверка прав доступа"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT role FROM db_users WHERE username = ?', (username,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return False
        
        role = result[0]
        
        # Определение прав по ролям
        permissions = {
            'Менеджер': {
                'select': ['users', 'requests', 'comments'],
                'insert': ['users', 'requests', 'comments'],
                'update': ['users', 'requests', 'comments'],
                'delete': ['users', 'requests', 'comments']
            },
            'Автомеханик': {
                'select': ['users', 'requests', 'comments'],
                'insert': ['requests', 'comments'],
                'update': ['requests'],
                'delete': []
            },
            'Заказчик': {
                'select': ['users', 'requests'],
                'insert': [],
                'update': [],
                'delete': []
            }
        }
        
        return table in permissions.get(role, {}).get(action, [])
    
    def get_user_requests(self, username, user_type):
        """Получение заявок с учетом прав пользователя"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        if user_type == 'Заказчик':
            # Заказчик видит только свои заявки
            cursor.execute('''
                SELECT r.*, u.fio as master_name 
                FROM requests r
                LEFT JOIN users u ON r.masterID = u.userID
                WHERE r.clientID = (SELECT userID FROM users WHERE login = ?)
            ''', (username,))
        elif user_type == 'Автомеханик':
            # Механик видит все заявки
            cursor.execute('''
                SELECT r.*, u.fio as master_name, c.fio as client_name
                FROM requests r
                LEFT JOIN users u ON r.masterID = u.userID
                LEFT JOIN users c ON r.clientID = c.userID
            ''')
        else:
            # Менеджер видит всё
            cursor.execute('''
                SELECT r.*, u.fio as master_name, c.fio as client_name
                FROM requests r
                LEFT JOIN users u ON r.masterID = u.userID
                LEFT JOIN users c ON r.clientID = c.userID
            ''')
        
        results = cursor.fetchall()
        conn.close()
        return results

# Декоратор для проверки прав доступа
def check_access(action, table):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            if hasattr(self, 'current_user'):
                um = UserManager()
                if um.check_permissions(self.current_user, action, table):
                    return func(self, *args, **kwargs)
                else:
                    raise PermissionError(f"Нет прав на {action} в таблице {table}")
            else:
                raise PermissionError("Пользователь не авторизован")
        return wrapper
    return decorator