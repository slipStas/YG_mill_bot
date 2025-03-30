import sqlite3

import telebot

from telebot import types
from employee import Employee
from employee_group import EmployeeGroup

db_name = 'cutting_tools/available_tools.db'
new_employeer = Employee(name='', second_name='', phone_number='', telegram_id=0)
token = open('token.txt', 'r').read()

bot = telebot.TeleBot(token)

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "Привет":
        bot.send_message(message.from_user.id, "Привет, чем я могу тебе помочь?")
    elif message.text == "/help":
        bot.send_message(message.from_user.id, 'Для регистрации нажми /registration\nХочешь взять инструмент - /get_instrument')
    elif message.text == '/registration':
        bot.send_message(message.from_user.id, "Введи имя...")
        bot.register_next_step_handler(message, get_name)  # следующий шаг – функция get_name
    elif message.text == "/start":
        con = sqlite3.connect(db_name)
        cursor = con.cursor()
        if cursor.execute(
                "SELECT * FROM employee WHERE telegram_id=" + str(message.from_user.id)).fetchone() is not None:
            print('registration ok')
            match cursor.execute(
                "SELECT * FROM employee WHERE telegram_id=" + str(message.from_user.id)).fetchone()[5]:
                case EmployeeGroup.employee.value:
                    # user_group = EmployeeGroup.employee
                    keyboard = types.InlineKeyboardMarkup()
                    key_mill = types.InlineKeyboardButton(text='взять фрезу', callback_data='get_mill')  # кнопка «Да»
                    keyboard.add(key_mill)  # добавляем кнопку в клавиатуру
                    key_drill = types.InlineKeyboardButton(text='взять сверло', callback_data='get_drill')
                    keyboard.add(key_drill)

                    bot.send_message(message.from_user.id, text="Какой инструмент хочешь взять?", reply_markup=keyboard)
                case EmployeeGroup.master.value:
                    # user_group = EmployeeGroup.master
                    keyboard = types.InlineKeyboardMarkup()
                    key_get_mill = types.InlineKeyboardButton(text='взять фрезу', callback_data='get_mill')  # кнопка «Да»
                    keyboard.add(key_get_mill)  # добавляем кнопку в клавиатуру
                    key_get_drill = types.InlineKeyboardButton(text='взять сверло', callback_data='get_drill')
                    keyboard.add(key_get_drill)

                    key_put_mill = types.InlineKeyboardButton(text='положить фрезу',
                                                              callback_data='put_mill')  # кнопка «Да»
                    keyboard.add(key_put_mill)  # добавляем кнопку в клавиатуру
                    key_put_drill = types.InlineKeyboardButton(text='положить сверло', callback_data='put_drill')
                    keyboard.add(key_put_drill)

                    bot.send_message(message.from_user.id, text="Выберите нужный пункт", reply_markup=keyboard)

            print(message.from_user.id)
            print(cursor.execute(
                "SELECT * FROM employee WHERE telegram_id=" + str(message.from_user.id)).fetchone()[5])
            cursor.close()
            con.close()
        else:
            print('need registration')
            bot.send_message(message.from_user.id, "Тебя нет в базе данных, необходима регистрация\n"
                                                   "для регистрации нажми /registration")
    else:
        bot.send_message(message.from_user.id, "Здравствуйте, нажмите /start для начала работы")


# @bot.message_handler(commands=['list_all_tool'])
# def send_list_all_tool(message):
#     try:
#         # Подключаемся к базе данных
#         conn = sqlite3.connect(db_name)
#         cursor = conn.cursor()
#
#         # Выполняем SQL-запрос
#         cursor.execute("SELECT * FROM milling_cutters_steel")
#         data = cursor.fetchall()
#
#         # Закрываем соединение
#         cursor.close()
#         conn.close()
#
#         if not data:
#             bot.send_message(message.chat.id, "Список пуст")
#             return
#
#         # Создаем inline-клавиатуру
#         markup = types.InlineKeyboardMarkup()
#         for item in data:
#             markup.add(
#                 types.InlineKeyboardButton(
#                     text=item[0],  # Отображаемое имя
#                     callback_data=f"selectAllTools_{item[0]}"
#                 )
#             )
#
#         bot.edit_message_text(
#             chat_id=message.chat.id,
#             message_id=message.message_id,
#             text="Выберите элемент:",
#             reply_markup=markup
#         )
#
#     except sqlite3.Error as e:
#         bot.send_message(message.chat.id, f"Ошибка базы данных: {e}")
#     except Exception as e:
#         bot.send_message(message.chat.id, f"Произошла ошибка: {e}")

@bot.message_handler(commands=['list_diameters'])
def send_list_diameters(message):
    try:
        # Подключаемся к базе данных
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Выполняем SQL-запрос
        cursor.execute("SELECT DISTINCT diameter FROM milling_cutters_steel WHERE count>0")
        data = cursor.fetchall()
        diameters = [float(row[0]) for row in data]
        # Закрываем соединение
        cursor.close()
        conn.close()

        if not data:
            bot.send_message(message.chat.id, "Список пуст")
            return
        # Создаем inline-клавиатуру
        markup = types.InlineKeyboardMarkup()
        for item in diameters:
            markup.add(
                types.InlineKeyboardButton(
                    text=str(item),  # Отображаемое имя
                    callback_data=f"listUniqueDiameters_{item}"
                )
            )

        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text="Доступны такие диаметры:",
            reply_markup=markup
        )

    except sqlite3.Error as e:
        bot.send_message(message.chat.id, f"Ошибка базы данных: {e}")
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {e}")


# Обработчик нажатий на кнопки
@bot.callback_query_handler(func=lambda call: call.data.startswith('selectAllTools_'))
def handle_element_selection(call):
    try:
        element_name = call.data.split('_')[1]  # Извлекаем ID из callback_data

        with sqlite3.connect(db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM milling_cutters_steel WHERE name=? AND count>0",
                (element_name,)
            )
            element = cursor.fetchone()
        cursor.close()
        conn.close()
        if element:
            # Форматируем информацию о элементе
            response = (
                f"название: {element[0]}\n"
                f"диаметр: {element[1]}\n"
                f"радиус: {element[2]}\n"
                f"длина: {element[3]}\n"
                f"количество: {element[4]}"
            )
        else:
            response = "Элемент не найден"

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=response
        )
    except Exception as e:
        bot.send_message(call.message.chat.id, f"Ошибка: {str(e)}")


@bot.callback_query_handler(func=lambda call: call.data.startswith('listUniqueDiameters_'))
def handle_diameter_selection(call):
    try:
        diameter_name = call.data.split('_')[1]  # Извлекаем ID из callback_data
        print(diameter_name)
        with sqlite3.connect(db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM milling_cutters_steel WHERE diameter=? AND count>0",
                (float(diameter_name),)
            )
            data = cursor.fetchall()
            print(data)
        cursor.close()
        conn.close()

        markup = types.InlineKeyboardMarkup()
        for item in data:
            markup.add(
                types.InlineKeyboardButton(
                    text=str(item[0]),  # Отображаемое имя
                    callback_data=f"listDiameterMills_{item[0]}"
                )
            )

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Выберите фрезу:",
            reply_markup=markup
        )


    except Exception as e:
        bot.send_message(call.message.chat.id, f"Ошибка: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('listDiameterMills_'))
def handle_mill_selection(call):
    try:
        element_name = call.data.split('_')[1]  # Извлекаем ID из callback_data
        with sqlite3.connect(db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM milling_cutters_steel WHERE name=?",
                (element_name,)
            )
            element = cursor.fetchone()
        cursor.close()
        conn.close()

        if element:
            # Форматируем информацию о элементе
            response = (
                f"название: {element[0]}\n"
                f"диаметр: {element[1]}\n"
                f"радиус: {element[2]}\n"
                f"длина: {element[3]}\n\n"
                f"остаток: {element[4]}"
            )
        else:
            response = "Элемент не найден"

        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton(
                text=str("Да, беру!"),  # Отображаемое имя
                callback_data=f"takeMill_{element_name}"
            ),
            types.InlineKeyboardButton(
                text=str("Нет, оставлю!"),  # Отображаемое имя
                callback_data=f"get_mill"
            )
        )

        # Редактируем исходное сообщение с кнопками
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=response,
            reply_markup=markup
        )

    except Exception as e:
        bot.send_message(call.message.chat.id, f"Ошибка: {str(e)}")


@bot.callback_query_handler(func=lambda call: call.data.startswith('takeMill_'))
def handle_take_mill(call):
    try:
        mill_name = call.data.split('_')[1]  # Извлекаем ID из callback_data

        with sqlite3.connect(db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM milling_cutters_steel WHERE name=?",
                (mill_name,)
            )
            element = cursor.fetchone()
            new_count = element[4] - 1
        cursor.close()
        conn.close()

        if element:
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE milling_cutters_steel SET count = ? WHERE name = ?",
                (new_count, element[0])
            )
            conn.commit()
            cursor.close()
            conn.close()
            response = (f"Вы взяли фрезу _*__{element[0]}__*_\n"
                        f"было ~* {new_count + 1} *~  "
                        f"осталось *{new_count}*\n"
                        f"В начало /start")
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=response,
                parse_mode='MarkdownV2'
            )
        else:
            response = "Элемент не найден"
            # Редактируем исходное сообщение с кнопками
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=response
            )
    except Exception as e:
        bot.send_message(call.message.chat.id, f"Ошибка: {str(e)}")


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "yes": #call.data это callback_data, которую мы указали при объявлении кнопки
        print('unswer Yes')#код сохранения данных, или их обработки
        bot.send_message(call.message.chat.id, 'Запомню : )')
        con = sqlite3.connect(db_name)
        cursor = con.cursor()
        print(new_employeer.get_info())
        cursor.execute("INSERT INTO employee (name, second_name, phone_number, telegram_id, employee_group) VALUES (?, ?, ?, ?, ?)",
                       new_employeer.get_info())

        con.commit()
        cursor.close()
        con.close()
        print('data has been added into the db')
        bot.send_message(call.message.chat.id, 'чтобы взять инструмент нажмите /start')
    elif call.data == "no":
        print('unswer NO')
    elif call.data == "get_mill":
        print('unswer get_mill')
        # con = sqlite3.connect(db_name)
        # cursor = con.cursor()
        send_list_diameters(call.message)

        # cursor.close()
        # con.close()
    elif call.data == "get_drill":
        print('unswer get_drill')
    elif call.data == "put_mill":
        print('unswer put_mill')
    elif call.data == "put_drill":
        print('unswer put_drill')
    # elif call.data == "list_diameters":
    #     print("put Нет, оставлю")
    #     send_list_diameters(call.message)




def get_name(message): #получаем фамилию
    new_employeer.telegram_id = message.from_user.id
    new_employeer.name = message.text
    bot.send_message(message.from_user.id, 'Введи фамилию...')
    bot.register_next_step_handler(message, get_surname)

def get_surname(message):
    new_employeer.second_name = message.text
    bot.send_message(message.from_user.id,'Введи номер телефона')
    bot.register_next_step_handler(message, get_phone_number)

def get_phone_number(message):
    new_employeer.phone_number = message.text
    keyboard1 = types.InlineKeyboardMarkup()  # наша клавиатура
    key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')  # кнопка «Да»
    keyboard1.add(key_yes)  # добавляем кнопку в клавиатуру
    key_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard1.add(key_no)
    question = 'Твой номер телефона ' + new_employeer.phone_number + ' и тебя зовут ' + new_employeer.name + ' ' + new_employeer.second_name + '?'
    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard1)


def create_employee_table():
    con = sqlite3.connect(db_name)
    cursor = con.cursor()
    print(new_employeer.get_info())
    cursor.execute("CREATE TABLE 'employee' ('id' INTEGER NOT NULL,'name' TEXT NOT NULL,'second_name' TEXT NOT NULL,'phone_number' TEXT NOT NULL,"
                   "'telegram_id' INTEGER NOT NULL,'employee_group' TEXT NOT NULL,PRIMARY KEY('id'))")
    cursor.close()
    con.close()
    print("employee table was create")



if __name__ == '__main__':

    print("start bot...")
    # create_employee_table()
    bot.polling(none_stop=True, interval=0)
