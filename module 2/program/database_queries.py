import database_setup

def run_queries():
    db = database_setup.AutoServiceDB()
    db.connect()
    
    # 1. Количество заявок по статусам
    results = db.execute_query('''
        SELECT requestStatus, COUNT(*) as count
        FROM requests
        GROUP BY requestStatus
    ''')
    db.print_query_results(results, "Заявки по статусам")
    
    # 2. Среднее время ремонта
    results = db.execute_query('''
        SELECT AVG(julianday(completionDate) - julianday(startDate)) as avg_repair_days
        FROM requests
        WHERE completionDate IS NOT NULL
    ''')
    db.print_query_results(results, "Среднее время ремонта (дни)")
    
    # 3. Топ автомехаников
    results = db.execute_query('''
        SELECT u.fio, COUNT(r.requestID) as requests_count
        FROM users u
        LEFT JOIN requests r ON u.userID = r.masterID
        WHERE u.type = 'Автомеханик'
        GROUP BY u.userID, u.fio
        ORDER BY requests_count DESC
        LIMIT 5
    ''')
    db.print_query_results(results, "Топ автомехаников")
    
    # 4. Заявки с последними комментариями
    results = db.execute_query('''
        SELECT r.requestID, r.carModel, r.problemDescription, 
               c.message as last_comment, u.fio as comment_author
        FROM requests r
        LEFT JOIN comments c ON r.requestID = c.requestID
        LEFT JOIN users u ON c.masterID = u.userID
        WHERE c.commentID = (
            SELECT MAX(commentID) 
            FROM comments c2 
            WHERE c2.requestID = r.requestID
        ) OR c.commentID IS NULL
    ''')
    db.print_query_results(results, "Заявки с комментариями")
    
    # 5. Отчет по месяцам
    results = db.execute_query('''
        SELECT 
            strftime('%Y-%m', startDate) as month,
            COUNT(*) as total_requests,
            SUM(CASE WHEN requestStatus = 'Готова к выдаче' THEN 1 ELSE 0 END) as completed,
            AVG(CASE WHEN completionDate IS NOT NULL 
                THEN julianday(completionDate) - julianday(startDate) 
                ELSE NULL END) as avg_days
        FROM requests
        WHERE startDate >= '2023-01-01' 
        GROUP BY strftime('%Y-%m', startDate)
        ORDER BY month
    ''')
    db.print_query_results(results, "Отчет по месяцам")
    
    db.disconnect()

if __name__ == "__main__":
    run_queries()