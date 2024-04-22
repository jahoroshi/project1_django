from tkinter import *  # Импортируем все из модуля tkinter для создания графического интерфейса пользователя
import random  # Импортируем модуль random для использования функции случайного перемешивания
import csv  # Импортируем модуль csv для работы с файлами CSV

# Определение класса flashcard для создания карточек с вопросом и ответом
class flashcard:
    def __init__(self, question, answer):
        self.question = question  # Текст вопроса на лицевой стороне карточки
        self.answer = answer  # Текст ответа на обратной стороне карточки
        self.side_up = "Q"  # Переменная, указывающая, какая сторона карточки видна: "Q" - вопрос, "A" - ответ

# Функция для переворачивания карточки
def flip(flashcard_list, the_canvas, index_of_card):
    the_canvas.delete("all")  # Очищаем холст
    current_on_screen = flashcard_list[index_of_card]  # Получаем текущую карточку по индексу
    the_canvas.create_rectangle(0, 0, 500, 500, fill="white", outline="")  # Создаем белый прямоугольник (фон карточки)
    # Проверяем, какая сторона карточки сейчас видна, и переворачиваем ее
    if(current_on_screen.side_up == "Q"):
        the_canvas.create_text(270, 170, width=530, font="Times 20 italic bold", text=current_on_screen.answer)
        current_on_screen.side_up = "A"
    else:
        the_canvas.create_text(270, 170, width=530, font="Times 20 italic bold", text=current_on_screen.question)
        current_on_screen.side_up = "Q"
    global card_index  # Объявляем переменную card_index глобальной, чтобы иметь к ней доступ вне функции
    card_index = index_of_card  # Обновляем индекс текущей карточки

# Функция для перехода к следующей карточке
def next_card(flashcard_list, the_canvas, index_of_card):
    the_canvas.delete("all")  # Очищаем холст
    global card_index  # Объявляем переменную card_index глобальной
    # Проверяем, не достигли ли мы конца списка карточек, и переходим к следующей карточке или к первой в списке
    if(index_of_card + 1 >= len(flashcard_list)):
        next_card_on_screen = flashcard_list[0]
        card_index = 0
    else:
        next_card_on_screen = flashcard_list[index_of_card + 1]
        card_index = index_of_card + 1
    # Отображаем вопрос следующей карточки
    the_canvas.create_text(270, 170, width=530, font="Times 20 italic bold", text=next_card_on_screen.question)
    next_card_on_screen.side_up = "Q"

# Функция для перехода к предыдущей карточке
def prev_card(flashcard_list, the_canvas, index_of_card):
    the_canvas.delete("all")  # Очищаем холст
    global card_index  # Объявляем переменную card_index глобальной
    # Проверяем, не находимся ли мы в начале списка, и переходим к предыдущей карточке или к последней в списке
    if(index_of_card - 1 <= -1):
        next_card_on_screen = flashcard_list[len(flashcard_list) - 1]
        card_index = len(flashcard_list) - 1
    else:
        next_card_on_screen = flashcard_list[index_of_card - 1]
        card_index = index_of_card - 1
    # Отображаем вопрос предыдущей карточки
    the_canvas.create_text(270, 170, width=530, font="Times 20 italic bold", text=next_card_on_screen.question)
    next_card_on_screen.side_up = "Q"

# Функция для подготовки интерфейса к отображению карточек
def finalize(flashcard_list):
    random.shuffle(flashcard_list)  # Перемешиваем список карточек случайным образом
    the_canvas = Canvas(window, width=550, height=370, highlightthickness=0)  # Создаем холст для отображения карточек
    # Отображаем вопрос первой карточки в списке
    the_canvas.create_text(270, 170, width=530, font="Times 20 italic bold", text=flashcard_list[0].question)
    global card_index  # Объявляем переменную card_index глобальной
    card_index = 0  # Устанавливаем индекс текущей карточки на 0
    the_canvas.configure(bg="white")  # Устанавливаем белый фон холста
    the_canvas.place(x=225, y=60)  # Размещаем холст в окне
    # Создаем кнопки для управления карточками
    flip_button = Button(text="Flip Card", font=("fixedsys", 30), command=lambda: flip(flashcard_list, the_canvas, card_index), bg="#2a19e3", fg="white")
    flip_button.pack(side=BOTTOM, pady=40)
    next_button = Button(text="Next", font=("fixedsys", 30), command=lambda: next_card(flashcard_list, the_canvas, card_index), bg="#2a19e3", fg="white")
    next_button.place(x=640, y=491)
    prev_button = Button(text="Prev", font=("fixedsys", 30), command=lambda: prev_card(flashcard_list, the_canvas, card_index), bg="#2a19e3", fg="white")
    prev_button.place(x=250, y=491)


# Функция для чтения файла CSV с флеш-картами, создания списка объектов flashcard и их отображения
def get_flashcards(entry, label, button):
    try:
        the_file = open(entry.get(), "r")  # Пытаемся открыть файл
        entry.delete(0, END)  # Очищаем поле ввода
        the_file.seek(0)  # Перемещаем указатель в начало файла
        the_reader = csv.reader(the_file)  # Создаем объект для чтения файла CSV
        header1 = next(the_reader, None)  # Пропускаем заголовок, если он есть
        flashcard_list = list()  # Создаем пустой список для флеш-карт
        for line in the_reader:  # Читаем каждую строку в файле CSV
            flashcard_list.append(flashcard(line[0], line[1]))  # Добавляем флеш-карту в список
        label.destroy()  # Удаляем метку
        entry.destroy()  # Удаляем поле ввода
        button.destroy()  # Удаляем кнопку
        finalize(flashcard_list)  # Вызываем функцию finalize для отображения флеш-карт
    except:
        label.configure(text="File does not exist. Try again")  # В случае ошибки выводим сообщение
        entry.delete(0, END)  # Очищаем поле ввода

# Функция для настройки GUI для ввода файла CSV с флеш-картами
def start_game():
    start_button.destroy()  # Удаляем кнопку "Начать"
    start_label.destroy()  # Удаляем метку "Начать"
    flashcard_entry = Entry(window, width=80, borderwidth=15)  # Создаем поле ввода для пути к файлу
    flashcard_entry.place(x=245, y=360)  # Размещаем поле ввода
    # Создаем метку с инструкцией для пользователя
    entry_label = Label(text="Please enter the path of the csv file that contains the flashcard pack you wish to use", font=("fixedsys", 30), wraplength=590, bg="#6e17bf", fg="White", justify="center")
    entry_label.pack(pady=60)  # Размещаем метку
    # Создаем кнопку для использования набора флеш-карт
    entry_button = Button(text="use flashcard set", font=("fixedsys", 30), command=lambda: get_flashcards(flashcard_entry, entry_label, entry_button), bg="#2a19e3", fg="white", padx=73)
    entry_button.place(x=245, y=450)  # Размещаем кнопку

# Настройка основного окна GUI
window = Tk()
window.configure(bg="#6e17bf")  # Устанавливаем фоновый цвет
window.resizable(False, False)  # Запрещаем изменение размера окна
window.geometry("1001x601")  # Устанавливаем размер окна
window.title("Flashcard-App")  # Устанавливаем заголовок окна
# Создаем холст для рисования и размещаем его
the_canvas = Canvas(window, width=1000, height=600, highlightthickness=0)
the_canvas.place(x=0, y=0)
# Рисуем разноцветные прямоугольники для декоративного оформления
the_canvas.create_rectangle(0, 0, 1000, 600, fill="#1A17BF", outline="")
# ... (продолжение рисования прямоугольников)
# Создаем метку и кнопку для начала работы с флеш-картами
start_label = Label(text="FLASHCARDS", font=("fixedsys", 155), bg="#6e17bf", fg="white", pady=90)
start_label.place(x=245, y=100)
start_button = Button(text="START STUDYING", font=("fixedsys", 30), command=start_game, bg="#2a19e3", fg="white", anchor=CENTER, padx=99)
start_button.place(x=246, y=450)
window.mainloop()  # Запускаем главный цикл обработки событий Tkinter
