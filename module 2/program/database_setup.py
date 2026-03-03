import sqlite3
import csv
from datetime import datetime
import os

class AutoServiceDB:
    def __init__(self, db_name="autoservice.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """Подключение к БД"""
        self.conn = sqlite3.connect(self.db_name)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        print(f"Подключено к БД: {self.db_name}")
    
    def disconnect(self):
        """Отключение от БД"""
        if self.conn:
            self.conn.close()
            print("Отключено от БД")
    
    def create_tables(self):
        """Создание таблиц в 3НФ"""
        print("Создание таблиц...")
        
        # Таблица пользователей
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                userID INTEGER PRIMARY KEY,
                fio TEXT NOT NULL,
                phone TEXT,
                login TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                type TEXT NOT NULL CHECK(type IN ('Менеджер', 'Автомеханик', 'Заказчик'))
            )
        ''')
        
        # Таблица заявок
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS requests (
                requestID INTEGER PRIMARY KEY,
                startDate TEXT NOT NULL,
                carType TEXT NOT NULL,
                carModel TEXT NOT NULL,
                problemDescription TEXT NOT NULL,
                requestStatus TEXT NOT NULL,
                completionDate TEXT,
                repairParts TEXT,
                masterID INTEGER,
                clientID INTEGER NOT NULL,
                FOREIGN KEY (masterID) REFERENCES users(userID) ON DELETE SET NULL,
                FOREIGN KEY (clientID) REFERENCES users(userID) ON DELETE CASCADE
            )
        ''')
        
        # Таблица комментариев
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                commentID INTEGER PRIMARY KEY,
                message TEXT NOT NULL,
                masterID INTEGER NOT NULL,
                requestID INTEGER NOT NULL,
                FOREIGN KEY (masterID) REFERENCES users(userID) ON DELETE CASCADE,
                FOREIGN KEY (requestID) REFERENCES requests(requestID) ON DELETE CASCADE
            )
        ''')
        
        # Создание индексов
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_requests_status ON requests(requestStatus)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_requests_dates ON requests(startDate, completionDate)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_comments_request ON comments(requestID)')
        
        self.conn.commit()
        print("Таблицы успешно созданы")
    
    def load_data_from_csv(self):
        """Загрузка данных из CSV файлов"""
        
        # Загрузка пользователей
        if os.path.exists("inputDataUsers.csv"):
            with open("inputDataUsers.csv", 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=';')
                for row in reader:
                    self.cursor.execute('''
                        INSERT OR REPLACE INTO users (userID, fio, phone, login, password, type)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (int(row['userID']), row['fio'], row['phone'], 
                          row['login'], row['password'], row['type']))
        else:
            # Тестовые данные
            test_users = [
                (1, 'Белов А.Д.', '89210563128', 'login1', 'pass1', 'Менеджер'),
                (2, 'Харитонова М.П.', '89535078985', 'login2', 'pass2', 'Автомеханик'),
                (3, 'Сидоров П.П.', '89531234567', 'login3', 'pass3', 'Автомеханик'),
                (7, 'Ильина Т.Д.', '89219567841', 'login12', 'pass12', 'Заказчик'),
                (8, 'Петров И.И.', '89161234567', 'login8', 'pass8', 'Заказчик')
            ]
            self.cursor.executemany('INSERT OR REPLACE INTO users VALUES (?,?,?,?,?,?)', test_users)
        
        # Загрузка заявок
        if os.path.exists("inputDataRequests.csv"):
            with open("inputDataRequests.csv", 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=';')
                for row in reader:
                    completion_date = None if row['completionDate'] in ('null', '') else row['completionDate']
                    master_id = int(row['masterID']) if row['masterID'] not in ('null', '') else None
                    
                    self.cursor.execute('''
                        INSERT OR REPLACE INTO requests 
                        (requestID, startDate, carType, carModel, problemDescription, 
                         requestStatus, completionDate, repairParts, masterID, clientID)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (int(row['requestID']), row['startDate'], row['carType'], 
                          row['carModel'], row['problemDescryption'], row['requestStatus'],
                          completion_date, row['repairParts'], master_id, int(row['clientID'])))
        else:
            test_requests = [
                (1, '2023-06-06', 'Легковая', 'Hyundai Avante', 'Отказали тормоза.', 
                 'В процессе ремонта', None, None, 2, 7),
                (2, '2023-05-05', 'Легковая', 'Nissan 180SX', 'Отказали тормоза.', 
                 'В процессе ремонта', None, None, 3, 8)
            ]
            self.cursor.executemany('''
                INSERT OR REPLACE INTO requests 
                VALUES (?,?,?,?,?,?,?,?,?,?)
            ''', test_requests)
        
        # Загрузка комментариев
        if os.path.exists("inputDataComments.csv"):
            with open("inputDataComments.csv", 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=';')
                for row in reader:
                    self.cursor.execute('''
                        INSERT OR REPLACE INTO comments (commentID, message, masterID, requestID)
                        VALUES (?, ?, ?, ?)
                    ''', (int(row['commentID']), row['message'], 
                          int(row['masterID']), int(row['requestID'])))
        else:
            test_comments = [
                (1, 'Очень странно.', 2, 1),
                (2, 'Будем разбираться!', 3, 2)
            ]
            self.cursor.executemany('INSERT OR REPLACE INTO comments VALUES (?,?,?,?)', test_comments)
        
        self.conn.commit()
        print("Данные успешно загружены")
    
    def execute_query(self, query, params=()):
        """Выполнение SQL-запроса"""
        self.cursor.execute(query, params)
        return self.cursor.fetchall()
    
    def print_query_results(self, results, description):
        """Вывод результатов запроса"""
        print(f"\n{description}:")
        print("-" * 50)
        for row in results:
            print(dict(row))
        print("-" * 50)