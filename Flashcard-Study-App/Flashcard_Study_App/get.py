import random
from random import randint

import psycopg2
from psycopg2 import pool


# def connect_db(func):
#     def wrapper(*args, **kwargs):
#         try:
#             conn = psycopg2.connect(
#                 dbname='project1',
#                 user='project1',
#                 password='123',
#                 host='localhost',
#             )
#         except Exception as e:
#             print(f'error1 {e}')
#
#         cursor = conn.cursor()
#
#         result = func(cursor, *args, **kwargs)
#
#         cursor.close()
#         conn.close()
#         return result
#
#     return wrapper
def connect_db(func):
    def wrapper(*args, **kwargs):
        try:
            dbconfig = {
                'dbname': 'project1',
                'user': 'project1',
                'password': '123',
                'host': 'localhost',
            }

        except Exception as e:
            print(f'Error in connect_db {e}')

        cnxpool = psycopg2.pool.SimpleConnectionPool(1, 2, **dbconfig)
        conn = cnxpool.getconn()
        cursor = conn.cursor()

        result = func(cursor, *args, **kwargs)

        cursor.close()
        conn.close()
        return result

    return wrapper


@connect_db
def update_db(cursor, query, data):
    cursor.execute(query, data)
    cursor.connection.commit()


@connect_db
def get_data(cursor, *args, **kwargs):
    cursor.execute(*args, **kwargs)
    return cursor.fetchall()


def show_side(card_number, box_number, card_boxes, shown_sides):
    if shown_sides[box_number][card_number] in (1, 4):
        current_side = card_boxes[box_number][card_number][1]
    elif shown_sides[box_number][card_number] in (2, 3):
        current_side = card_boxes[box_number][card_number][2]
    return current_side


def reverse_side(card_number, box_number, card_boxes, shown_sides):
    if shown_sides[box_number][card_number] in (1, 4):
        shown_sides[box_number][card_number] += 2
        current_side = card_boxes[box_number][card_number][2]
    elif shown_sides[box_number][card_number] in (2, 3):
        shown_sides[box_number][card_number] += 2
        current_side = card_boxes[box_number][card_number][1]

    # if shown_sides[box_number][card_number] == 1:
    #     shown_sides[box_number][card_number] += 2
    #     current_side = card_boxes[box_number][card_number][2]
    # elif shown_sides[box_number][card_number] == 2:
    #     shown_sides[box_number][card_number] += 2
    #     current_side = card_boxes[box_number][card_number][1]
    #
    # elif shown_sides[box_number][card_number] == 3:
    #     del shown_sides[box_number][card_number]
    #     current_side = card_boxes[box_number].pop(card_number)[1]
    # elif shown_sides[box_number][card_number] == 4:
    #     del shown_sides[box_number][card_number]
    #     current_side = card_boxes[box_number].pop(card_number)[2]
    return current_side


def set_repetition_interval(repetition_interval):
    sql = "UPDATE flashcard SET status = %s, create_datetime = %s WHERE id = %s"
    update_db(sql, (repetition_interval, "now()", card_boxes[box_number][card_number][0]))


def cards_in_box():
    boxes = ['box1', 'box2', 'box3', 'box4']
    query = 'SELECT COUNT(id) FROM flashcard WHERE status = '
    quantity = dict(zip(boxes, [get_data(f'{query}{int(status[-1])}') for status in boxes]))
    # quantity = {box: count for box, count in zip(boxes, get_data(f'{query}{int(status[-1])}'))}
    return quantity


class Card:
    def __init__(self, *args):
        self.card_id = args[0]
        self.side1 = args[1]
        self.side2 = args[2]
        self.date = args[3]
        self.status = args[4]

    def priority(self, status):
        ...


def create_boxes():
    cur_box = []
    sides = []
    for i in range(1, 5):
        cur_box.append(
            get_data('SELECT id, word1, word2 FROM flashcard WHERE status = ' + str(i) + ' ORDER BY create_datetime DESC LIMIT 10'))
        sides.append([randint(1, 2) for _ in range(len(cur_box[i - 1]))])
    return cur_box, sides


def get_box_index(card_boxes):
    total_weight = sum(len(i) for i in card_boxes)
    weights = [len(i) / total_weight for i in card_boxes]
    weights[0] *= 3
    box_index = random.choices(range(len(card_boxes)), weights=weights, k=1)
    return box_index[0]


def fill_incomplete_lists(card_boxes, shown_sides):
    query = 'SELECT id, word1, word2 FROM flashcard WHERE status = %s ORDER BY create_datetime ASC'
    for i, box in enumerate(shown_sides[:]):
        if not box:
            card_boxes[i] = get_data(query, str(i + 1))
            shown_sides[i] = [random.randint(1, 2) for _ in range(len(card_boxes[i]))]
    card_boxes = [box for box in card_boxes if box]
    shown_sides = [side for side in shown_sides if side]
    if not card_boxes:
        print('The list is out of words')
        return
    return card_boxes, shown_sides


def clean_unused_cards(card_boxes, shown_sides):
    for i, box in enumerate(shown_sides[:]):
        for indx, el in enumerate(box):
            if el > 4:
                del shown_sides[i][indx]
                del card_boxes[i][indx]
    return card_boxes, shown_sides


card_boxes, shown_sides = create_boxes()
box_number = 0
card_number = 0
user_answer = 0
counter = {}
# print(*[f'{key}: {value[0][0]}  ' for key, value in cards_in_box().items()])
# box = int(input('Choose a box: '))
# card_boxes = get_data('SELECT * FROM flashcard WHERE status = ' + str(1))
# card_boxes= [get_data('SELECT * FROM flashcard WHERE status = ' + str(i) + ' ORDER BY create_datetime DESC') for i in range(1, 5)]
# shown_sides = [randint(1, 2) for _ in range(len(card_boxes))]


while user_answer != 3:
    if card_boxes is None:
        break

    clean_unused_cards(card_boxes, shown_sides)
    card_boxes, shown_sides = fill_incomplete_lists(card_boxes, shown_sides)

    box_number = get_box_index(card_boxes)
    card_number = randint(0, len(shown_sides[box_number]) - 1)

    # print(show_side(card_number, box_number, card_boxes, shown_sides))
    sside = show_side(card_number, box_number, card_boxes, shown_sides)
    counter[sside] = counter.get(sside, 0) + 1
    print(sside)

    user_answer = int(input('2 - show answer, 3 - exit: '))

    if user_answer == 2:
        rside = reverse_side(card_number, box_number, card_boxes, shown_sides)
        print(rside)


        repetition_interval = int(input('repetition interval 1, 2 or 3: '))
        set_repetition_interval(repetition_interval)

        if repetition_interval == 1:
            if shown_sides[box_number][card_number] > 2:
                shown_sides[box_number][card_number] -= 2
        # # else:
        #     del card_boxes[box_number][card_number]
        #     del shown_sides[box_number][card_number]

    print('\n', counter, '\n')
    for i, box in enumerate(card_boxes):
        print(i, ' ', len(box), end='\n')
