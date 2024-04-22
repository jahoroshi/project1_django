import psycopg2

word1 = [
    "Яблоко",
    "Книга",
    "Солнце",
    "Машина",
    "Дом",
    "Вода",
    "Кошка",
    "Стол",
    "Чашка",
    "Путешествие",
    "Море",
    "Гора",
    "Цветок",
    "Птица",
    "Медведь",
    "Луна",
    "Звезда",
    "Ключ",
    "Ручка",
    "Велосипед"
]
word2 = [
    "Apple",
    "Book",
    "Sun",
    "Car",
    "House",
    "Water",
    "Cat",
    "Table",
    "Cup",
    "Journey",
    "Sea",
    "Mountain",
    "Flower",
    "Bird",
    "Bear",
    "Moon",
    "Star",
    "Key",
    "Pen",
    "Bicycle"
]

try:
    conn = psycopg2.connect(
        dbname='project1',
        user='project1',
        password='123',
        host='localhost',
    )
except Exception as e:
    print(f'erro1 {e}')

cursor = conn.cursor()

try:
    for i in range(len(word1)):
        sql = "INSERT INTO flashcard (word1, word2, create_datetime, status) VALUES (%s, %s, %s, %s)"
        data = (word1[i], word2[i], 'now()', '1')
        cursor.execute(sql, data)
    conn.commit()
except Exception as e:
    print(f'erro {e}')

finally:
    if conn:
        cursor.close()
        conn.close()
        print('connection closed')
