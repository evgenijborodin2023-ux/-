import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import csv
from typing import List, Dict, Any

# ----------------------------------------------------------------------
# Модуль 1: Разработка модулей ПО
# Вариант №3: Учёт заявок на ремонт автомобилей
# ----------------------------------------------------------------------

# ======================================================================
# 1. ЗАГРУЗКА ДАННЫХ ИЗ ФАЙЛОВ (имитация БД)
# ======================================================================

def load_users(filename: str = "inputDataUsers.csv") -> List[Dict[str, Any]]:
    """Загружает пользователей из CSV-файла."""
    users = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                # Преобразуем ID в int
                row['userID'] = int(row['userID'])
                users.append(row)
    except FileNotFoundError:
        # Если файл не найден, создаём тестовые данные
        users = [
            {'userID': 1, 'fio': 'Белов А.Д.', 'phone': '89210563128', 'login': 'login1', 'password': 'pass1', 'type': 'Менеджер'},
            {'userID': 2, 'fio': 'Харитонова М.П.', 'phone': '89535078985', 'login': 'login2', 'password': 'pass2', 'type': 'Автомеханик'},
            {'userID': 7, 'fio': 'Ильина Т.Д.', 'phone': '89219567841', 'login': 'login12', 'password': 'pass12', 'type': 'Заказчик'},
        ]
    return users

def load_requests(filename: str = "inputDataRequests.csv") -> List[Dict[str, Any]]:
    """Загружает заявки из CSV-файла."""
    requests = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                row['requestID'] = int(row['requestID'])
                # Преобразуем пустые строки и 'null' в None
                row['completionDate'] = None if row['completionDate'] in ('null', '') else row['completionDate']
                row['repairParts'] = row['repairParts'] if row['repairParts'] else None
                row['masterID'] = int(row['masterID']) if row['masterID'] not in ('null', '') else None
                row['clientID'] = int(row['clientID'])
                requests.append(row)
    except FileNotFoundError:
        # Тестовые данные
        requests = [
            {'requestID': 1, 'startDate': '2023-06-06', 'carType': 'Легковая', 'carModel': 'Hyundai Avante',
             'problemDescryption': 'Отказали тормоза.', 'requestStatus': 'В процессе ремонта',
             'completionDate': None, 'repairParts': None, 'masterID': 2, 'clientID': 7},
            {'requestID': 2, 'startDate': '2023-05-05', 'carType': 'Легковая', 'carModel': 'Nissan 180SX',
             'problemDescryption': 'Отказали тормоза.', 'requestStatus': 'В процессе ремонта',
             'completionDate': None, 'repairParts': None, 'masterID': 3, 'clientID': 8},
        ]
    return requests

def load_comments(filename: str = "inputDataComments.csv") -> List[Dict[str, Any]]:
    """Загружает комментарии из CSV-файла."""
    comments = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                row['commentID'] = int(row['commentID'])
                row['masterID'] = int(row['masterID'])
                row['requestID'] = int(row['requestID'])
                comments.append(row)
    except FileNotFoundError:
        comments = [
            {'commentID': 1, 'message': 'Очень странно.', 'masterID': 2, 'requestID': 1},
            {'commentID': 2, 'message': 'Будем разбираться!', 'masterID': 3, 'requestID': 2},
        ]
    return comments


# ======================================================================
# 2. ОСНОВНОЙ КЛАСС ПРИЛОЖЕНИЯ
# ======================================================================

class AutoServiceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Автосервис: Учёт заявок на ремонт")
        self.root.geometry("900x600")
        
        # Данные (имитация БД)
        self.users = load_users()
        self.requests = load_requests()
        self.comments = load_comments()
        
        # Текущий пользователь (после авторизации)
        self.current_user = None
        
        # Показываем окно авторизации
        self.show_login_window()
    
    # ==================================================================
    # 2.1. АВТОРИЗАЦИЯ
    # ==================================================================
    
    def show_login_window(self):
        """Создаёт окно входа в систему."""
        # Очищаем главное окно
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.root.title("Авторизация")
        
        # Фрейм для центрирования
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
        
        # Привязываем Enter к кнопке входа
        self.password_entry.bind('<Return>', lambda e: self.login())
    
    def login(self):
        """Проверяет логин и пароль."""
        login = self.login_entry.get()
        password = self.password_entry.get()
        
        # Поиск пользователя
        for user in self.users:
            if user['login'] == login and user['password'] == password:
                self.current_user = user
                self.show_main_window()
                return
        
        # Если не найден
        messagebox.showerror("Ошибка входа", "Неверный логин или пароль.\nПопробуйте снова.")
    
    # ==================================================================
    # 2.2. ГЛАВНОЕ ОКНО (СПИСОК ЗАЯВОК)
    # ==================================================================
    
    def show_main_window(self):
        """Главное окно со списком заявок."""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.root.title(f"Автосервис - Главная (пользователь: {self.current_user['fio']})")
        
        # Верхняя панель с информацией о пользователе и кнопкой выхода
        top_frame = ttk.Frame(self.root, padding="5")
        top_frame.pack(fill=tk.X)
        
        ttk.Label(top_frame, text=f"Вы вошли как: {self.current_user['fio']} ({self.current_user['type']})").pack(side=tk.LEFT)
        ttk.Button(top_frame, text="Выйти", command=self.show_login_window).pack(side=tk.RIGHT)
        
        # Панель инструментов
        toolbar = ttk.Frame(self.root, padding="5")
        toolbar.pack(fill=tk.X)
        
        ttk.Button(toolbar, text="➕ Новая заявка", command=self.add_request_window).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="📊 Статистика", command=self.show_stats).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🔄 Обновить", command=self.refresh_requests_list).pack(side=tk.LEFT, padx=2)
        
        # Поле поиска
        ttk.Label(toolbar, text="Поиск:").pack(side=tk.LEFT, padx=(20, 2))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda a, b, c: self.filter_requests())
        ttk.Entry(toolbar, textvariable=self.search_var, width=30).pack(side=tk.LEFT, padx=2)
        
        # Таблица заявок
        columns = ('ID', 'Дата', 'Авто', 'Проблема', 'Статус', 'Мастер', 'Клиент')
        self.tree = ttk.Treeview(self.root, columns=columns, show='headings', height=15)
        
        # Настройка заголовков
        self.tree.heading('ID', text='№')
        self.tree.heading('Дата', text='Дата создания')
        self.tree.heading('Авто', text='Автомобиль')
        self.tree.heading('Проблема', text='Описание проблемы')
        self.tree.heading('Статус', text='Статус')
        self.tree.heading('Мастер', text='Ответственный')
        self.tree.heading('Клиент', text='Клиент')
        
        self.tree.column('ID', width=50)
        self.tree.column('Дата', width=100)
        self.tree.column('Авто', width=150)
        self.tree.column('Проблема', width=200)
        self.tree.column('Статус', width=120)
        self.tree.column('Мастер', width=120)
        self.tree.column('Клиент', width=150)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Привязываем двойной клик для просмотра деталей
        self.tree.bind('<Double-1>', lambda e: self.show_request_details())
        
        # Загружаем данные
        self.refresh_requests_list()
    
    def refresh_requests_list(self):
        """Обновляет список заявок в таблице."""
        # Очищаем таблицу
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        # Заполняем данными
        for req in self.requests:
            # Находим ФИО мастера и клиента
            master_name = self.get_user_name(req['masterID']) if req['masterID'] else 'Не назначен'
            client_name = self.get_user_name(req['clientID'])
            
            self.tree.insert('', tk.END, values=(
                req['requestID'],
                req['startDate'],
                f"{req['carType']} {req['carModel']}",
                req['problemDescryption'][:50] + ('...' if len(req['problemDescryption']) > 50 else ''),
                req['requestStatus'],
                master_name,
                client_name
            ))
    
    def filter_requests(self):
        """Фильтрует заявки по поисковому запросу."""
        search_text = self.search_var.get().lower()
        
        # Очищаем таблицу
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        # Заполняем отфильтрованными данными
        for req in self.requests:
            if (search_text in str(req['requestID']).lower() or 
                search_text in req['carModel'].lower() or
                search_text in req['problemDescryption'].lower()):
                
                master_name = self.get_user_name(req['masterID']) if req['masterID'] else 'Не назначен'
                client_name = self.get_user_name(req['clientID'])
                
                self.tree.insert('', tk.END, values=(
                    req['requestID'],
                    req['startDate'],
                    f"{req['carType']} {req['carModel']}",
                    req['problemDescryption'][:50] + ('...' if len(req['problemDescryption']) > 50 else ''),
                    req['requestStatus'],
                    master_name,
                    client_name
                ))
        
        # Если ничего не найдено, показываем сообщение
        if not self.tree.get_children():
            messagebox.showinfo("Результаты поиска", "Заявки, соответствующие запросу, не найдены.")
    
    def get_user_name(self, user_id: int) -> str:
        """Возвращает ФИО пользователя по ID."""
        for user in self.users:
            if user['userID'] == user_id:
                return user['fio']
        return "Неизвестно"
    
    # ==================================================================
    # 2.3. ДОБАВЛЕНИЕ НОВОЙ ЗАЯВКИ
    # ==================================================================
    
    def add_request_window(self):
        """Окно для создания новой заявки."""
        add_win = tk.Toplevel(self.root)
        add_win.title("Новая заявка на ремонт")
        add_win.geometry("500x450")
        add_win.transient(self.root)
        add_win.grab_set()
        
        # Основной фрейм
        frame = ttk.Frame(add_win, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Поля ввода
        ttk.Label(frame, text="Тип авто:").grid(row=0, column=0, sticky="w", pady=5)
        car_type_var = tk.StringVar(value="Легковая")
        ttk.Combobox(frame, textvariable=car_type_var, values=["Легковая", "Грузовая", "Мотоцикл"], 
                    state="readonly", width=30).grid(row=0, column=1, pady=5)
        
        ttk.Label(frame, text="Модель авто:*").grid(row=1, column=0, sticky="w", pady=5)
        model_entry = ttk.Entry(frame, width=32)
        model_entry.grid(row=1, column=1, pady=5)
        
        ttk.Label(frame, text="Описание проблемы:*").grid(row=2, column=0, sticky="w", pady=5)
        problem_text = tk.Text(frame, width=30, height=5)
        problem_text.grid(row=2, column=1, pady=5)
        
        ttk.Label(frame, text="Клиент (ID):").grid(row=3, column=0, sticky="w", pady=5)
        # Простой выбор клиента (в реальном проекте был бы ComboBox со списком)
        client_entry = ttk.Entry(frame, width=32)
        client_entry.insert(0, "7")  # Тестовый ID
        client_entry.grid(row=3, column=1, pady=5)
        
        # Информационное сообщение об обязательных полях
        ttk.Label(frame, text="* - обязательные поля", foreground="gray").grid(row=4, column=0, columnspan=2, pady=10)
        
        # Кнопки
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        def save_request():
            """Сохранение новой заявки."""
            # Проверка обязательных полей
            car_model = model_entry.get().strip()
            problem = problem_text.get("1.0", tk.END).strip()
            
            if not car_model or not problem:
                messagebox.showwarning("Предупреждение", 
                                      "Поля 'Модель' и 'Описание проблемы' обязательны для заполнения.")
                return
            
            # Генерация нового ID
            new_id = max([r['requestID'] for r in self.requests]) + 1 if self.requests else 1
            
            # Создание заявки
            new_request = {
                'requestID': new_id,
                'startDate': datetime.now().strftime('%Y-%m-%d'),
                'carType': car_type_var.get(),
                'carModel': car_model,
                'problemDescryption': problem,
                'requestStatus': 'Новая заявка',
                'completionDate': None,
                'repairParts': None,
                'masterID': None,
                'clientID': int(client_entry.get()) if client_entry.get().isdigit() else 7
            }
            
            self.requests.append(new_request)
            self.refresh_requests_list()
            messagebox.showinfo("Успех", f"Заявка №{new_id} успешно создана!")
            add_win.destroy()
        
        ttk.Button(btn_frame, text="Сохранить", command=save_request).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Отмена", command=add_win.destroy).pack(side=tk.LEFT, padx=5)
    
    # ==================================================================
    # 2.4. ПРОСМОТР ДЕТАЛЕЙ ЗАЯВКИ И ДОБАВЛЕНИЕ КОММЕНТАРИЕВ
    # ==================================================================
    
    def show_request_details(self):
        """Открывает окно с детальной информацией о заявке."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Информация", "Выберите заявку для просмотра.")
            return
        
        # Получаем ID выбранной заявки
        item = self.tree.item(selected[0])
        request_id = int(item['values'][0])
        
        # Находим заявку в списке
        request = None
        for r in self.requests:
            if r['requestID'] == request_id:
                request = r
                break
        
        if not request:
            return
        
        # Создаём окно деталей
        detail_win = tk.Toplevel(self.root)
        detail_win.title(f"Заявка №{request_id}")
        detail_win.geometry("600x500")
        detail_win.transient(self.root)
        
        # Основной фрейм
        main_frame = ttk.Frame(detail_win, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Информация о заявке
        info_frame = ttk.LabelFrame(main_frame, text="Информация о заявке", padding="10")
        info_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(info_frame, text=f"Номер: {request['requestID']}").pack(anchor="w")
        ttk.Label(info_frame, text=f"Дата создания: {request['startDate']}").pack(anchor="w")
        ttk.Label(info_frame, text=f"Автомобиль: {request['carType']} {request['carModel']}").pack(anchor="w")
        ttk.Label(info_frame, text=f"Проблема: {request['problemDescryption']}").pack(anchor="w")
        ttk.Label(info_frame, text=f"Статус: {request['requestStatus']}").pack(anchor="w")
        
        master_name = self.get_user_name(request['masterID']) if request['masterID'] else 'Не назначен'
        ttk.Label(info_frame, text=f"Мастер: {master_name}").pack(anchor="w")
        
        client_name = self.get_user_name(request['clientID'])
        ttk.Label(info_frame, text=f"Клиент: {client_name}").pack(anchor="w")
        
        if request['completionDate']:
            ttk.Label(info_frame, text=f"Дата завершения: {request['completionDate']}").pack(anchor="w")
        
        # Комментарии
        comments_frame = ttk.LabelFrame(main_frame, text="Комментарии", padding="10")
        comments_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Текстовое поле для комментариев
        comments_text = tk.Text(comments_frame, height=8, state=tk.DISABLED)
        comments_text.pack(fill=tk.BOTH, expand=True)
        
        # Загружаем комментарии к этой заявке
        comments_text.config(state=tk.NORMAL)
        comments_text.delete(1.0, tk.END)
        request_comments = [c for c in self.comments if c['requestID'] == request_id]
        for c in request_comments:
            author = self.get_user_name(c['masterID'])
            comments_text.insert(tk.END, f"[{author}]: {c['message']}\n{'-'*40}\n")
        if not request_comments:
            comments_text.insert(tk.END, "Нет комментариев.")
        comments_text.config(state=tk.DISABLED)
        
        # Добавление нового комментария
        if self.current_user['type'] in ('Автомеханик', 'Менеджер'):
            add_frame = ttk.Frame(main_frame)
            add_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(add_frame, text="Новый комментарий:").pack(anchor="w")
            self.comment_entry = ttk.Entry(add_frame, width=50)
            self.comment_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
            
            def add_comment():
                message = self.comment_entry.get().strip()
                if not message:
                    messagebox.showwarning("Предупреждение", "Комментарий не может быть пустым.")
                    return
                
                new_id = max([c['commentID'] for c in self.comments]) + 1 if self.comments else 1
                new_comment = {
                    'commentID': new_id,
                    'message': message,
                    'masterID': self.current_user['userID'],
                    'requestID': request_id
                }
                self.comments.append(new_comment)
                
                # Обновляем отображение комментариев
                comments_text.config(state=tk.NORMAL)
                comments_text.insert(tk.END, f"[{self.current_user['fio']}]: {message}\n{'-'*40}\n")
                comments_text.config(state=tk.DISABLED)
                self.comment_entry.delete(0, tk.END)
                
                messagebox.showinfo("Успех", "Комментарий добавлен.")
            
            ttk.Button(add_frame, text="Добавить", command=add_comment).pack(side=tk.RIGHT)
        
        # Кнопка "Назад"
        ttk.Button(main_frame, text="Назад", command=detail_win.destroy).pack(pady=10)
    
    # ==================================================================
    # 2.5. СТАТИСТИКА
    # ==================================================================
    
    def show_stats(self):
        """Показывает окно со статистикой."""
        # Расчёт статистики
        total = len(self.requests)
        completed = 0
        total_days = 0
        problem_stats = {}
        
        for req in self.requests:
            if req['requestStatus'] == 'Готова к выдаче' and req['completionDate']:
                completed += 1
                try:
                    start = datetime.strptime(req['startDate'], '%Y-%m-%d')
                    end = datetime.strptime(req['completionDate'], '%Y-%m-%d')
                    total_days += (end - start).days
                except (ValueError, TypeError):
                    pass
            
            # Статистика по проблемам (первые слова)
            problem_words = req['problemDescryption'].split()
            if problem_words:
                key = problem_words[0]  # Группируем по первому слову
                problem_stats[key] = problem_stats.get(key, 0) + 1
        
        avg_time = total_days / completed if completed > 0 else 0
        
        # Окно статистики
        stats_win = tk.Toplevel(self.root)
        stats_win.title("Статистика работы сервиса")
        stats_win.geometry("400x300")
        stats_win.transient(self.root)
        
        frame = ttk.Frame(stats_win, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Статистика заявок", font=("Arial", 14, "bold")).pack(pady=10)
        
        ttk.Label(frame, text=f"Всего заявок: {total}").pack(anchor="w", pady=2)
        ttk.Label(frame, text=f"Выполнено заявок: {completed}").pack(anchor="w", pady=2)
        ttk.Label(frame, text=f"Среднее время ремонта: {avg_time:.1f} дней").pack(anchor="w", pady=2)
        
        ttk.Label(frame, text="\nСтатистика по проблемам:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 5))
        
        # Сортируем и показываем топ проблем
        sorted_problems = sorted(problem_stats.items(), key=lambda x: x[1], reverse=True)
        for prob, count in sorted_problems[:5]:  # Топ-5
            ttk.Label(frame, text=f"  {prob}: {count}").pack(anchor="w")
        
        ttk.Button(frame, text="Закрыть", command=stats_win.destroy).pack(pady=20)


# ======================================================================
# 3. ЗАПУСК ПРИЛОЖЕНИЯ
# ======================================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoServiceApp(root)
    root.mainloop()