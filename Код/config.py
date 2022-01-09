import os

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  # Выбор устройства для TF
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Уведомления TF

host = "127.0.0.1"  # Адрес хоста
port = 3306  # Порт
user = "root"  # Имя пользователя
password = "####"  # Пароль
db_name = "mydb"  # Название базы данных
table_name = "reviews"  # Название таблицы в БД с комментариями
column_name = "review"  # Название столбца в таблице с комментариями
