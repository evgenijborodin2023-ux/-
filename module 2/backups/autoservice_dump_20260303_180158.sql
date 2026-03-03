BEGIN TRANSACTION;
CREATE TABLE comments (
                commentID INTEGER PRIMARY KEY,
                message TEXT NOT NULL,
                masterID INTEGER NOT NULL,
                requestID INTEGER NOT NULL,
                FOREIGN KEY (masterID) REFERENCES users(userID) ON DELETE CASCADE,
                FOREIGN KEY (requestID) REFERENCES requests(requestID) ON DELETE CASCADE
            );
INSERT INTO "comments" VALUES(1,'Проверил, нужна замена',2,3);
INSERT INTO "comments" VALUES(2,'Ждем запчасти',3,3);
INSERT INTO "comments" VALUES(3,'Сделано',3,5);
INSERT INTO "comments" VALUES(4,'Требуется доп. диагностика',3,5);
INSERT INTO "comments" VALUES(5,'Будем разбираться',4,5);
INSERT INTO "comments" VALUES(6,'Клиент уведомлен',2,6);
INSERT INTO "comments" VALUES(7,'Сделано',3,6);
INSERT INTO "comments" VALUES(8,'Будем разбираться',4,6);
INSERT INTO "comments" VALUES(9,'Ждем запчасти',4,7);
INSERT INTO "comments" VALUES(10,'Очень странно',6,7);
INSERT INTO "comments" VALUES(11,'Ждем запчасти',4,7);
INSERT INTO "comments" VALUES(12,'Сделано',6,9);
INSERT INTO "comments" VALUES(13,'Проверил, нужна замена',4,9);
INSERT INTO "comments" VALUES(14,'Очень странно',4,10);
INSERT INTO "comments" VALUES(15,'Ждем запчасти',3,10);
INSERT INTO "comments" VALUES(16,'Будем разбираться',2,11);
INSERT INTO "comments" VALUES(17,'Требуется доп. диагностика',6,13);
INSERT INTO "comments" VALUES(18,'Сделано',3,13);
INSERT INTO "comments" VALUES(19,'Сделано',2,15);
INSERT INTO "comments" VALUES(20,'Проверил, нужна замена',6,18);
INSERT INTO "comments" VALUES(21,'Сделано',2,18);
INSERT INTO "comments" VALUES(22,'Требуется доп. диагностика',6,20);
INSERT INTO "comments" VALUES(23,'Клиент уведомлен',3,20);
CREATE TABLE db_users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL
            );
INSERT INTO "db_users" VALUES('manager','866485796cfa8d7c0cf7111640205b83076433547577511d81f8030ae99ecea5','Менеджер');
INSERT INTO "db_users" VALUES('mechanic','ec23dea4ae16e63726aebb67afa6ea8d3f972533f43c76eae6c13dc228c8c316','Автомеханик');
INSERT INTO "db_users" VALUES('client','186474c1f2c2f735a54c2cf82ee8e87f2a5cd30940e280029363fecedfc5328c','Заказчик');
CREATE TABLE requests (
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
            );
INSERT INTO "requests" VALUES(1,'2026-01-03','Грузовая','GAZelle','Отказали тормоза','Готова к выдаче','2026-01-11','',NULL,10);
INSERT INTO "requests" VALUES(2,'2026-01-23','Легковая','Hyundai Solaris','Скрип при повороте','Готова к выдаче','2026-01-24','',2,8);
INSERT INTO "requests" VALUES(3,'2026-01-20','Легковая','Toyota Camry','Проблемы с электрикой','В процессе ремонта',NULL,'',NULL,7);
INSERT INTO "requests" VALUES(4,'2026-02-06','Грузовая','MAN','Отказали тормоза','Готова к выдаче','2026-02-13','',6,7);
INSERT INTO "requests" VALUES(5,'2026-01-03','Грузовая','MAN','Стук в подвеске','Готова к выдаче','2026-01-07','',6,10);
INSERT INTO "requests" VALUES(6,'2026-01-03','Грузовая','MAN','Проблемы с электрикой','Готова к выдаче','2026-01-07','',4,7);
INSERT INTO "requests" VALUES(7,'2026-01-02','Легковая','Hyundai Solaris','Проблемы с электрикой','Новая заявка',NULL,'',NULL,7);
INSERT INTO "requests" VALUES(8,'2026-01-06','Легковая','KIA Rio','Отказали тормоза','Готова к выдаче','2026-01-20','',6,8);
INSERT INTO "requests" VALUES(9,'2026-02-02','Легковая','Hyundai Solaris','Не заводится двигатель','В процессе ремонта',NULL,'',3,9);
INSERT INTO "requests" VALUES(10,'2026-02-17','Легковая','KIA Rio','Течь масла','В процессе ремонта',NULL,'',NULL,10);
INSERT INTO "requests" VALUES(11,'2026-02-14','Легковая','Toyota Camry','Скрип при повороте','Готова к выдаче','2026-02-18','',NULL,8);
INSERT INTO "requests" VALUES(12,'2026-02-01','Мотоцикл','Yamaha R6','Не заводится двигатель','В процессе ремонта',NULL,'',4,10);
INSERT INTO "requests" VALUES(13,'2026-01-16','Легковая','Lada Vesta','Стук в подвеске','Новая заявка',NULL,'',2,10);
INSERT INTO "requests" VALUES(14,'2026-01-29','Легковая','Lada Vesta','Течь масла','Готова к выдаче','2026-01-30','',4,7);
INSERT INTO "requests" VALUES(15,'2026-02-05','Грузовая','MAN','Скрип при повороте','В процессе ремонта',NULL,'',3,8);
INSERT INTO "requests" VALUES(16,'2026-01-15','Легковая','Lada Vesta','Течь масла','В процессе ремонта',NULL,'',4,9);
INSERT INTO "requests" VALUES(17,'2026-02-24','Грузовая','MAN','Стук в подвеске','Готова к выдаче','2026-02-28','',NULL,9);
INSERT INTO "requests" VALUES(18,'2026-02-01','Легковая','Lada Vesta','Скрип при повороте','Новая заявка',NULL,'',4,8);
INSERT INTO "requests" VALUES(19,'2026-02-04','Мотоцикл','Yamaha R6','Отказали тормоза','Готова к выдаче','2026-02-07','',2,7);
INSERT INTO "requests" VALUES(20,'2026-02-08','Мотоцикл','Yamaha R6','Отказали тормоза','В процессе ремонта',NULL,'',2,9);
CREATE TABLE users (
                userID INTEGER PRIMARY KEY,
                fio TEXT NOT NULL,
                phone TEXT,
                login TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                type TEXT NOT NULL CHECK(type IN ('Менеджер', 'Автомеханик', 'Заказчик'))
            );
INSERT INTO "users" VALUES(1,'Белов А.Д.','89210563128','login1','pass1','Менеджер');
INSERT INTO "users" VALUES(2,'Харитонова М.П.','89535078985','login2','pass2','Автомеханик');
INSERT INTO "users" VALUES(3,'Сидоров П.П.','89531234567','login3','pass3','Автомеханик');
INSERT INTO "users" VALUES(4,'Козлов В.В.','89123456789','login4','pass4','Автомеханик');
INSERT INTO "users" VALUES(5,'Морозова Е.А.','89234567890','login5','pass5','Менеджер');
INSERT INTO "users" VALUES(6,'Волков Н.Н.','89345678901','login6','pass6','Автомеханик');
INSERT INTO "users" VALUES(7,'Ильина Т.Д.','89219567841','login12','pass12','Заказчик');
INSERT INTO "users" VALUES(8,'Петров И.И.','89161234567','login8','pass8','Заказчик');
INSERT INTO "users" VALUES(9,'Соколова А.С.','89456789012','login9','pass9','Заказчик');
INSERT INTO "users" VALUES(10,'Михайлов Д.Д.','89567890123','login10','pass10','Заказчик');
CREATE INDEX idx_requests_status ON requests(requestStatus);
CREATE INDEX idx_requests_dates ON requests(startDate, completionDate);
CREATE INDEX idx_comments_request ON comments(requestID);
COMMIT;
