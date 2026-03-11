import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from models import Request, Comment
from data import requests, users, comments, load_data
import qrcode
from io import BytesIO
from PIL import Image, ImageTk

class App:
    # Коричневая цветовая схема
    COLORS = {
        'bg_primary': '#3E2723',        # Тёмно-коричневый фон
        'bg_secondary': '#5D4037',       # Средне-коричневый
        'bg_card': '#4E342E',            # Коричневый для карточек
        'accent': '#8D6E63',              # Светло-коричневый акцент
        'accent_hover': '#A1887F',        # Светлее при наведении
        'accent_light': '#EFEBE9',        # Очень светлый коричневый
        'success': '#6D4C41',              # Коричневый для успеха
        'success_hover': '#8D6E63',
        'warning': '#BF360C',              # Терракотовый
        'warning_hover': '#D84315',
        'danger': '#B71C1C',               # Тёмно-красный
        'danger_hover': '#C62828',
        'text_primary': '#FFFFFF',        # Белый текст
        'text_secondary': '#D7CCC8',       # Светло-бежевый текст
        'border': '#6D4C41',               # Границы
        'hover': '#5D4037'                  # Ховер эффект
    }
    
    # Цвета статусов (в коричневых тонах)
    STATUS_COLORS = {
        'Новая заявка': '#8D6E63',      # Светло-коричневый
        'В процессе ремонта': '#BF360C',  # Терракотовый
        'Ожидание запчастей': '#B71C1C',   # Тёмно-красный
        'Готова к выдаче': '#6D4C41',      # Коричневый
        'Завершена': '#4E342E'            # Тёмно-коричневый
    }

    def __init__(self):
        load_data()
        self.current_user = None
        self.window = tk.Tk()
        self.window.title("Автосервис - Коричневый стиль")
        self.window.geometry("1200x700")
        self.window.configure(bg=self.COLORS['bg_primary'])
        self.window.resizable(True, True)
        
        # Центрирование окна
        self.center_window()
        
        # Настройка стилей
        self.setup_styles()
        
        self.show_login()
        self.window.mainloop()
    
    def center_window(self):
        """Центрирование окна на экране"""
        self.window.update_idletasks()
        width = 1200
        height = 700
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_styles(self):
        """Настройка стилей ttk"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Стиль для Treeview
        style.configure('Treeview',
                       background=self.COLORS['bg_card'],
                       foreground=self.COLORS['text_primary'],
                       fieldbackground=self.COLORS['bg_card'],
                       borderwidth=0,
                       rowheight=40,
                       font=('Arial', 10))
        
        style.configure('Treeview.Heading',
                       background=self.COLORS['bg_secondary'],
                       foreground=self.COLORS['text_primary'],
                       borderwidth=0,
                       font=('Arial', 10, 'bold'))
        
        style.map('Treeview',
                  background=[('selected', self.COLORS['accent'])])
    
    def clear_window(self):
        for widget in self.window.winfo_children():
            widget.destroy()
    
    def create_sidebar(self, parent):
        """Создание боковой панели навигации"""
        sidebar = tk.Frame(parent, bg=self.COLORS['bg_secondary'], width=200)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)
        
        # Логотип в боковой панели
        logo_frame = tk.Frame(sidebar, bg=self.COLORS['accent'], height=100)
        logo_frame.pack(fill='x')
        logo_frame.pack_propagate(False)
        
        tk.Label(logo_frame, text="🔧", font=('Arial', 30),
                bg=self.COLORS['accent'],
                fg=self.COLORS['text_primary']).pack(expand=True)
        
        tk.Label(logo_frame, text="АВТОСЕРВИС",
                font=('Arial', 12, 'bold'),
                bg=self.COLORS['accent'],
                fg=self.COLORS['text_primary']).pack()
        
        # Информация о пользователе в боковой панели
        if self.current_user:
            user_info = tk.Frame(sidebar, bg=self.COLORS['bg_secondary'])
            user_info.pack(fill='x', pady=20)
            
            tk.Label(user_info, text=f"👤 {self.current_user['name']}",
                    font=('Arial', 11),
                    bg=self.COLORS['bg_secondary'],
                    fg=self.COLORS['text_primary']).pack(pady=5)
            
            tk.Label(user_info, text=f"📌 {self.current_user['role']}",
                    font=('Arial', 10),
                    bg=self.COLORS['bg_secondary'],
                    fg=self.COLORS['text_secondary']).pack()
        
        return sidebar
    
    def create_header(self, parent, title):
        """Создание заголовка страницы"""
        header = tk.Frame(parent, bg=self.COLORS['accent'], height=60)
        header.pack(fill='x', side='top')
        header.pack_propagate(False)
        
        tk.Label(header, text=title, 
                font=('Arial', 18, 'bold'),
                bg=self.COLORS['accent'],
                fg=self.COLORS['text_primary']).pack(pady=15)
        
        return header
    
    def create_card(self, parent, **kwargs):
        """Создание карточки-контейнера"""
        card = tk.Frame(parent, bg=self.COLORS['bg_card'], relief='raised', borderwidth=1)
        card.pack(fill='both', expand=True, padx=20, pady=10, **kwargs)
        return card
    
    def create_button(self, parent, text, command, width=25, style='primary'):
        """Создание стилизованной кнопки"""
        if style == 'primary':
            bg = self.COLORS['accent']
            fg = self.COLORS['text_primary']
        elif style == 'success':
            bg = self.COLORS['success']
            fg = self.COLORS['text_primary']
        elif style == 'danger':
            bg = self.COLORS['danger']
            fg = self.COLORS['text_primary']
        else:
            bg = self.COLORS['bg_secondary']
            fg = self.COLORS['text_primary']
        
        btn = tk.Button(parent, text=text, command=command, width=width,
                       bg=bg, fg=fg, font=('Arial', 11, 'bold'),
                       relief='flat', padx=15, pady=8,
                       activebackground=self.COLORS['accent_hover'],
                       activeforeground=self.COLORS['text_primary'],
                       cursor='hand2')
        btn.pack(pady=5)
        
        # Эффект при наведении
        def on_enter(e):
            btn['bg'] = self.COLORS['accent_hover']
        def on_leave(e):
            btn['bg'] = bg
        
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        
        return btn
    
    def show_login(self):
        self.clear_window()
        
        # Основной контейнер
        main_frame = tk.Frame(self.window, bg=self.COLORS['bg_primary'])
        main_frame.pack(fill='both', expand=True)
        
        # Центральный контейнер для формы входа
        center_frame = tk.Frame(main_frame, bg=self.COLORS['bg_primary'])
        center_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Карточка входа
        card = tk.Frame(center_frame, bg=self.COLORS['bg_card'], 
                       highlightbackground=self.COLORS['border'],
                       highlightthickness=2, padx=40, pady=40)
        card.pack()
        
        tk.Label(card, text="🔧 АВТОСЕРВИС", 
                font=('Arial', 20, 'bold'),
                bg=self.COLORS['bg_card'],
                fg=self.COLORS['text_primary']).pack(pady=10)
        
        tk.Label(card, text="ВХОД В СИСТЕМУ", 
                font=('Arial', 14),
                bg=self.COLORS['bg_card'],
                fg=self.COLORS['text_secondary']).pack(pady=10)
        
        # Поля ввода
        input_frame = tk.Frame(card, bg=self.COLORS['bg_card'])
        input_frame.pack(pady=20)
        
        tk.Label(input_frame, text="Логин:", 
                font=('Arial', 12),
                bg=self.COLORS['bg_card'],
                fg=self.COLORS['text_primary'],
                anchor='w').pack(fill='x', pady=5)
        
        self.login_entry = tk.Entry(input_frame, font=('Arial', 12), width=30,
                                   relief='flat', bg=self.COLORS['bg_secondary'],
                                   fg=self.COLORS['text_primary'],
                                   insertbackground=self.COLORS['text_primary'])
        self.login_entry.pack(pady=5, ipady=5)
        
        tk.Label(input_frame, text="Пароль:", 
                font=('Arial', 12),
                bg=self.COLORS['bg_card'],
                fg=self.COLORS['text_primary'],
                anchor='w').pack(fill='x', pady=5)
        
        self.pass_entry = tk.Entry(input_frame, font=('Arial', 12), width=30,
                                  show='*', relief='flat', bg=self.COLORS['bg_secondary'],
                                  fg=self.COLORS['text_primary'],
                                  insertbackground=self.COLORS['text_primary'])
        self.pass_entry.pack(pady=5, ipady=5)
        self.pass_entry.bind('<Return>', lambda e: self.try_login())
        
        # Кнопка входа
        self.create_button(card, "🚀 Войти", self.try_login, width=30)
        
        # Подсказка
        tk.Label(card, text="💡 login1 / pass1", 
                font=('Arial', 9),
                bg=self.COLORS['bg_card'],
                fg=self.COLORS['text_secondary']).pack(pady=10)
    
    def try_login(self):
        for user in users:
            if user["login"] == self.login_entry.get() and user["password"] == self.pass_entry.get():
                self.current_user = user
                self.show_main_menu()
                return
        messagebox.showerror("❌ Ошибка", "Неверный логин или пароль")
    
    def show_main_menu(self):
        self.clear_window()
        
        # Создаем боковую панель
        sidebar = self.create_sidebar(self.window)
        
        # Основной контент
        content = tk.Frame(self.window, bg=self.COLORS['bg_primary'])
        content.pack(side='left', fill='both', expand=True)
        
        # Заголовок
        self.create_header(content, "ГЛАВНОЕ МЕНЮ")
        
        # Контейнер для кнопок в 2 ряда
        menu_frame = tk.Frame(content, bg=self.COLORS['bg_primary'])
        menu_frame.pack(expand=True, padx=30, pady=30)
        
        # Верхний ряд кнопок
        top_frame = tk.Frame(menu_frame, bg=self.COLORS['bg_primary'])
        top_frame.pack(fill='both', expand=True, pady=10)
        
        # Нижний ряд кнопок
        bottom_frame = tk.Frame(menu_frame, bg=self.COLORS['bg_primary'])
        bottom_frame.pack(fill='both', expand=True, pady=10)
        
        # Определяем кнопки для разных ролей
        all_buttons = [
            ("📁 ВСЕ ЗАЯВКИ", self.show_all_requests, self.COLORS['accent']),
            ("➕ НОВАЯ ЗАЯВКА", self.add_request, self.COLORS['success']),
            ("🔍 ПОИСК", self.show_search, self.COLORS['warning']),
            ("📊 СТАТИСТИКА", self.show_stats, self.COLORS['bg_secondary']),
        ]
        
        if self.current_user["role"] == "Автомеханик":
            all_buttons.insert(2, ("🔧 МОИ ЗАЯВКИ", self.show_my_requests, self.COLORS['accent']))
        
        # Распределяем кнопки по рядам
        mid = len(all_buttons) // 2
        top_buttons = all_buttons[:mid]
        bottom_buttons = all_buttons[mid:]
        
        # Создаем кнопки в верхнем ряду
        for text, cmd, color in top_buttons:
            btn_frame = tk.Frame(top_frame, bg=self.COLORS['bg_primary'])
            btn_frame.pack(side='left', expand=True, fill='both', padx=10)
            
            btn = tk.Button(btn_frame, text=text, command=cmd,
                           bg=color, fg=self.COLORS['text_primary'],
                           font=('Arial', 14, 'bold'),
                           relief='flat', padx=20, pady=30,
                           activebackground=self.COLORS['accent_hover'],
                           cursor='hand2')
            btn.pack(expand=True, fill='both')
        
        # Создаем кнопки в нижнем ряду
        for text, cmd, color in bottom_buttons:
            btn_frame = tk.Frame(bottom_frame, bg=self.COLORS['bg_primary'])
            btn_frame.pack(side='left', expand=True, fill='both', padx=10)
            
            btn = tk.Button(btn_frame, text=text, command=cmd,
                           bg=color, fg=self.COLORS['text_primary'],
                           font=('Arial', 14, 'bold'),
                           relief='flat', padx=20, pady=30,
                           activebackground=self.COLORS['accent_hover'],
                           cursor='hand2')
            btn.pack(expand=True, fill='both')
        
        # Кнопка выхода внизу
        exit_frame = tk.Frame(content, bg=self.COLORS['bg_primary'])
        exit_frame.pack(fill='x', pady=20)
        
        self.create_button(exit_frame, "🚪 ВЫХОД", self.window.quit, style='danger')
    
    def show_requests_list(self, title, req_list):
        self.clear_window()
        
        # Боковая панель
        sidebar = self.create_sidebar(self.window)
        
        # Основной контент
        content = tk.Frame(self.window, bg=self.COLORS['bg_primary'])
        content.pack(side='left', fill='both', expand=True)
        
        # Заголовок
        self.create_header(content, title)
        
        # Кнопка назад
        nav_frame = tk.Frame(content, bg=self.COLORS['bg_primary'])
        nav_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Button(nav_frame, text="← Назад в меню", command=self.show_main_menu,
                 bg=self.COLORS['bg_secondary'], fg=self.COLORS['text_primary'],
                 font=('Arial', 10, 'bold'), relief='flat',
                 padx=15, pady=5, cursor='hand2').pack(anchor='w')
        
        # Список заявок
        list_frame = self.create_card(content)
        
        if not req_list:
            tk.Label(list_frame, text="📭 Нет заявок",
                    font=('Arial', 14),
                    bg=self.COLORS['bg_card'],
                    fg=self.COLORS['text_secondary']).pack(pady=50)
            return
        
        # Создаём Treeview для красивого отображения
        columns = ('ID', 'Дата', 'Авто', 'Статус')
        tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Настройка заголовков
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor='center')
        
        tree.column('Авто', width=200)
        tree.column('Статус', width=150)
        
        # Добавление данных с цветовой индикацией
        for req in req_list:
            status_color = self.STATUS_COLORS.get(req.status, '#7F8C8D')
            tree.insert('', 'end', values=(
                req.id, 
                req.start_date, 
                f"{req.car_type} {req.car_model}",
                req.status
            ), tags=(req.status,))
        
        # Настройка цветов для статусов
        for status, color in self.STATUS_COLORS.items():
            tree.tag_configure(status, background=f'{color}40')  # 40 = прозрачность
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)
        
        self.current_req_list = req_list
        self.current_tree = tree
        
        # Кнопка просмотра
        btn_frame = tk.Frame(content, bg=self.COLORS['bg_primary'])
        btn_frame.pack(pady=15)
        
        self.create_button(btn_frame, "👁 Просмотреть", self.show_selected_request)
    
    def show_selected_request(self):
        try:
            selection = self.current_tree.selection()
            if selection:
                item = self.current_tree.item(selection[0])
                req_id = int(item['values'][0])
                for req in self.current_req_list:
                    if req.id == req_id:
                        self.show_request_details(req)
                        return
        except:
            messagebox.showerror("Ошибка", "Выберите заявку")
    
    def show_request_details(self, req):
        win = tk.Toplevel(self.window)
        win.title(f"Заявка №{req.id}")
        win.geometry("550x600")
        win.configure(bg=self.COLORS['bg_primary'])
        win.resizable(False, False)
        
        # Центрирование окна
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (550 // 2)
        y = (win.winfo_screenheight() // 2) - (600 // 2)
        win.geometry(f'+{x}+{y}')
        
        # Заголовок
        header = tk.Frame(win, bg=self.COLORS['accent'])
        header.pack(fill='x')
        tk.Label(header, text=f"📄 ЗАЯВКА №{req.id}",
                font=('Arial', 16, 'bold'),
                bg=self.COLORS['accent'],
                fg=self.COLORS['text_primary']).pack(pady=15)
        
        # Контейнер с информацией
        info_frame = tk.Frame(win, bg=self.COLORS['bg_card'])
        info_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Информация о заявке
        details = [
            ("📅 Дата:", req.start_date),
            ("🚗 Авто:", f"{req.car_type} {req.car_model}"),
            ("⚠️ Проблема:", req.problem),
            ("📊 Статус:", req.status),
            ("👤 Клиент:", f"{req.client_name}"),
            ("📞 Телефон:", req.client_phone),
        ]
        
        if req.master_id:
            master = next((u for u in users if u.get("id") == req.master_id), {})
            details.append(("🔧 Механик:", master.get('name', 'Неизвестно')))
        
        if req.parts:
            details.append(("🔩 Запчасти:", req.parts))
        
        if req.end_date:
            details.append(("📅 Срок до:", req.end_date))
        
        # Отображение информации
        for label, value in details:
            row = tk.Frame(info_frame, bg=self.COLORS['bg_card'])
            row.pack(fill='x', pady=5)
            tk.Label(row, text=label, font=('Arial', 11, 'bold'),
                    bg=self.COLORS['bg_card'],
                    fg=self.COLORS['text_primary'],
                    width=15, anchor='w').pack(side='left')
            tk.Label(row, text=value, font=('Arial', 11),
                    bg=self.COLORS['bg_card'],
                    fg=self.COLORS['text_secondary']).pack(side='left', fill='x', expand=True)
        
        # Комментарии
        comm_frame = tk.LabelFrame(info_frame, text="💬 Комментарии",
                                  font=('Arial', 12, 'bold'),
                                  bg=self.COLORS['bg_card'],
                                  fg=self.COLORS['text_primary'])
        comm_frame.pack(fill='both', expand=True, pady=15)
        
        comms = [c for c in comments if c.request_id == req.id]
        if comms:
            for c in comms:
                comm_row = tk.Frame(comm_frame, bg=self.COLORS['bg_secondary'], relief='flat')
                comm_row.pack(fill='x', padx=5, pady=3)
                tk.Label(comm_row, text=f"{c.master_name}:",
                        font=('Arial', 10, 'bold'),
                        bg=self.COLORS['bg_secondary'],
                        fg=self.COLORS['accent']).pack(anchor='w')
                tk.Label(comm_row, text=c.text,
                        font=('Arial', 10),
                        bg=self.COLORS['bg_secondary'],
                        fg=self.COLORS['text_primary']).pack(anchor='w')
        else:
            tk.Label(comm_frame, text="Нет комментариев",
                    font=('Arial', 10),
                    bg=self.COLORS['bg_card'],
                    fg=self.COLORS['text_secondary']).pack(pady=10)
        
        # Кнопки действий
        btn_frame = tk.Frame(win, bg=self.COLORS['bg_primary'])
        btn_frame.pack(fill='x', pady=15)
        
        if self.current_user["role"] == "Автомеханик":
            self.create_button(btn_frame, "🔄 Изменить статус", 
                              lambda: self.change_status(req))
            tk.Button(btn_frame, text="🔩 Добавить запчасти",
                     command=lambda: self.add_parts(req),
                     bg=self.COLORS['warning'], fg=self.COLORS['text_primary'],
                     font=('Arial', 10, 'bold'), relief='flat',
                     padx=10, pady=5, cursor='hand2').pack(side='left', padx=5)
            tk.Button(btn_frame, text="💬 Комментарий",
                     command=lambda: self.add_comment(req),
                     bg=self.COLORS['bg_secondary'], fg=self.COLORS['text_primary'],
                     font=('Arial', 10, 'bold'), relief='flat',
                     padx=10, pady=5, cursor='hand2').pack(side='left', padx=5)
        
        elif self.current_user["role"] == "Менеджер качества":
            tk.Button(btn_frame, text="📅 Продлить срок",
                     command=lambda: self.extend_deadline(req),
                     bg=self.COLORS['warning'], fg=self.COLORS['text_primary'],
                     font=('Arial', 10, 'bold'), relief='flat',
                     padx=10, pady=5, cursor='hand2').pack(side='left', padx=5)
            tk.Button(btn_frame, text="👥 Привлечь механика",
                     command=lambda: self.assign_additional_mechanic(req),
                     bg=self.COLORS['accent'], fg=self.COLORS['text_primary'],
                     font=('Arial', 10, 'bold'), relief='flat',
                     padx=10, pady=5, cursor='hand2').pack(side='left', padx=5)
            tk.Button(btn_frame, text="📱 QR-код отзыва",
                     command=lambda: self.show_qr_code(req),
                     bg=self.COLORS['success'], fg=self.COLORS['text_primary'],
                     font=('Arial', 10, 'bold'), relief='flat',
                     padx=10, pady=5, cursor='hand2').pack(side='left', padx=5)
        
        elif self.current_user["role"] in ["Оператор", "Менеджер"] and not req.master_id:
            self.create_button(btn_frame, "👤 Назначить механика",
                              lambda: self.assign_master(req))
        
        tk.Button(btn_frame, text="❌ Закрыть", command=win.destroy,
                 bg=self.COLORS['danger'], fg=self.COLORS['text_primary'],
                 font=('Arial', 10, 'bold'), relief='flat',
                 padx=15, pady=5, cursor='hand2').pack(side='right', padx=5)
    
    def add_comment_system(self, req, text):
        c = Comment()
        c.id = len(comments) + 1
        c.text = text
        c.master_name = self.current_user["name"]
        c.request_id = req.id
        comments.append(c)
    
    def change_status(self, req):
        win = tk.Toplevel(self.window)
        win.title("Изменить статус")
        win.geometry("350x400")
        win.configure(bg=self.COLORS['bg_primary'])
        
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (350 // 2)
        y = (win.winfo_screenheight() // 2) - (400 // 2)
        win.geometry(f'+{x}+{y}')
        
        tk.Label(win, text=f"Заявка №{req.id}",
                font=('Arial', 14, 'bold'),
                bg=self.COLORS['bg_primary'],
                fg=self.COLORS['text_primary']).pack(pady=15)
        
        statuses = ["Новая заявка", "В процессе ремонта", "Ожидание запчастей", 
                   "Готова к выдаче", "Завершена"]
        var = tk.StringVar(value=req.status)
        
        for s in statuses:
            color = self.STATUS_COLORS.get(s, '#7F8C8D')
            rb = tk.Radiobutton(win, text=s, variable=var, value=s,
                               bg=self.COLORS['bg_primary'],
                               fg=self.COLORS['text_primary'],
                               selectcolor=color,
                               font=('Arial', 11),
                               anchor='w')
            rb.pack(fill='x', padx=30, pady=3)
        
        def save():
            if var.get():
                req.status = var.get()
                if var.get() == "Завершена":
                    req.end_date = datetime.datetime.now().strftime("%Y-%m-%d")
                self.add_comment_system(req, f"Статус изменен на: {var.get()}")
                messagebox.showinfo("✅ Успех", "Статус изменен")
                win.destroy()
        
        tk.Button(win, text="💾 Сохранить", command=save,
                 bg=self.COLORS['success'], fg=self.COLORS['text_primary'],
                 font=('Arial', 12, 'bold'), relief='flat',
                 padx=20, pady=8, cursor='hand2').pack(pady=20)
    
    def add_parts(self, req):
        win = tk.Toplevel(self.window)
        win.title("Добавить запчасти")
        win.geometry("400x200")
        win.configure(bg=self.COLORS['bg_primary'])
        
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (400 // 2)
        y = (win.winfo_screenheight() // 2) - (200 // 2)
        win.geometry(f'+{x}+{y}')
        
        tk.Label(win, text=f"Заявка №{req.id}",
                font=('Arial', 14, 'bold'),
                bg=self.COLORS['bg_primary'],
                fg=self.COLORS['text_primary']).pack(pady=15)
        
        entry = tk.Entry(win, font=('Arial', 12), width=40,
                        relief='flat', bg=self.COLORS['bg_secondary'],
                        fg=self.COLORS['text_primary'],
                        insertbackground=self.COLORS['text_primary'])
        entry.pack(pady=10, ipady=5)
        
        def save():
            if entry.get():
                req.parts = (req.parts + "; " + entry.get()) if req.parts else entry.get()
                self.add_comment_system(req, f"Добавлены запчасти: {entry.get()}")
                messagebox.showinfo("✅ Успех", "Запчасти добавлены")
                win.destroy()
        
        tk.Button(win, text="➕ Добавить", command=save,
                 bg=self.COLORS['accent'], fg=self.COLORS['text_primary'],
                 font=('Arial', 12, 'bold'), relief='flat',
                 padx=20, pady=8, cursor='hand2').pack(pady=10)
    
    def add_comment(self, req):
        win = tk.Toplevel(self.window)
        win.title("Добавить комментарий")
        win.geometry("400x200")
        win.configure(bg=self.COLORS['bg_primary'])
        
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (400 // 2)
        y = (win.winfo_screenheight() // 2) - (200 // 2)
        win.geometry(f'+{x}+{y}')
        
        tk.Label(win, text=f"Заявка №{req.id}",
                font=('Arial', 14, 'bold'),
                bg=self.COLORS['bg_primary'],
                fg=self.COLORS['text_primary']).pack(pady=15)
        
        entry = tk.Entry(win, font=('Arial', 12), width=40,
                        relief='flat', bg=self.COLORS['bg_secondary'],
                        fg=self.COLORS['text_primary'],
                        insertbackground=self.COLORS['text_primary'])
        entry.pack(pady=10, ipady=5)
        
        def save():
            if entry.get():
                self.add_comment_system(req, entry.get())
                messagebox.showinfo("✅ Успех", "Комментарий добавлен")
                win.destroy()
        
        tk.Button(win, text="💬 Добавить", command=save,
                 bg=self.COLORS['accent'], fg=self.COLORS['text_primary'],
                 font=('Arial', 12, 'bold'), relief='flat',
                 padx=20, pady=8, cursor='hand2').pack(pady=10)
    
    def assign_master(self, req):
        win = tk.Toplevel(self.window)
        win.title("Назначить механика")
        win.geometry("350x300")
        win.configure(bg=self.COLORS['bg_primary'])
        
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (350 // 2)
        y = (win.winfo_screenheight() // 2) - (300 // 2)
        win.geometry(f'+{x}+{y}')
        
        tk.Label(win, text=f"Заявка №{req.id}",
                font=('Arial', 14, 'bold'),
                bg=self.COLORS['bg_primary'],
                fg=self.COLORS['text_primary']).pack(pady=15)
        
        masters = [u for u in users if u["role"] == "Автомеханик"]
        var = tk.StringVar()
        
        for m in masters:
            rb = tk.Radiobutton(win, text=m['name'], variable=var, 
                               value=m.get("id", 0),
                               bg=self.COLORS['bg_primary'],
                               fg=self.COLORS['text_primary'],
                               selectcolor=self.COLORS['accent'],
                               font=('Arial', 11),
                               anchor='w')
            rb.pack(fill='x', padx=30, pady=3)
        
        def save():
            try:
                req.master_id = int(var.get())
                self.add_comment_system(req, "Назначен механик")
                messagebox.showinfo("✅ Успех", "Механик назначен")
                win.destroy()
            except:
                messagebox.showerror("❌ Ошибка", "Выберите механика")
        
        tk.Button(win, text="👤 Назначить", command=save,
                 bg=self.COLORS['success'], fg=self.COLORS['text_primary'],
                 font=('Arial', 12, 'bold'), relief='flat',
                 padx=20, pady=8, cursor='hand2').pack(pady=20)
    
    def extend_deadline(self, req):
        win = tk.Toplevel(self.window)
        win.title("Продлить срок")
        win.geometry("350x250")
        win.configure(bg=self.COLORS['bg_primary'])
        
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (350 // 2)
        y = (win.winfo_screenheight() // 2) - (250 // 2)
        win.geometry(f'+{x}+{y}')
        
        tk.Label(win, text=f"Заявка №{req.id}",
                font=('Arial', 14, 'bold'),
                bg=self.COLORS['bg_primary'],
                fg=self.COLORS['text_primary']).pack(pady=15)
        
        tk.Label(win, text=f"Текущая дата: {req.end_date or 'не указана'}",
                bg=self.COLORS['bg_primary'],
                fg=self.COLORS['text_secondary']).pack()
        
        tk.Label(win, text="Новая дата (ГГГГ-ММ-ДД):",
                bg=self.COLORS['bg_primary'],
                fg=self.COLORS['text_primary']).pack(pady=10)
        
        entry = tk.Entry(win, font=('Arial', 12), width=20,
                        relief='flat', bg=self.COLORS['bg_secondary'],
                        fg=self.COLORS['text_primary'],
                        insertbackground=self.COLORS['text_primary'])
        entry.pack(pady=5, ipady=5)
        
        def save():
            new_date = entry.get()
            if new_date:
                req.end_date = new_date
                self.add_comment_system(req, f"Срок продлён до {new_date} (менеджер качества)")
                messagebox.showinfo("✅ Успех", "Срок изменён")
                win.destroy()
        
        tk.Button(win, text="💾 Сохранить", command=save,
                 bg=self.COLORS['success'], fg=self.COLORS['text_primary'],
                 font=('Arial', 12, 'bold'), relief='flat',
                 padx=20, pady=8, cursor='hand2').pack(pady=15)
    
    def assign_additional_mechanic(self, req):
        win = tk.Toplevel(self.window)
        win.title("Привлечь механика")
        win.geometry("350x300")
        win.configure(bg=self.COLORS['bg_primary'])
        
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (350 // 2)
        y = (win.winfo_screenheight() // 2) - (300 // 2)
        win.geometry(f'+{x}+{y}')
        
        tk.Label(win, text=f"Заявка №{req.id}",
                font=('Arial', 14, 'bold'),
                bg=self.COLORS['bg_primary'],
                fg=self.COLORS['text_primary']).pack(pady=15)
        
        mechanics = [u for u in users if u["role"] == "Автомеханик"]
        var = tk.StringVar()
        
        for m in mechanics:
            rb = tk.Radiobutton(win, text=m['name'], variable=var, 
                               value=m['name'],
                               bg=self.COLORS['bg_primary'],
                               fg=self.COLORS['text_primary'],
                               selectcolor=self.COLORS['accent'],
                               font=('Arial', 11),
                               anchor='w')
            rb.pack(fill='x', padx=30, pady=3)
        
        def save():
            mech_name = var.get()
            if mech_name:
                self.add_comment_system(req, f"Привлечён механик: {mech_name}")
                messagebox.showinfo("✅ Успех", f"Механик {mech_name} привлечён")
                win.destroy()
        
        tk.Button(win, text="👥 Привлечь", command=save,
                 bg=self.COLORS['accent'], fg=self.COLORS['text_primary'],
                 font=('Arial', 12, 'bold'), relief='flat',
                 padx=20, pady=8, cursor='hand2').pack(pady=20)
    
    def show_qr_code(self, req):
        url = "https://docs.google.com/forms/d/e/1FAIpQLSdhZcExx6LSIXxk0ub55mSu-WIh23WYdGG9HY5EZhLDo7P8eA/viewform"
        
        qr = qrcode.make(url)
        
        img_bytes = BytesIO()
        qr.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        pil_img = Image.open(img_bytes)
        img_tk = ImageTk.PhotoImage(pil_img)
        
        win = tk.Toplevel(self.window)
        win.title("QR-код для отзыва")
        win.geometry("350x400")
        win.configure(bg=self.COLORS['bg_primary'])
        
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (350 // 2)
        y = (win.winfo_screenheight() // 2) - (400 // 2)
        win.geometry(f'+{x}+{y}')
        
        tk.Label(win, text="⭐ Оцените качество работы",
                font=('Arial', 14, 'bold'),
                bg=self.COLORS['bg_primary'],
                fg=self.COLORS['text_primary']).pack(pady=15)
        
        label_img = tk.Label(win, image=img_tk, bg=self.COLORS['bg_primary'])
        label_img.image = img_tk
        label_img.pack(pady=15)
        
        tk.Label(win, text="📱 Отсканируйте QR-код",
                font=('Arial', 11),
                bg=self.COLORS['bg_primary'],
                fg=self.COLORS['text_secondary']).pack()
        
        tk.Button(win, text="❌ Закрыть", command=win.destroy,
                 bg=self.COLORS['danger'], fg=self.COLORS['text_primary'],
                 font=('Arial', 11, 'bold'), relief='flat',
                 padx=15, pady=5, cursor='hand2').pack(pady=15)
    
    def add_request(self):
        win = tk.Toplevel(self.window)
        win.title("Новая заявка")
        win.geometry("450x450")
        win.configure(bg=self.COLORS['bg_primary'])
        
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (450 // 2)
        y = (win.winfo_screenheight() // 2) - (450 // 2)
        win.geometry(f'+{x}+{y}')
        
        # Заголовок
        header = tk.Frame(win, bg=self.COLORS['accent'])
        header.pack(fill='x')
        tk.Label(header, text="➕ НОВАЯ ЗАЯВКА",
                font=('Arial', 16, 'bold'),
                bg=self.COLORS['accent'],
                fg=self.COLORS['text_primary']).pack(pady=15)
        
        # Форма
        form_frame = tk.Frame(win, bg=self.COLORS['bg_card'])
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        fields = ["Вид авто:", "Модель:", "Проблема:", "ФИО клиента:", "Телефон:"]
        entries = []
        
        for i, text in enumerate(fields):
            row = tk.Frame(form_frame, bg=self.COLORS['bg_card'])
            row.pack(fill='x', pady=8)
            
            tk.Label(row, text=text, font=('Arial', 11, 'bold'),
                    bg=self.COLORS['bg_card'],
                    fg=self.COLORS['text_primary'],
                    width=15, anchor='w').pack(side='left')
            
            e = tk.Entry(row, font=('Arial', 11), width=25,
                        relief='flat', bg=self.COLORS['bg_secondary'],
                        fg=self.COLORS['text_primary'],
                        insertbackground=self.COLORS['text_primary'])
            e.pack(side='left', ipady=5)
            entries.append(e)
        
        def save():
            req = Request()
            req.id = max([r.id for r in requests] + [0]) + 1
            req.start_date = datetime.datetime.now().strftime("%Y-%m-%d")
            req.car_type, req.car_model, req.problem, req.client_name, req.client_phone = [e.get() for e in entries]
            requests.append(req)
            messagebox.showinfo("✅ Успех", f"Заявка №{req.id} создана")
            win.destroy()
        
        tk.Button(win, text="💾 Создать", command=save,
                 bg=self.COLORS['success'], fg=self.COLORS['text_primary'],
                 font=('Arial', 13, 'bold'), relief='flat',
                 padx=30, pady=10, cursor='hand2').pack(pady=15)
    
    def show_search(self):
        win = tk.Toplevel(self.window)
        win.title("Поиск")
        win.geometry("650x450")
        win.configure(bg=self.COLORS['bg_primary'])
        
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (650 // 2)
        y = (win.winfo_screenheight() // 2) - (450 // 2)
        win.geometry(f'+{x}+{y}')
        
        # Заголовок
        header = tk.Frame(win, bg=self.COLORS['accent'])
        header.pack(fill='x')
        tk.Label(header, text="🔍 ПОИСК ЗАЯВОК",
                font=('Arial', 16, 'bold'),
                bg=self.COLORS['accent'],
                fg=self.COLORS['text_primary']).pack(pady=15)
        
        # Notebook
        notebook = ttk.Notebook(win)
        notebook.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Поиск по номеру
        frame1 = tk.Frame(notebook, bg=self.COLORS['bg_card'])
        notebook.add(frame1, text="📋 По номеру")
        
        tk.Label(frame1, text="Номер заявки:",
                font=('Arial', 12),
                bg=self.COLORS['bg_card'],
                fg=self.COLORS['text_primary']).pack(pady=15)
        
        id_entry = tk.Entry(frame1, font=('Arial', 12), width=20,
                           relief='flat', bg=self.COLORS['bg_secondary'],
                           fg=self.COLORS['text_primary'],
                           insertbackground=self.COLORS['text_primary'])
        id_entry.pack()
        
        def search_by_id():
            try:
                rid = int(id_entry.get())
                for req in requests:
                    if req.id == rid:
                        self.show_request_details(req)
                        win.destroy()
                        return
                messagebox.showinfo("📭 Результат", "Заявка не найдена")
            except:
                messagebox.showerror("❌ Ошибка", "Введите число")
        
        tk.Button(frame1, text="🔍 Найти", command=search_by_id,
                 bg=self.COLORS['accent'], fg=self.COLORS['text_primary'],
                 font=('Arial', 12, 'bold'), relief='flat',
                 padx=20, pady=8, cursor='hand2').pack(pady=20)
        
        # Поиск по статусу
        frame2 = tk.Frame(notebook, bg=self.COLORS['bg_card'])
        notebook.add(frame2, text="📊 По статусу")
        
        status_var = tk.StringVar()
        statuses = ["Новая заявка", "В процессе ремонта", "Ожидание запчастей", 
                   "Готова к выдаче", "Завершена"]
        
        for s in statuses:
            color = self.STATUS_COLORS.get(s, '#7F8C8D')
            rb = tk.Radiobutton(frame2, text=s, variable=status_var, value=s,
                               bg=self.COLORS['bg_card'],
                               fg=self.COLORS['text_primary'],
                               selectcolor=color,
                               font=('Arial', 11),
                               anchor='w')
            rb.pack(fill='x', padx=30, pady=3)
        
        def search_by_status():
            if not status_var.get():
                messagebox.showerror("❌ Ошибка", "Выберите статус")
                return
            found = [req for req in requests if req.status == status_var.get()]
            if found:
                res = tk.Toplevel(win)
                res.title("Результаты поиска")
                res.geometry("450x350")
                res.configure(bg=self.COLORS['bg_primary'])
                
                res.update_idletasks()
                x = (res.winfo_screenwidth() // 2) - (450 // 2)
                y = (res.winfo_screenheight() // 2) - (350 // 2)
                res.geometry(f'+{x}+{y}')
                
                lb = tk.Listbox(res, font=('Arial', 11),
                               bg=self.COLORS['bg_secondary'],
                               fg=self.COLORS['text_primary'],
                               selectbackground=self.COLORS['accent'],
                               selectforeground=self.COLORS['text_primary'])
                lb.pack(fill='both', expand=True, padx=20, pady=20)
                
                for req in found:
                    lb.insert('end', f"ID: {req.id} | {req.car_model} | {req.start_date}")
                
                def view():
                    s = lb.curselection()
                    if s:
                        self.show_request_details(found[s[0]])
                        res.destroy()
                
                tk.Button(res, text="👁 Просмотреть", command=view,
                         bg=self.COLORS['accent'], fg=self.COLORS['text_primary'],
                         font=('Arial', 11, 'bold'), relief='flat',
                         padx=15, pady=5, cursor='hand2').pack(pady=10)
            else:
                messagebox.showinfo("📭 Результат", "Заявки не найдены")
        
        tk.Button(frame2, text="🔍 Найти", command=search_by_status,
                 bg=self.COLORS['accent'], fg=self.COLORS['text_primary'],
                 font=('Arial', 12, 'bold'), relief='flat',
                 padx=20, pady=8, cursor='hand2').pack(pady=20)
    
    def show_stats(self):
        new = work = parts = ready = done = 0
        for req in requests:
            if req.status == "Новая заявка": new += 1
            elif req.status == "В процессе ремонта": work += 1
            elif req.status == "Ожидание запчастей": parts += 1
            elif req.status == "Готова к выдаче": ready += 1
            elif req.status == "Завершена": done += 1
        
        win = tk.Toplevel(self.window)
        win.title("Статистика")
        win.geometry("400x350")
        win.configure(bg=self.COLORS['bg_primary'])
        
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (400 // 2)
        y = (win.winfo_screenheight() // 2) - (350 // 2)
        win.geometry(f'+{x}+{y}')
        
        # Заголовок
        header = tk.Frame(win, bg=self.COLORS['accent'])
        header.pack(fill='x')
        tk.Label(header, text="📊 СТАТИСТИКА",
                font=('Arial', 16, 'bold'),
                bg=self.COLORS['accent'],
                fg=self.COLORS['text_primary']).pack(pady=15)
        
        # Карточки статистики
        stats_frame = tk.Frame(win, bg=self.COLORS['bg_primary'])
        stats_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        stats_data = [
            ("📁 Всего заявок", len(requests), self.COLORS['bg_secondary']),
            ("🆕 Новые", new, self.COLORS['accent']),
            ("🔧 В работе", work, self.COLORS['warning']),
            ("🔩 Ждут запчасти", parts, self.COLORS['danger']),
            ("✅ Готовы", ready, self.COLORS['success']),
            ("🏆 Завершены", done, self.COLORS['text_secondary']),
        ]
        
        for label, value, color in stats_data:
            card = tk.Frame(stats_frame, bg=color, relief='raised', borderwidth=1)
            card.pack(fill='x', pady=5)
            
            tk.Label(card, text=label, font=('Arial', 11),
                    bg=color, fg=self.COLORS['text_primary'],
                    anchor='w').pack(side='left', padx=15, pady=10)
            tk.Label(card, text=str(value), font=('Arial', 14, 'bold'),
                    bg=color, fg=self.COLORS['text_primary']).pack(side='right', padx=15, pady=10)
    
    def show_all_requests(self):
        self.show_requests_list("ВСЕ ЗАЯВКИ", requests)
    
    def show_my_requests(self):
        my_reqs = [req for req in requests if req.master_id == self.current_user.get("id")]
        self.show_requests_list("МОИ ЗАЯВКИ", my_reqs)


if __name__ == "__main__":
    App()