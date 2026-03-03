import csv
from datetime import datetime, timedelta
import random

def generate_test_csv():
    """Генерация тестовых CSV файлов"""
    
    # Пользователи
    users = [
        [1, 'Белов А.Д.', '89210563128', 'login1', 'pass1', 'Менеджер'],
        [2, 'Харитонова М.П.', '89535078985', 'login2', 'pass2', 'Автомеханик'],
        [3, 'Сидоров П.П.', '89531234567', 'login3', 'pass3', 'Автомеханик'],
        [4, 'Козлов В.В.', '89123456789', 'login4', 'pass4', 'Автомеханик'],
        [5, 'Морозова Е.А.', '89234567890', 'login5', 'pass5', 'Менеджер'],
        [6, 'Волков Н.Н.', '89345678901', 'login6', 'pass6', 'Автомеханик'],
        [7, 'Ильина Т.Д.', '89219567841', 'login12', 'pass12', 'Заказчик'],
        [8, 'Петров И.И.', '89161234567', 'login8', 'pass8', 'Заказчик'],
        [9, 'Соколова А.С.', '89456789012', 'login9', 'pass9', 'Заказчик'],
        [10, 'Михайлов Д.Д.', '89567890123', 'login10', 'pass10', 'Заказчик']
    ]
    
    with open('inputDataUsers.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['userID', 'fio', 'phone', 'login', 'password', 'type'])
        writer.writerows(users)
    
    # Заявки
    car_models = [
        ('Легковая', 'Toyota Camry'), ('Легковая', 'Hyundai Solaris'),
        ('Грузовая', 'GAZelle'), ('Легковая', 'KIA Rio'),
        ('Мотоцикл', 'Yamaha R6'), ('Легковая', 'Lada Vesta'),
        ('Грузовая', 'MAN'), ('Легковая', 'BMW X5')
    ]
    
    problems = [
        'Отказали тормоза', 'Не заводится двигатель', 'Стук в подвеске',
        'Проблемы с электрикой', 'Течь масла', 'Скрип при повороте',
        'Не работает кондиционер', 'Вибрация на скорости'
    ]
    
    statuses = ['Новая заявка', 'В процессе ремонта', 'Готова к выдаче']
    
    requests = []
    for i in range(1, 21):  # 20 заявок
        car_type, car_model = random.choice(car_models)
        start = datetime.now() - timedelta(days=random.randint(1, 60))
        status = random.choice(statuses)
        
        completion = None
        if status == 'Готова к выдаче':
            completion = start + timedelta(days=random.randint(1, 14))
            completion = completion.strftime('%Y-%m-%d')
        
        master = random.choice([2, 3, 4, 6]) if random.random() > 0.3 else None
        client = random.choice([7, 8, 9, 10])
        
        requests.append([
            i, start.strftime('%Y-%m-%d'), car_type, car_model,
            random.choice(problems), status, completion, None,
            master, client
        ])
    
    with open('inputDataRequests.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['requestID', 'startDate', 'carType', 'carModel', 
                        'problemDescryption', 'requestStatus', 'completionDate', 
                        'repairParts', 'masterID', 'clientID'])
        writer.writerows(requests)
    
    # Комментарии
    comments = []
    comment_id = 1
    messages = [
        'Проверил, нужна замена', 'Ждем запчасти', 'Сделано', 'Клиент уведомлен',
        'Очень странно', 'Будем разбираться', 'Требуется доп. диагностика'
    ]
    
    for req_id in range(1, 21):
        # Добавляем комментарии к случайным заявкам
        if random.random() > 0.5:
            for _ in range(random.randint(1, 3)):
                comments.append([
                    comment_id, random.choice(messages),
                    random.choice([2, 3, 4, 6]), req_id
                ])
                comment_id += 1
    
    with open('inputDataComments.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['commentID', 'message', 'masterID', 'requestID'])
        writer.writerows(comments)
    
    print("✅ Тестовые CSV файлы созданы!")

if __name__ == "__main__":
    generate_test_csv()