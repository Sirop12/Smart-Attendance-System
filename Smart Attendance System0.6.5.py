import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk

# Existing imports
import os
import cv2
from deepface import DeepFace
import speech_recognition
import pyautogui as gui
import pygame
import time
import hashlib
from datetime import datetime
import sqlite3 as sq
import pandas as pd
import numpy as np
import telebot

bot = telebot.TeleBot("7261830610:AAEaaXmk0rtmnExOvFn_pbo97gfmwTg0jpw")

sa = int(input("debag mod: "))
ss = int(input("Camera index, please: "))
# Подключение к базе данных SQLite
pars = r'C:\\admin'

connect = sq.connect(pars + r"\data\db_admin.db", check_same_thread=False)

cursor = connect.cursor()

# Загрузка данных из базы лиц

# Инициализация Pygame для работы со звуком
pygame.mixer.init()


# Функция для поиска лица в базе данных
def find_person(face_img_path):
    identity = None
    cursor.execute('SELECT * FROM Users')
    users = cursor.fetchall()
    for user in users:
        #user_id, FstName, LstName, photo_path, trash1, trash2 = user
        user_id, FstName, LstName, photo_path = user[:4]

        try:
            result = DeepFace.verify(face_img_path, photo_path, model_name='Facenet512')
            if result.get('verified'):
                identity = {
                    'ID': user_id,
                    'FstName': FstName,
                    'LstName': LstName,
                    'photo_path': photo_path
                }
                break
        except Exception as e:
            print(f"Ошибка при проверке лица: {e}")
            continue

    return identity


# Функция для записи и распознавания речи
def record_and_recognize_audio(*args: tuple):
    time.sleep(0.5)
    recognizer = speech_recognition.Recognizer()
    microphone = speech_recognition.Microphone()
    """
    Запись и распознавание аудио
    """
    debag = sa
    if debag != 1:
        with microphone:
            recognized_data = ""

            # регулирование уровня окружающего шума
            recognizer.adjust_for_ambient_noise(microphone, duration=2)

            try:
                print("СЛУШАЮ...")
                audio = recognizer.listen(microphone, 5, 5)

            except speech_recognition.WaitTimeoutError:
                print("ПРОВЕРЬТЕ МИКРОФОН")
                pygame.mixer.music.load('../sound/check_micro.mp3')
                pygame.mixer.music.play()
                time.sleep(2)

                return

            # использование online-распознавания через Google
            try:
                print("ОБРАБОТКА...")
                pygame.mixer.music.load(r'C://admin/data/sound/wait.mp3')
                pygame.mixer.music.play()
                time.sleep(2.3)

                recognized_data = recognizer.recognize_google(audio, language="ru").lower()

            except speech_recognition.UnknownValueError:
                pass

            # в случае проблем с доступом в Интернет происходит выброс ошибки
            except speech_recognition.RequestError:
                print("ПРОВЕРЬТЕ ИНТЕРНЕТ СОЕДИНЕНИЕ")
                pygame.mixer.music.load('../sound/check_Internet_connect.mp3')
                pygame.mixer.music.play()
                time.sleep(2)

                return
            return recognized_data
    else:
        return input("Включен режим отладки, напишите в консоль то, сказали бы: ")


# Функция для получения данных из таблицы data
def getData(name):
    cursor.execute(f'SELECT `Value` FROM `data` WHERE `Name` = "{name}"')
    result = cursor.fetchone()
    return None if result is None else result[0]


# Функция для получения данных из таблицы Users
def getUData(name, id):
    print(f"Get {name} id - {id}")
    cursor.execute(f'SELECT `{name}` FROM `Users` WHERE `ID` = {id}')
    result = cursor.fetchone()
    return None if result is None else result[0]


# получение id
def getUID(fst_name, lst_name):
    print(f"Get id for {fst_name} {lst_name}")
    cursor.execute(f'''SELECT `ID` FROM `Users` WHERE `FstName` = "{fst_name}" AND `LstName` = "{lst_name}"''')
    result = cursor.fetchone()
    return None if result is None else result[0]


# Функция для получения данных из таблицы Vizitsф
def getVData(name, id):
    print(f"Get {name} id - {id}")
    cursor.execute(f'SELECT `{name}` FROM `Vizits` WHERE `IDV` = {id}')
    result = cursor.fetchone()
    return None if result is None else result[0]


# Функция для записи данных в таблицу Vizits
def writeVData(st, znach, id=-1):
    print(f"write visits into {st} {znach}, id - {id}")
    cursor.execute(f'SELECT * FROM Vizits WHERE `IDV` = "{id}"')
    result = cursor.fetchone()
    znach = str(znach)
    if result is None:
        cursor.execute(f'INSERT INTO Vizits ({st}) VALUES (?)', (int(znach) if znach.isdigit() else znach,))
    else:
        cursor.execute(f'UPDATE Vizits SET `{st}` = ? WHERE `IDV` = ?', (int(znach) if znach.isdigit() else znach, id))
    connect.commit()


# Функция для записи данных в таблицу data
def writeData(name, value):
    print(f"write data into {name}, {value}")
    cursor.execute(f'SELECT `Name` FROM data WHERE `Name` = "{name}"')
    result = cursor.fetchone()
    value = str(value)
    if result is None:
        cursor.execute(f'INSERT INTO data (Name, Value) VALUES (?, ?)',
                       (name, int(value) if value.isdigit() else value))
    else:
        cursor.execute(f'UPDATE data SET Value = ? WHERE Name = ?', (value, name))
    connect.commit()


# Функция для записи данных в таблицу Users
def writeUData(st, znach, id=-1):
    print(f"write users into {st} {znach}, id - {id}")
    cursor.execute(f'SELECT * FROM Users WHERE `ID` = "{id}"')
    result = cursor.fetchone()
    znach = str(znach)
    if result is None:
        cursor.execute(f'INSERT INTO Users ({st}) VALUES (?)', (int(znach) if znach.isdigit() else znach,))
    else:
        cursor.execute(f'UPDATE Users SET `{st}` = ? WHERE `ID` = ?', (int(znach) if znach.isdigit() else znach, id))
    connect.commit()


# Функция для проверки наличия пользователя по ID
def check(id):
    print(f"check id - {id}")
    cursor.execute(f'SELECT * FROM Users WHERE `ID` = {id}')
    result = cursor.fetchone()
    return result is not None


# Функция для получения ID класса по названию
def getClassID(klass=""):
    i = 1
    klass = klass.title()
    print(f"Ищем класс: {klass}")  # Отладочное сообщение
    while getData(name=f"n{i}") is not None:

        checkSps = getData(name="n" + str(i)).split()
        print(f"Сравниваем с: {checkSps}")  # Отладочное сообщение
        for checkword in checkSps:
            print(f"Сравниваем с: {checkword}")
            if checkword in klass:
                print(f"Найдено совпадение: {checkword} с ID {i}")  # Отладочное сообщение
                return i
        i += 1
    print("Класс не найден")  # Отладочное сообщение
    return -1


# Режим форматирования
def format_mode():
    # подтвердите что являетесь доверенным лицом
    pygame.mixer.music.load(pars + '\data\sound\check_admin.mp3')
    pygame.mixer.music.play()
    password = gui.password("Введите пароль", "Администратор", mask="*")
    if password is None:
        return
    print("Enter password  :", hashlib.sha256(password.encode()).hexdigest())
    print("Correct password:", "03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4")
    if hashlib.sha256(
            password.encode()).hexdigest() == "03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4":
        format_ = ''
        while format_ == "" or format_ == None or not (format_ in ("1", "2", "3", "4")):
            format_ = gui.prompt("Что нужно отформатировать? \n"
                                 "1 - БД(всю)\n"
                                 "2 - Пароль от настроек\n"
                                 "3 - Пользователи и посещения\n"
                                 "4 - Прочие данные (кружки, пароли и тд)")
        sure = gui.confirm("Уверенны?", "Администратор", buttons=["ДА", "ОТМЕНА"])
        if sure == "ДА":
            if format_ == '1':
                cursor.execute("DELETE FROM Users")
                cursor.execute("DELETE FROM data")
                connect.commit()
                clear()
                gui.alert('Для входа в режим настройки, автоматически установлен пароль "1234"',
                          "Администратор")
                writeData("password", "03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4")
            elif format_ == '2':
                gui.alert('Для входа в режим настройки, автоматически установлен пароль "1234"',
                          "Администратор")
                writeData("password", "03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4")
                connect.commit()
            elif format_ == '3':
                cursor.execute("DELETE FROM Users")
                connect.commit()
                clear()
            elif format_ == '4':
                cursor.execute("DELETE FROM data")
                connect.commit()
                gui.alert('Для входа в режим настройки, автоматически установлен пароль "1234"',
                          "Администратор")
                writeData("password", "03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4")



# Function to show an alert message
def show_message(title, message):
    tk.messagebox.showinfo(title, message)

# Function to prompt for a password
def prompt_password(title, prompt):
    return tk.simpledialog.askstring(title, prompt, show='*')

# Function to prompt for input
def prompt_input(title, prompt):
    return tk.simpledialog.askstring(title, prompt)


# Function to confirm an action
def confirm_action(title, prompt):
    return tk.messagebox.askyesno(title, prompt)

# Function to update the user interface with the new data
def update_user_list(tree):
    for i in tree.get_children():
        tree.delete(i)
    cursor.execute("SELECT * FROM Users")
    result = cursor.fetchall()
    for row in result:
        tree.insert("", "end", values=row)






def update_data_list(tree):
    for i in tree.get_children():
        tree.delete(i)
    cursor.execute("SELECT * FROM Data")
    result = cursor.fetchall()
    for row in result:
        tree.insert("", "end", values=row)




def search_user(search_var, tree):
    search_term = search_var.get()
    print(f"Searching for: {search_term}")  # Отладочное сообщение
    for i in tree.get_children():
        tree.delete(i)
    cursor.execute("SELECT * FROM Users WHERE FstName LIKE ? OR LstName LIKE ?", 
                   ('%' + search_term + '%', '%' + search_term + '%'))
    result = cursor.fetchall()
    print(f"Search results: {result}")  # Отладочное сообщение
    for row in result:
        tree.insert("", "end", values=row)

def clear_search(search_var, tree):
    search_var.set("")
    update_user_list(user_tree)

def admin_mode():
    pygame.mixer.music.load(pars + '\data\sound\check_admin.mp3')
    pygame.mixer.music.play()

    password = prompt_password("Администратор", "Введите пароль")
    if not password:
        return

    print("Enter password  :", hashlib.sha256(password.encode()).hexdigest())
    print("Correct password:", getData("password"))
    if hashlib.sha256(password.encode()).hexdigest() == getData("password"):
        pygame.mixer.music.load(pars + r'\data\sound\set.mp3')
        pygame.mixer.music.play()

        root = tk.Tk()
        root.title("Admin Mode")
        root.geometry("600x400")

        tab_control = ttk.Notebook(root)

        users_tab = ttk.Frame(tab_control)
        data_tab = ttk.Frame(tab_control)

        tab_control.add(users_tab, text='Users')
        tab_control.add(data_tab, text='Data')

        tab_control.pack(expand=1, fill='both')

        # Users tab
        users_frame = ttk.Frame(users_tab)
        users_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        search_frame = ttk.Frame(users_tab)
        search_frame.pack(side=tk.TOP, fill=tk.X)

        search_label = ttk.Label(search_frame, text="Search:")
        search_label.pack(side=tk.LEFT, padx=5, pady=5)

        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)

        search_button = ttk.Button(search_frame, text="Search", command=lambda: search_user(search_var, user_tree))
        search_button.pack(side=tk.LEFT, padx=5, pady=5)

        clear_search_button = ttk.Button(search_frame, text="Clear Search", command=lambda: clear_search(search_var, user_tree))
        clear_search_button.pack(side=tk.LEFT, padx=5, pady=5)




        def on_data_double_click(event):
            item = data_tree.selection()[0]
            col = data_tree.identify_column(event.x)
            col_index = int(col.replace("#", "")) - 1
            old_value = data_tree.item(item, "values")[col_index]
            new_value = simpledialog.askstring("Edit Value", "Enter new value:", initialvalue=old_value)
            
            if new_value:
                col_name = data_tree.heading(col)["text"]
                row_id = data_tree.item(item)["values"][0]  # Assuming the first column is a unique ID
                cursor.execute(f"UPDATE Data SET \"{col_name}\" = ? WHERE Name = ?", (new_value, row_id))
                connect.commit()
                update_data_list(data_tree)



        def on_user_double_click(event):
            item = user_tree.selection()[0]
            col = user_tree.identify_column(event.x)
            col_index = int(col.replace("#", "")) - 1
            old_value = user_tree.item(item, "values")[col_index]
            new_value = simpledialog.askstring("Edit Value", "Enter new value:", initialvalue=old_value)
    
            if new_value:
                col_name = user_tree.heading(col)["text"]
                user_id = user_tree.item(item)["values"][0]  # Assuming the first column is a unique ID
                cursor.execute(f"UPDATE Users SET \"{col_name}\" = ? WHERE ID = ?", (new_value, user_id))
                connect.commit()
                update_user_list(user_tree)







        global user_tree
        user_tree = ttk.Treeview(users_frame, columns=('ID', 'FstName', 'LstName', 'photo_path'), show='headings')
        user_tree.heading('ID', text='ID')
        user_tree.heading('FstName', text='FstName')
        user_tree.heading('LstName', text='LstName')
        user_tree.heading('photo_path', text='photo_path')


        user_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        user_scrollbar = ttk.Scrollbar(users_frame, orient="vertical", command=user_tree.yview)
        user_scrollbar.pack(side=tk.RIGHT, fill='y')

        user_tree.configure(yscroll=user_scrollbar.set)


        update_user_list(user_tree)
        user_tree.bind("<Double-1>", on_user_double_click)


        def add_user():
            try:
                FstName = prompt_input("Add User", "Enter first name:")
                LstName = prompt_input("Add User", "Enter last name:")
                if FstName and LstName:
                    cursor.execute(f'INSERT INTO Users (`FstName`, `LstName`) VALUES (?, ?)', (FstName, LstName))
                    connect.commit()
                    UID = getUID(FstName, LstName)
                    writeUData("photo_path", f"C://admin/data/photo/{UID}.jpg", UID)

                    cap = cv2.VideoCapture(0)
                    if not cap.isOpened():
                        show_message("Error", "Cannot open camera")
                        return

                    while True:
                        ret, frame = cap.read()
                        if not ret:
                            show_message("Error", "Failed to capture image from camera.")
                            break

                        cv2.imshow('Camera', frame)
                        key = cv2.waitKey(1)
                        response = gui.confirm("Убедитесь, что камера видит человека.", "Администратор", buttons=["ОБОНОВИТЬ", "ГОТОВО"])

                        if response == "ГОТОВО":
                            cv2.imwrite(f"C://admin/data/photo/{UID}.jpg", frame)
                            break

                    cap.release()
                    cv2.destroyAllWindows()
                    update_user_list(user_tree)

            except Exception as e:
                print("Произошла ошибка:", e)

        def delete_user():
            selected_item = user_tree.selection()[0]
            user_id = user_tree.item(selected_item)['values'][0]
            cursor.execute(f"DELETE FROM Users WHERE ID = {int(user_id)}")
            connect.commit()
            update_user_list(user_tree)

        def update_user():
            selected_item = user_tree.selection()[0]
            user_id = user_tree.item(selected_item)['values'][0]
            column = prompt_input("Update User", "Enter column to update:")
            value = prompt_input("Update User", "Enter new value:")
            if column and value:
                writeUData(column, value, user_id)
                update_user_list(user_tree)

        def commit_changes():
            connect.commit()
            show_message("Admin", "Changes committed!")

    
            
        btn_frame = ttk.Frame(users_tab)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X)

        add_btn = ttk.Button(btn_frame, text="Add User", command=add_user)
        add_btn.pack(side=tk.LEFT)

        update_btn = ttk.Button(btn_frame, text="Update User", command=update_user)
        update_btn.pack(side=tk.LEFT)

        delete_btn = ttk.Button(btn_frame, text="Delete User", command=delete_user)
        delete_btn.pack(side=tk.LEFT)

        commit_btn = ttk.Button(btn_frame, text="Commit Changes", command=commit_changes)
        commit_btn.pack(side=tk.LEFT)

        # Data tab
        data_frame = ttk.Frame(data_tab)
        data_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        data_tree = ttk.Treeview(data_frame, columns=('Name', 'Value'), show='headings')
        data_tree.heading('Name', text='Name')
        data_tree.heading('Value', text='Value')

        data_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        data_scrollbar = ttk.Scrollbar(data_frame, orient="vertical", command=data_tree.yview)
        data_scrollbar.pack(side=tk.RIGHT, fill='y')

        data_tree.configure(yscroll=data_scrollbar.set)

        update_data_list(data_tree)

        data_tree.bind("<Double-1>", on_data_double_click)




        def add_data():
            key = prompt_input("Add Data", "Enter key:")
            value = prompt_input("Add Data", "Enter value:")
            if key and value:
                cursor.execute(f'INSERT INTO Data (`Name`, `Value`) VALUES (?, ?)', (key, value))
                connect.commit()
                update_data_list(data_tree)

        def update_data():
            selected_item = data_tree.selection()[0]
            name = data_tree.item(selected_item)['values'][0]
            value = prompt_input("Update Data", "Enter new value:")
            if value:
                cursor.execute(f"UPDATE Data SET `Value` = ? WHERE `Name` = ?", (value, name))
                connect.commit()
                update_data_list(data_tree)

        def delete_data():
            selected_item = data_tree.selection()[0]
            name = data_tree.item(selected_item)['values'][0]
            cursor.execute(f"DELETE FROM Data WHERE `Name` = ?", (name,))
            connect.commit()
            update_data_list(data_tree)



        def add_data():
            try:
                key = prompt_input("Add Data", "Enter key:")
                value = prompt_input("Add Data", "Enter value:")
                if key and value:
                    cursor.execute(f'INSERT INTO Data (`Name`, `Value`) VALUES (?, ?)', (key, value))
                    connect.commit()
                    update_data_list(data_tree)
            except Exception as e:
                 print("Произошла ошибка:", e)


            # Кнопки команд для вкладки данных
        data_btn_frame = ttk.Frame(data_tab)
        data_btn_frame.pack(side=tk.BOTTOM, fill=tk.X)

        add_data_btn = ttk.Button(data_btn_frame, text="Add Data", command=add_data)
        add_data_btn.pack(side=tk.LEFT)

        update_data_btn = ttk.Button(data_btn_frame, text="Update Data", command=update_data)
        update_data_btn.pack(side=tk.LEFT)

        delete_data_btn = ttk.Button(data_btn_frame, text="Delete Data", command=delete_data)
        delete_data_btn.pack(side=tk.LEFT)

    # Командные кнопки для вкладки пользователей
        btn_frame = ttk.Frame(users_tab)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X)




        root.mainloop()



    else:
        pygame.mixer.music.load(pars + r'\data\sound\uncorrect.mp3')
        pygame.mixer.music.play()
        time.sleep(2)


# Функция для записи данных в Excel файл
def log_to_excel(person, klass, cur_dt):
    file_path = pars + r'\data\log.xlsx'  # Specify the path to the Excel file
    data = {
        "Имя": [person['FstName']],
        "Фамилия": [person['LstName']],
        "Класс": [klass],
        "Дата": [cur_dt.strftime("%Y-%m-%d")],
        "Время": [cur_dt.strftime("%H:%M:%S")]
    }
    df = pd.DataFrame(data)

    try:
        # Try to append data to the existing Excel file
        existing_df = pd.read_excel(file_path)
        df = pd.concat([existing_df, df], ignore_index=True)
    except FileNotFoundError:
        # If the file does not exist, create a new one
        pass

    df.to_excel(file_path, index=False)
    print(f"Лог записан в файл {file_path}")


# Функция для отчистуи xlsx
def clear():
    file_path = pars + r'\data\log.xlsx'  # Specify the path to the Excel file
    # Создаем пустой dataFrame
    df = pd.DataFrame()

    # Сохраняем его в Excel-файл, очищая все данные
    df.to_excel(file_path, index=False)
    print(f"Файл {file_path} был очищен.")


def send_telegram_message(person):
    try:
        message = f"Пришёл ученик: {person['FstName']} {person['LstName']} в {datetime.now().strftime('%H:%M:%S')}"
        bot.send_message("1323639041", message)  # Замените "YOUR_CHAT_ID" на ваш ID чата в Telegram
    except Exception as e:
        print(f"Ошибка при отправке сообщения в Telegram: {e}")




# Основная часть программы


camera_index = ss
camera = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
recent_people_ids = []  # Список для хранения последних пяти ID
if getData("password") == None:
    gui.alert('Для входа в режим настройки, автоматически установлен пароль "1234"', "Администратор")
    writeData("password", "03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4")

if getData("admins") == None:
    writeData("admins", "")

while True:
    ret, frame = camera.read()
    cv2.imshow('Camera', frame)
    # sleep(0.5)
    cv2.waitKey(1)

    person = find_person(frame)
    if person:
        cur_dt = datetime.now()
        lTimeMin = getUData("PrevTime", person["ID"])
        lDay = getUData("PrevDay", person["ID"])
        curDay = cur_dt.month * 100 + cur_dt.day
        curMin = cur_dt.hour * 100 + cur_dt.minute
        print(curDay - lDay == 0, abs(curMin - lTimeMin) < 30, not (str(person['ID']) in getData("admins").split()),
              getData("admins").split())
        if (curDay - lDay == 0 and abs(curMin - lTimeMin) < 30) and not (
                str(person['ID']) in getData("admins").split()):
            print("Дублей игнорируем!!!")
            continue

        print(f"Имя: {person['FstName']}, Фамилия: {person['LstName']}")
        pygame.mixer.music.load(pars + r'\data\sound\hello.mp3')
        pygame.mixer.music.play()
        time.sleep(1.5)

        voice_input = record_and_recognize_audio()
        if voice_input:
            toSettings = ["настройк", "администратор", "админ", "команды"]
            ToFormat_ = ["форматирование", 'отчистка']
            in_ = voice_input.split()
            for word in in_:
                for checkWordIndex in range(4):
                    if checkWordIndex < len(toSettings):
                        if toSettings[checkWordIndex] == word:
                            admin_mode()
                            break
                    if checkWordIndex < len(ToFormat_):
                        if ToFormat_[checkWordIndex] == word:
                            format_mode()
                            break
            else:
                if (curDay - lDay == 0 and abs(curMin - lTimeMin) < 30):
                    print("Дублей игнорируем!!!")
                    continue
                classID = getClassID(klass=voice_input)
                if classID != -1:
                    pygame.mixer.music.load(pars + r'\data\sound\succses.mp3')
                    pygame.mixer.music.play()
                    cur_dt = datetime.now()
                    print(cur_dt.year, cur_dt.month, cur_dt.day, cur_dt.hour, cur_dt.minute)

                    # Log the data to Excel
                    log_to_excel(person, voice_input, cur_dt)
                    curDay = cur_dt.month * 100 + cur_dt.day
                    curMin = cur_dt.hour * 100 + cur_dt.minute
                    writeUData("PrevTime", cur_dt.hour * 100 + cur_dt.minute, person["ID"])
                    writeUData("PrevDay", cur_dt.month * 100 + cur_dt.day, person["ID"])
                    connect.commit()
                    print(f"{person['FstName']} {person['LstName']} направляется {voice_input}")
                    send_telegram_message(person)

                    # Обновление списка последних пяти ID
                else:
                    print(f"Класс с именем '{voice_input}' не найден.")  # Отладочное сообщение
                    pygame.mixer.music.load(r'C://admin/data/sound/ERR_use.mp3')
                    pygame.mixer.music.play()
                    time.sleep(3)
        else:
            print("Не удалось распознать голосовую команду.")
    else:
        print("Фотография не найдена в базе данных.")

camera.release()
cv2.destroyAllWindows()
#  pyinstaller --onefile D:\admin\skripts\code_final.py
