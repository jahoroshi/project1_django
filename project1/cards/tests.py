import psycopg2

# Параметры подключения к базе данных
conn = psycopg2.connect("dbname=project1 user=project1 password=123 host=localhost")
cur = conn.cursor()

# Параметр для запроса
slug = 'test-new'

# Выполнение подзапроса для проверки
subquery = """
SELECT cards_mappings.id AS mappings_id
FROM cards_cards
JOIN cards_mappings ON cards_cards.id = cards_mappings.card_id
JOIN cards_categories ON cards_mappings.category_id = cards_categories.id
WHERE cards_categories.slug = %(slug)s
AND cards_mappings.study_mode = 'new'
ORDER BY cards_mappings.mem_rating DESC
LIMIT 10;
"""

cur.execute(subquery, {'slug': slug})
subquery_results = cur.fetchall()
print("Subquery Results:", subquery_results)

# Основной запрос с ограничением до одного результата
query = """
WITH subquery AS (
    SELECT cards_mappings.id AS mappings_id
    FROM cards_cards
    JOIN cards_mappings ON cards_cards.id = cards_mappings.card_id
    JOIN cards_categories ON cards_mappings.category_id = cards_categories.id
    WHERE cards_categories.slug = %(slug)s
    AND cards_mappings.study_mode = 'new'
    ORDER BY cards_mappings.mem_rating DESC
    LIMIT 10
)
SELECT
    cards_cards.id,
    cards_mappings.repetition,
    CASE 
        WHEN cards_mappings.is_back_side = TRUE THEN cards_cards.side2
        ELSE cards_cards.side1
    END AS front_side,
    CASE 
        WHEN cards_mappings.is_back_side = TRUE THEN cards_cards.side1
        ELSE cards_cards.side2
    END AS back_side,
    cards_mappings.id AS mappings_id,
    cards_categories.name AS category_name
FROM cards_cards
JOIN cards_mappings ON cards_cards.id = cards_mappings.card_id
JOIN cards_categories ON cards_mappings.category_id = cards_categories.id
WHERE cards_mappings.id IN (SELECT mappings_id FROM subquery)
ORDER BY cards_mappings.easiness
LIMIT 1;
"""

cur.execute(query, {'slug': slug})

# Получение первого результата
first_result = cur.fetchone()

# Закрытие курсора и соединения
cur.close()
conn.close()

# Вывод первого результата
print("First Result:", first_result)
