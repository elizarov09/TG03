import sqlite3

# Создаем или подключаемся к базе данных
conn = sqlite3.connect('school_data.db')
cursor = conn.cursor()

# Создаем таблицу students
cursor.execute('''CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER,
    grade TEXT
)''')

# Сохраняем изменения и закрываем подключение
conn.commit()
conn.close()
