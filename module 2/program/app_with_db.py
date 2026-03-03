import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database_setup import AutoServiceDB
from user_management import UserManager, check_access

class AutoServiceAppWithDB:
    def __init__(self, root):
        self.root = root
        self.root.title("Автосервис: Учёт заявок на ремонт")
        self.root.geometry("900x600")
        
        # Инициализация БД
        self.db = AutoServiceDB()
        self.db.connect()
        
        # Создание таблиц, если их нет
        self.db.create_tables()
        self.db.load_data_from_csv()
        
        # Менеджер пользователей
        self.user_manager = UserManager()
        self.user_manager.create_users_with_roles()
        
        # Текущий пользователь
        self.current_user = None
        self.current_user_role = None
        
        self.show_login_window()
    
    def show_login_window(self):
        """Окно входа"""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.root.title("Авторизация")
        
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(expand=True)
        
        ttk.Label(main_frame, text="Вход в систему учёта заявок", 
                 font=("Arial", 16)).grid(row=0, column=0, columnspan=2, pady=20)
        
        ttk.Label(main_frame, text="Логин:").grid(row=1, column=0, sticky="w", pady=5)
        self.login_entry = ttk.Entry(main_frame, width=30)
        self.login_entry.grid(row=1, column=1, pady=5)
        
        ttk.Label(main_frame, text="Пароль:").grid(row=2, column=0, sticky="w", pady=5)
        self.password_entry = ttk.Entry(main_frame, width=30, show="*")
        self.password_entry.grid(row=2, column=1, pady=5)
        
        ttk.Button(main_frame, text="Войти", command=self.login).grid(row=3, column=0, columnspan=2, pady=20)
        
        self.password_entry.bind('<Return>', lambda e: self.login())
    
    def login(self):
        """Проверка логина и пароля в БД"""
        login = self.login_entry.get()
        password = self.password_entry.get()
        
        # Поиск пользователя в БД
        result = self.db.execute_query(
            'SELECT * FROM users WHERE login = ? AND password = ?',
            (login, password)
        )
        
        if result:
            self.current_user = login
            self.current_user_role = result[0]['type']
            self.show_main_window()
        else:
            messagebox.showerror("Ошибка входа", "Неверный логин или пароль")
    
    def show_main_window(self):
        """Главное окно"""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.root.title(f"Автосервис - Главная (пользователь: {self.current_user}, роль: {self.current_user_role})")
        
        # Верхняя панель
        top_frame = ttk.Frame(self.root, padding="5")
        top_frame.pack(fill=tk.X)
        
        ttk.Label(top_frame, text=f"Вы вошли как: {self.current_user} ({self.current_user_role})").pack(side=tk.LEFT)
        ttk.Button(top_frame, text="Выйти", command=self.show_login_window).pack(side=tk.RIGHT)
        
        # Панель инструментов (с проверкой прав)
        toolbar = ttk.Frame(self.root, padding="5")
        toolbar.pack(fill=tk.X)
        
        if self.user_manager.check_permissions(self.current_user, 'insert', 'requests'):
            ttk.Button(toolbar, text="➕ Новая заявка", 
                      command=self.add_request_window).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(toolbar, text="📊 Статистика", 
                  command=self.show_stats).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🔄 Обновить", 
                  command=self.refresh_requests_list).pack(side=tk.LEFT, padx=2)
        
        # Поиск
        ttk.Label(toolbar, text="Поиск:").pack(side=tk.LEFT, padx=(20, 2))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda a, b, c: self.filter_requests())
        ttk.Entry(toolbar, textvariable=self.search_var, width=30).pack(side=tk.LEFT, padx=2)
        
        # Таблица заявок
        columns = ('ID', 'Дата', 'Авто', 'Проблема', 'Статус', 'Мастер', 'Клиент')
        self.tree = ttk.Treeview(self.root, columns=columns, show='headings', height=15)
        
        # Настройка заголовков
        for col in columns:
            self.tree.heading(col, text=col)
        
        self.tree.column('ID', width=50)
        self.tree.column('Дата', width=100)
        self.tree.column('Авто', width=150)
        self.tree.column('Проблема', width=200)
        self.tree.column('Статус', width=120)
        self.tree.column('Мастер', width=120)
        self.tree.column('Клиент', width=150)
        
        scrollbar = ttk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        self.tree.bind('<Double-1>', lambda e: self.show_request_details())
        
        self.refresh_requests_list()
    
    def refresh_requests_list(self):
        """Обновление списка заявок из БД"""
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        # Получаем заявки с учетом прав пользователя
        requests = self.user_manager.get_user_requests(self.current_user, self.current_user_role)
        
        for req in requests:
            self.tree.insert('', tk.END, values=req[:7])
    
    def filter_requests(self):
        """Фильтрация заявок"""
        search_text = self.search_var.get().lower()
        
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        requests = self.user_manager.get_user_requests(self.current_user, self.current_user_role)
        
        for req in requests:
            if (search_text in str(req[0]).lower() or 
                search_text in str(req[3]).lower()):
                self.tree.insert('', tk.END, values=req[:7])
    
    def add_request_window(self):
        """Окно добавления заявки"""
        if not self.user_manager.check_permissions(self.current_user, 'insert', 'requests'):
            messagebox.showerror("Ошибка", "У вас нет прав на создание заявок")
            return
        
        add_win = tk.Toplevel(self.root)
        add_win.title("Новая заявка")
        add_win.geometry("500x400")
        
        frame = ttk.Frame(add_win, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Тип авто:").grid(row=0, column=0, sticky="w", pady=5)
        car_type = ttk.Combobox(frame, values=["Легковая", "Грузовая", "Мотоцикл"], width=30)
        car_type.set("Легковая")
        car_type.grid(row=0, column=1, pady=5)
        
        ttk.Label(frame, text="Модель:*").grid(row=1, column=0, sticky="w", pady=5)
        model = ttk.Entry(frame, width=32)
        model.grid(row=1, column=1, pady=5)
        
        ttk.Label(frame, text="Описание:*").grid(row=2, column=0, sticky="w", pady=5)
        problem = tk.Text(frame, width=30, height=5)
        problem.grid(row=2, column=1, pady=5)
        
        ttk.Label(frame, text="Клиент ID:").grid(row=3, column=0, sticky="w", pady=5)
        client = ttk.Entry(frame, width=32)
        client.insert(0, "7")
        client.grid(row=3, column=1, pady=5)
        
        def save():
            if not model.get() or not problem.get("1.0", tk.END).strip():
                messagebox.showwarning("Ошибка", "Заполните обязательные поля")
                return
            
            # Получаем следующий ID
            result = self.db.execute_query('SELECT MAX(requestID) FROM requests')
            new_id = (result[0][0] or 0) + 1
            
            self.db.execute_query('''
                INSERT INTO requests 
                (requestID, startDate, carType, carModel, problemDescription, 
                 requestStatus, completionDate, repairParts, masterID, clientID)
                VALUES (?, date('now'), ?, ?, ?, 'Новая заявка', NULL, NULL, NULL, ?)
            ''', (new_id, car_type.get(), model.get(), 
                  problem.get("1.0", tk.END).strip(), 
                  int(client.get()) if client.get().isdigit() else 7))
            
            self.db.conn.commit()
            self.refresh_requests_list()
            messagebox.showinfo("Успех", f"Заявка №{new_id} создана")
            add_win.destroy()
        
        ttk.Button(frame, text="Сохранить", command=save).grid(row=4, column=0, columnspan=2, pady=20)
    
    def show_request_details(self):
        """Просмотр деталей заявки"""
        selected = self.tree.selection()
        if not selected:
            return
        
        item = self.tree.item(selected[0])
        request_id = item['values'][0]
        
        # Получаем данные из БД
        request = self.db.execute_query(
            'SELECT * FROM requests WHERE requestID = ?', 
            (request_id,)
        )[0]
        
        comments = self.db.execute_query(
            '''SELECT c.*, u.fio FROM comments c 
               JOIN users u ON c.masterID = u.userID 
               WHERE requestID = ?''',
            (request_id,)
        )
        
        # Отображение деталей (аналогично оригинальному коду)
        detail_win = tk.Toplevel(self.root)
        detail_win.title(f"Заявка №{request_id}")
        detail_win.geometry("600x500")
        
        # ... (код отображения аналогичен оригинальному)
    
    def show_stats(self):
        """Показ статистики из БД"""
        stats = self.db.execute_query('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN requestStatus = 'Готова к выдаче' THEN 1 ELSE 0 END) as completed,
                AVG(CASE WHEN completionDate IS NOT NULL 
                    THEN julianday(completionDate) - julianday(startDate) 
                    ELSE NULL END) as avg_time
            FROM requests
        ''')[0]
        
        problem_stats = self.db.execute_query('''
            SELECT substr(problemDescription, 1, instr(problemDescription, ' ') - 1) as problem_word,
                   COUNT(*) as count
            FROM requests
            GROUP BY problem_word
            ORDER BY count DESC
            LIMIT 5
        ''')
        
        # Отображение статистики
        stats_win = tk.Toplevel(self.root)
        stats_win.title("Статистика")
        stats_win.geometry("400x300")
        
        frame = ttk.Frame(stats_win, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Статистика заявок", font=("Arial", 14, "bold")).pack(pady=10)
        ttk.Label(frame, text=f"Всего заявок: {stats['total']}").pack(anchor="w")
        ttk.Label(frame, text=f"Выполнено: {stats['completed']}").pack(anchor="w")
        ttk.Label(frame, text=f"Среднее время: {stats['avg_time']:.1f} дней").pack(anchor="w")
        
        ttk.Label(frame, text="\nТоп проблем:", font=("Arial", 10, "bold")).pack(anchor="w")
        for p in problem_stats:
            ttk.Label(frame, text=f"  {p['problem_word']}: {p['count']}").pack(anchor="w")
        
        ttk.Button(frame, text="Закрыть", command=stats_win.destroy).pack(pady=20)

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoServiceAppWithDB(root)
    root.mainloop()