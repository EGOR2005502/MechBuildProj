import sqlite3
import os

# Путь к файлу базы данных
db_file = 'project.db'

if os.path.exists(db_file):
    os.remove(db_file)

# Подключение к базе данных
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Создание таблиц, если они не существуют
cursor.execute('''CREATE TABLE IF NOT EXISTS sklad (
    IDitem INTEGER PRIMARY KEY,
    item TEXT NOT NULL UNIQUE,
    volume real NOT NULL
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS kraft (
    IDcraft INTEGER PRIMARY KEY,
    product text not null UNIQUE,
    components text not null,
    speed_minut REAL NOT NULL
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS objective (
    IDorder INTEGER PRIMARY KEY,
    product text not null UNIQUE,
    Volume REAL NOT NULL
)''')

# Функция для проверки и добавления данных
def insert_or_ignore_data(table, columns, data):
    placeholders = ', '.join(['?'] * len(columns))
    columns_str = ', '.join(columns)
    query = f"INSERT OR IGNORE INTO {table} ({columns_str}) VALUES ({placeholders})"
    cursor.executemany(query, data)

# Данные для таблицы sklad
sklad_data = [
    ('пылесос',0),
    ('корпус пылесоса',2),
    ('двигатель', 2),
    ('труба', 2),
    ('шланг', 2),
    ('аккумулятор', 2),
    ('кабель питания', 4),
    ('фильтр', 2),
    ('болт', 19),
    ('вентилятор', 0),
    ('корпус вентилятора', 0),
    ('лопасть', 0),
    ('электрочайник', 0),
    ('корпус чайника', 2),
    ('нагревательный элемент', 2),
    ('пластик', 0),
    ('резиновая прокладка', 0),
    ('статор', 0),
    ('ротор', 0),
    ('подшипник', 0),
    ('гофр - пружина', 0),
    ('литий-ионный элемент', 0),
    ('медная жила с изоляцией', 0),
    ('вилка', 0),
    ('пенополиуретан', 0),
    ('бумага', 0),
    ('сталь', 1),
    ('резиновая ножка', 0),
    ('нержавеющая сталь', 0),
    ('нихромовая спираль', 0),
    ('термоизоляция', 0),
]
insert_or_ignore_data('sklad', ['item', 'volume'], sklad_data)

# Данные для таблицы kraft
kraft_data = [
    ('пылесос', '1 - корпус пылесоса, 1 -  двигатель, 1 - труба, 1 - шланг, 1 - аккумулятор, 1 - кабель питания, 1 - фильтр, 20 - болт', 0.5),
    ('корпус пылесоса', '1 - пластик, 1 - резиновая прокладка', 1),
    ('двигатель', '1 - статор, 1 - ротор,1 - подшипник', 1),
    ('труба', '1 - пластик', 40),
    ('шланг', '1 - пластик, 1 - гофр - пружина', 38),
    ('аккумулятор', '1 - литий-ионный элемент, 1 - пластик', 1),
    ('кабель питания', '1 - медная жила с изоляцией, 1 - вилка', 1),
    ('фильтр', '1 - пенополиуретан, 1 - бумага, 1 - пластик', 1),
    ('болт', '1 - сталь', 4),
    ('вентилятор', '1 - корпус вентилятора, 1 - двигатель, 5 - лопасть, 10 - болт', 0.5),
    ('корпус вентилятора', '1 - пластик, 4 - резиновая ножка', 1),
    ('лопасть', '1 - пластик', 20),
    ('электрочайник', '1 - корпус чайника, 1 - нагревательный элемент,  1 - кабель питания, 8 - болт', 0.5),
    ('корпус чайника', '1 - пластик, 1 - нержавеющая сталь', 0.6),
    ('нагревательный элемент', '1 - нихромовая спираль, 1 - термоизоляция', 1),
]
insert_or_ignore_data('kraft', ['product', 'components', 'speed_minut'], kraft_data)

# Данные для таблицы objective
objective_data = [
    ('пылесос', 1),
    ('вентилятор', 0),
    ('электрочайник', 1)
]
insert_or_ignore_data('objective', ['product', 'Volume'], objective_data)

# Сохранение изменений
conn.commit()

# Вывод содержимого таблиц
def print_table(table_name):
    cursor.execute(f"SELECT * FROM {table_name}")
    result = cursor.fetchall()
    print(f"\n{table_name}:")
    for row in result:
        print(row)

print_table('objective')
print_table('sklad')
print_table('kraft')

# Закрытие соединения
conn.close()