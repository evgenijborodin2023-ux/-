import sqlite3
import os
import shutil
from datetime import datetime
import zipfile
import json

class BackupManager:
    def __init__(self, db_name="autoservice.db", backup_dir="backups"):
        self.db_name = db_name
        self.backup_dir = backup_dir
        
        # Создаем папку для бэкапов, если её нет
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
    
    def create_backup(self, backup_type="full"):
        """Создание резервной копии"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if backup_type == "full":
            # Полный бэкап базы данных
            backup_file = os.path.join(self.backup_dir, f"autoservice_full_{timestamp}.db")
            shutil.copy2(self.db_name, backup_file)
            
            # Создаем также SQL дамп
            self.create_sql_dump(timestamp)
            
        elif backup_type == "structure":
            # Только структура
            self.create_sql_dump(timestamp, only_structure=True)
        
        elif backup_type == "data":
            # Только данные
            self.export_data_to_json(timestamp)
        
        print(f"Резервная копия создана: {backup_type} - {timestamp}")
        return timestamp
    
    def create_sql_dump(self, timestamp, only_structure=False):
        """Создание SQL дампа"""
        conn = sqlite3.connect(self.db_name)
        dump_file = os.path.join(self.backup_dir, f"autoservice_dump_{timestamp}.sql")
        
        with open(dump_file, 'w', encoding='utf-8') as f:
            for line in conn.iterdump():
                if only_structure and "INSERT INTO" in line:
                    continue
                f.write(f"{line}\n")
        
        conn.close()
        print(f"SQL дамп создан: {dump_file}")
    
    def export_data_to_json(self, timestamp):
        """Экспорт данных в JSON"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Получаем все таблицы
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        data = {}
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            data[table_name] = [dict(row) for row in rows]
        
        # Сохраняем в JSON
        json_file = os.path.join(self.backup_dir, f"autoservice_data_{timestamp}.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        conn.close()
        print(f"JSON экспорт создан: {json_file}")
    
    def restore_from_backup(self, backup_file):
        """Восстановление из резервной копии"""
        if not os.path.exists(backup_file):
            print(f"Файл бэкапа не найден: {backup_file}")
            return False
        
        # Закрываем все соединения с БД
        # Восстанавливаем файл
        shutil.copy2(backup_file, self.db_name)
        print(f"База данных восстановлена из: {backup_file}")
        return True
    
    def restore_from_sql(self, sql_file):
        """Восстановление из SQL дампа"""
        if not os.path.exists(sql_file):
            print(f"SQL файл не найден: {sql_file}")
            return False
        
        conn = sqlite3.connect(self.db_name)
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_script = f.read()
            conn.executescript(sql_script)
        
        conn.commit()
        conn.close()
        print(f"База данных восстановлена из SQL: {sql_file}")
        return True
    
    def list_backups(self):
        """Список всех резервных копий"""
        backups = []
        for file in os.listdir(self.backup_dir):
            file_path = os.path.join(self.backup_dir, file)
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                modified = datetime.fromtimestamp(os.path.getmtime(file_path))
                backups.append({
                    'file': file,
                    'size': size,
                    'modified': modified,
                    'type': file.split('_')[1] if '_' in file else 'unknown'
                })
        
        return sorted(backups, key=lambda x: x['modified'], reverse=True)
    
    def cleanup_old_backups(self, days_to_keep=30):
        """Удаление старых резервных копий"""
        cutoff = datetime.now().timestamp() - (days_to_keep * 24 * 3600)
        deleted = 0
        
        for file in os.listdir(self.backup_dir):
            file_path = os.path.join(self.backup_dir, file)
            if os.path.isfile(file_path):
                modified = os.path.getmtime(file_path)
                if modified < cutoff:
                    os.remove(file_path)
                    deleted += 1
        
        print(f"Удалено старых бэкапов: {deleted}")
        return deleted

# Пример использования
if __name__ == "__main__":
    bm = BackupManager()
    
    # Создание бэкапов
    print("Создание резервных копий:")
    bm.create_backup("full")
    bm.create_backup("structure")
    bm.create_backup("data")
    
    # Список бэкапов
    print("\nСписок резервных копий:")
    for backup in bm.list_backups():
        print(f"  {backup['file']} - {backup['size']} bytes - {backup['modified']}")
    
    # Очистка старых бэкапов (опционально)
    # bm.cleanup_old_backups(30)