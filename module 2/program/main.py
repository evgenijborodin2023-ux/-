import sys
import os
from database_setup import AutoServiceDB
from database_queries import run_queries
from user_management import UserManager
from backup_manager import BackupManager
from app_with_db import AutoServiceAppWithDB
import tkinter as tk

def setup_database():
    """Настройка базы данных"""
    print("=" * 50)
    print("НАСТРОЙКА БАЗЫ ДАННЫХ")
    print("=" * 50)
    
    db = AutoServiceDB()
    db.connect()
    db.create_tables()
    db.load_data_from_csv()
    db.disconnect()
    
    # Создание пользователей БД
    um = UserManager()
    um.create_users_with_roles()
    
    print("\n✅ База данных успешно настроена!\n")

def show_menu():
    """Показать меню"""
    print("\n" + "=" * 50)
    print("АВТОСЕРВИС - СИСТЕМА УПРАВЛЕНИЯ")
    print("=" * 50)
    print("1. Запустить приложение (GUI)")
    print("2. Выполнить SQL-запросы")
    print("3. Создать резервную копию")
    print("4. Восстановить из резервной копии")
    print("5. Показать список бэкапов")
    print("6. Настроить базу данных заново")
    print("0. Выход")
    print("=" * 50)

def main():
    # Первоначальная настройка БД, если её нет
    if not os.path.exists("autoservice.db"):
        setup_database()
    
    while True:
        show_menu()
        choice = input("Выберите действие: ").strip()
        
        if choice == "1":
            # Запуск GUI приложения
            print("\nЗапуск приложения...")
            root = tk.Tk()
            app = AutoServiceAppWithDB(root)
            root.mainloop()
            
        elif choice == "2":
            # Выполнение SQL-запросов
            print("\nВыполнение SQL-запросов...")
            run_queries()
            input("\nНажмите Enter для продолжения...")
            
        elif choice == "3":
            # Создание резервной копии
            bm = BackupManager()
            print("\nТипы резервных копий:")
            print("1. Полная копия (БД + данные)")
            print("2. Только структура")
            print("3. Только данные (JSON)")
            b_type = input("Выберите тип (1-3): ").strip()
            
            backup_types = {"1": "full", "2": "structure", "3": "data"}
            if b_type in backup_types:
                bm.create_backup(backup_types[b_type])
            else:
                print("Неверный выбор!")
            
        elif choice == "4":
            # Восстановление из бэкапа
            bm = BackupManager()
            backups = bm.list_backups()
            
            if not backups:
                print("Нет доступных резервных копий!")
                continue
            
            print("\nДоступные резервные копии:")
            for i, backup in enumerate(backups, 1):
                print(f"{i}. {backup['file']} ({backup['size']} bytes) - {backup['modified']}")
            
            try:
                idx = int(input("\nВыберите номер для восстановления: ")) - 1
                if 0 <= idx < len(backups):
                    backup_file = os.path.join(bm.backup_dir, backups[idx]['file'])
                    if backups[idx]['file'].endswith('.sql'):
                        bm.restore_from_sql(backup_file)
                    else:
                        bm.restore_from_backup(backup_file)
                else:
                    print("Неверный номер!")
            except ValueError:
                print("Неверный ввод!")
            
        elif choice == "5":
            # Список бэкапов
            bm = BackupManager()
            backups = bm.list_backups()
            
            if backups:
                print("\nРезервные копии:")
                for backup in backups:
                    print(f"  📁 {backup['file']}")
                    print(f"     Размер: {backup['size']} bytes")
                    print(f"     Дата: {backup['modified']}")
                    print(f"     Тип: {backup['type']}\n")
            else:
                print("Нет резервных копий!")
            
            input("\nНажмите Enter для продолжения...")
            
        elif choice == "6":
            # Перенастройка БД
            confirm = input("Это удалит все данные! Продолжить? (yes/no): ")
            if confirm.lower() == 'yes':
                if os.path.exists("autoservice.db"):
                    os.remove("autoservice.db")
                setup_database()
            
        elif choice == "0":
            print("\nДо свидания!")
            break
        
        else:
            print("Неверный выбор!")

if __name__ == "__main__":
    main()