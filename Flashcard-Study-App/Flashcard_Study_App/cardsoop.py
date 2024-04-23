import random
from random import randint
from random import choice

import psycopg2
from psycopg2 import pool


class CardBox:
    def __init__(self):
        dbconfig = {
            'dbname': 'project1',
            'user': 'project1',
            'password': '123',
            'host': 'localhost',
        }
        self.cnxpool = psycopg2.pool.SimpleConnectionPool(1, 2, **dbconfig)
        self.boxes_set = [self.create_box(0), self.create_box(1), self.create_box(2), self.create_box(3)]

    @staticmethod
    def connect_db(func):
        def wrapper(self, *args, **kwargs):
            try:
                conn = self.cnxpool.getconn()
                cursor = conn.cursor()
                result = func(self, cursor, *args, **kwargs)
                return result
            except Exception as e:
                print(f'Error in connect_db {e}')
            finally:
                cursor.close()
                self.cnxpool.putconn(conn)

        return wrapper

    @connect_db
    def update_data(self, cursor, repetition_interval):
        query = "UPDATE flashcard SET status = %s, create_datetime = %s WHERE id = %s"
        data = (repetition_interval, "NOW()", self.current_card['id'])
        cursor.execute(query, data)
        cursor.connection.commit()

    @connect_db
    def get_data(self, cursor, box_number, *args, **kwargs):
        query = (f'SELECT id, word1, word2 FROM flashcard WHERE status = {box_number} '
                 f'ORDER BY create_datetime ASC')
        cursor.execute(query, *args, **kwargs)
        return cursor.fetchall()

    def create_box(self, box_number):
        box = []
        data = self.get_data(box_number)
        for el in data:
            box.append({
                'id': el[0],
                'side1': el[1],
                'side2': el[2],
                'interval': randint(1, 2),
            })
        return box

    def generate_cur_card(self):
        if not any(self.boxes_set):
            raise Exception('There are no cards')
        lengths = tuple(map(len, self.boxes_set))
        total_lengths = sum(lengths)
        base_weights = [4, 3, 1, 0.1]
        # weight = [4, 3, 1, 0.1]
        relativ_weights = [i / total_lengths for i in lengths]
        weight = [x * y for x, y in zip(relativ_weights, base_weights)]
        if hasattr(self, 'box_number'):
            weight[self.box_number] /= 1.5
            print(weight)

        box_number, card_number = self.generate_card_position(lengths, weight)

        self.box_number, self.card_number = box_number, card_number
        self.current_card = self.boxes_set[box_number][card_number]

    def generate_card_position(self, lengths, weight):
        box_number = random.choices(range(len(lengths)), weights=weight, k=1)[0]
        card_number = randint(0, max(0, min(lengths[box_number] - 1, (lengths[box_number] - 1) // 2)))
        return box_number, card_number

    def gen_display_sides(self):
        interval = self.current_card['interval']
        if 1 <= interval <= 4:
            self.current_card['interval'] += 2

        if interval in (1, 4):
            self.current_side = 1
            return 1
        elif interval in (2, 3):
            self.current_side = 2
            return 2


    def change_box(self, box_num):
        if (box_num == self.box_number or box_num < self.box_number) and box_num != 3:
            self.current_card['interval'] -= 2
        elif box_num > self.box_number:
            if self.current_card['interval'] in (5, 6):
                self.current_card['interval'] -= 4
            else:
                box_num = self.box_number

        self.update_data(box_num)

        if self.boxes_set[self.box_number]:
            if self.current_card['interval'] < 5:
                card = self.boxes_set[self.box_number].pop(self.card_number)
                self.boxes_set[box_num].append(card)
            else:
                del self.boxes_set[self.box_number][self.card_number]

    def fill_incomplete_lists(self):
        for indx, box in enumerate(self.boxes_set[:-1]):
            if not box:
                self.boxes_set[indx] = self.create_box(indx)
                if not any(self.boxes_set[:-1]):
                    raise Exception('No cards')

    def get_card(self):
        self.generate_cur_card()
        side_num = self.gen_display_sides()
        side1 = self.current_card['side1']
        side2 = self.current_card['side2']
        return (side2, side1) if side_num == 1 else (side1, side2)

    def boxes_processing(self, interval):
        self.change_box(interval)
        self.fill_incomplete_lists()

    @staticmethod
    def display_substring(card_side, substr):
        side = card_side.split()
        return ' '.join(i[:min(substr, len(i))] + '.' * (len(i) - substr) for i in side)

    def provide_options(self):
        cur_side = self.current_side
        cb = self.boxes_set[self.box_number]
        max_box = max((box for box in self.boxes_set if box != cb), key=len)

        extra_words = (choice(max_box)['side1'] if cur_side == 1 else choice(max_box)['side2'] for _ in range(12))
        extra_words = tuple(set(extra_words))[:4]
        return extra_words





cardbox = CardBox()
user_answer = 0
while True:

    for i, j in enumerate(cardbox.boxes_set):
        print(f' ->> Box {i}: {len(j)} << ', end='')
    print('\n')

    card = cardbox.get_card()
    print(card[0])
    print('1.  box num ', cardbox.box_number, ' card num ', cardbox.card_number)

    # user_answer = int(input('2 - show answer, 3 - exit: '))
    user_answer = 3
    if user_answer == 2:
        sub_str = ''
        while card[1] != sub_str:
            display_substr = int(input('Сколько букв открыть?'))
            sub_str = cardbox.display_substring(card[1], display_substr)
            print(sub_str)
    elif user_answer == 3:
        extra_words = cardbox.provide_options()
        print(extra_words)

    print(card[1])
    print('2.  box num ', cardbox.box_number, ' card num ', cardbox.card_number)
    repetition_interval = int(input('repetition interval 0, 1, 2 or 3: '))
    cardbox.boxes_processing(repetition_interval - 1)

    # print()
    for i in cardbox.boxes_set:
        print()
        print('LENGHT OF BOX -', len(i), end='  /  ')
        for j in i:
            print(j['interval'], j['side1'][:3], end=' - - - |->')
    print('\n', '___________________________', '\n')
