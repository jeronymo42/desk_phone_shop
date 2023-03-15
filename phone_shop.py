import tkinter as tk
from tkinter import messagebox
import psycopg2

connection = psycopg2.connect(
    database='phoneshop',
    user='postgres',
    password='j7074225',
    host='localhost',
    port='5432'
)
cursor = connection.cursor()

screen = tk.Tk()
screen.geometry('300x300')
screen.title('Приложение продажи телефонов')
frame = tk.LabelFrame(
    screen,
    text='Варианты',
    bg='#f0f0f0',
    font=14,
    height=150,
    width=150
)
flag_phones_show = False


def admin_show(current_screen, rights):
    '''Функция при передаче информации о текущем окне и правах пользователя генерирует
    1й экран для кабинета админимтратора, уничтожая предыдущее окно
    '''

    current_screen.destroy()
    screen_admin_goods = tk.Tk()
    screen_admin_goods.title('Кабинет администратора')
    screen_admin_goods.geometry('1200x400')
    phones_button = tk.Button(text='Телефоны',
                              command=lambda current_screen=screen_admin_goods, rights=1: show_phones(current_screen, rights)).pack()
    user_button = tk.Button(text='Пользователи',
                            command=lambda current_screen=screen_admin_goods: show_users(current_screen)).pack()

def show_phones(current_screen, user_rights):
    '''Функция при передаче информации о текущем окне и правах пользователя
    запрашивает у БД информацию о телефонах и выводит ее на экран. В случае если пользователь
    является администратором, то дополнительно выводятся кнопки для удаления или добавления телефонов в БД.
    При изменении в БД необходимо повторно открыть меню.
    '''
    global flag_phones_show
    if not flag_phones_show:
        q_phones = '''SELECT * FROM phones'''
        cursor.execute(q_phones)
        result = list(cursor.fetchall())
        frame_phones = tk.LabelFrame(
            current_screen,
            text='База телефонов',
            bg='#f0f0f0',
            font=14,
            height=500,
            width=700)
        titles = ['Название', 'Память', 'RAM', 'Процессор']
        for i in range(1, len(titles)+1):
            t = tk.Entry(frame_phones, width=20,
                fg='black', justify='center')
            t.grid(row=0, column=i, padx=10)
            t.insert(i-1, titles[i-1])
        for i in range(len(result)):
            for j in range(1, len(result[i])):
                e = tk.Entry(frame_phones, width=20,
                fg='blue')
                e.grid(row=i+1, column=j, padx=10)
                e_list = result[i][j]
                if j == (len(result[i]) - 1) and i != (len(result)) and user_rights:
                    del_button = tk.Button(frame_phones, text='Удалить',
                                           command=lambda id=result[i][0], screen=current_screen: del_phone(id, screen))
                    del_button.grid(row=i+1, column = len(result[i]))
                e.insert(j, e_list)
        if user_rights:
            add_button = tk.Button(frame_phones, text='Добавить телефон',
                                command=add_phone)
            add_button.grid(row=len(result) + 1, column=1)    
        frame_phones.pack()
        flag_phones_show = True
    else:
        flag_phones_show = False
        admin_show(current_screen, user_rights)

def del_user(id):
    '''Функция "удаляет" пользователя из БД - параметр exist приравнивается к False
    При изменении в БД необходимо повторно открыть меню.
    '''
    if id:
        q_del_user = """
                UPDATE users SET exist = 'False'
                WHERE id = """ + str(id)
        cursor.execute(q_del_user)
        connection.commit()
        messagebox.showinfo("Удаление", "Пользователь удалён!")

def update_user(id):
    '''Функция дает пользователю права администратора / забирает права.
    В БД - параметр rights приравнивается к True (соответствует правам администратора),
    если было False и наоборот.
    При изменении в БД необходимо повторно открыть меню.
    '''
    if id:
        q_users = '''SELECT * FROM users
        WHERE id=''' + str(id)
        cursor.execute(q_users)
        q_result = list(cursor.fetchall())
        q_update_user = """
                UPDATE public.users SET rights=""" + ('False' if q_result[0][5] else 'True') + """ WHERE id = """ + str(id)
        cursor.execute(q_update_user)
        connection.commit()
        messagebox.showinfo("Изменение", "Права пользователя изменены!")

    

def show_users(current_screen):
    '''Функция при передаче информации о текущем окне выводит на экран информацию о пользователях,
    уничтожая предыдущее окно.
    '''
    global flag_phones_show
    if not flag_phones_show:
        q_users = '''SELECT * FROM users'''
        cursor.execute(q_users)
        result = list(cursor.fetchall())
        frame_users = tk.LabelFrame(
            current_screen,
            text='База пользователей',
            bg='#f0f0f0',
            font=14,
            height=500,
            width=800)
        titles = ['Фамилия', 'Имя', 'Отчество', 'Логин', 'Пароль', 'Администратор', 'Существует']
        for i in range(len(titles)):
            u = tk.Entry(frame_users, width=20,
                        fg='black', justify='center')
            u.grid(row=0, column=i, padx=10)
            u.insert(i, titles[i])
        for i in range(len(result)):
            for j in range(len(result[i])-1):
                e = tk.Entry(frame_users, width=20,
                            fg='blue')
                e.grid(row=i+1, column=j, padx=10)
                e_list = result[i][j]
                if j == (len(result[i]) - 2):
                    del_button = tk.Button(frame_users, text='Удалить',
                                           command=lambda id=result[i][7]: del_user(id))
                    del_button.grid(row=i+1, column=len(result[i]))
                    change_rights_button = tk.Button(frame_users, text='Изменить права',
                                           command=lambda id=result[i][7]: update_user(id))
                    change_rights_button.grid(row=i+1, column=(len(result[i])+1))
                e.insert(j, e_list)
        frame_users.pack()
        flag_phones_show = True
    else:
        flag_phones_show = False
        admin_show(current_screen, 1)

def del_phone(id, current_screen):
    '''Функция при передаче информации об ID и текущем окне удаляет из БД информацию о телефоне.
    При изменении в БД необходимо повторно открыть меню.
    '''
    if id:
        q_del_phone = """
                DELETE FROM phones
                WHERE id = """ + str(id)
        cursor.execute(q_del_phone)
        connection.commit()
        messagebox.showinfo("Удаление", "Телефон удалён!")
        show_phones(current_screen, 1)


def add_phone():
    '''Функция создает дополнительно окно для добавления нового телефона.
    '''
    screen_new_phone = tk.Tk()
    screen_new_phone.geometry('500x300')
    screen_new_phone.title('Добавление телефона')
    tk.Label(screen_new_phone, text='Название').pack()
    phone_name = tk.Entry(screen_new_phone)
    phone_name.pack()
    tk.Label(screen_new_phone, text='Память').pack()
    phone_memory = tk.Entry(screen_new_phone)
    phone_memory.pack()
    tk.Label(screen_new_phone, text='RAM').pack()
    phone_ram = tk.Entry(screen_new_phone)
    phone_ram.pack()
    tk.Label(screen_new_phone, text='Процессор').pack()
    phone_processor = tk.Entry(screen_new_phone)
    phone_processor.pack()
    def add_new_phone():
        phone_data = [phone_name, phone_memory,
                    phone_ram, phone_processor]
        phone_data_str = ''
        for i in phone_data:
            if not i.get():
                messagebox.showerror("Ошибка", "Не все поля заполнены!!!")
                return
            elif (isinstance(phone_memory, int) and isinstance(phone_ram, int)):
                messagebox.showerror("Ошибка", "Память и RAM должны быть целочисленными")
                return
            else:
                phone_data_str += "'" + \
                        i.get() + ["'", "', "][i != phone_data[-1]]
        q_add_new_phone = """INSERT INTO phones (name, memory, ram, processor) VALUES (""" + phone_data_str + ')'    
        cursor.execute(q_add_new_phone)
        connection.commit()
        screen_new_phone.destroy()
        messagebox.showinfo("Добавление", "Телефон добавлен!")
    add_phone = tk.Button(screen_new_phone, text='Добавить',
                          command=add_new_phone).pack()

def authorize():
    '''Функция создает 1й экран акторизации.
    '''
    screen.destroy()
    screen_auth = tk.Tk()
    screen_auth.geometry('300x300')
    screen_auth.title('Авторизация')

    def goods_store(user, rights):
        screen_auth.destroy()
        screen_goods = tk.Tk()
        screen_goods.geometry('700x400')
        screen_goods.title('Магазин телефонов')
        tk.Label(text=['Пользователь:', 'Админ:'][rights], justify='left').pack()
        tk.Label(text=user, justify='left').pack()
        if rights:
            admin_show(screen_goods, rights)
        else:
            show_phones(screen_goods, rights)
            

    def enter():
        q_auth = """
            SELECT password, rights, exist FROM users
            WHERE login = '""" + login.get() + """' AND exist = True"""
        cursor.execute(q_auth)
        quary_result = cursor.fetchone()
        if quary_result:
            if quary_result[0] == password.get():
                messagebox.showinfo("Супер", "Успешная авторизация!")
                goods_store(login.get(), quary_result[1])
        label['text'] = 'Неверный логин и/или пароль!'
    frame_login = tk.LabelFrame(
        screen_auth,
        text='Авторизация',
        bg='#f0f0f0',
        font=14,
        height=300,
        width=200
    )
    label = tk.Label(text='')
    label.pack()
    frame_login.pack()
    tk.Label(frame_login, text='Login').pack()
    login = tk.Entry(frame_login)
    login.pack()
    tk.Label(frame_login, text='Password').pack()
    password = tk.Entry(frame_login, show="*")
    password.pack()
    enter_buttom = tk.Button(frame_login, text='Войти',
                             command=enter).pack()
    

def registration():
    '''Функция позваоляет зарегистрироваться новому пользователю.'''
    screen.destroy()
    screen_reg = tk.Tk()
    screen_reg.geometry('500x300')
    screen_reg.title('Регистрация')
    tk.Label(text='Last name').pack()
    last_name = tk.Entry()
    last_name.pack()
    tk.Label(text='First name').pack()
    first_name = tk.Entry()
    first_name.pack()
    tk.Label(text='Patronimic').pack()
    patronimic = tk.Entry()
    patronimic.pack()
    tk.Label(text='Your login').pack()
    login = tk.Entry()
    login.pack()
    tk.Label(text='Your password').pack()
    password = tk.Entry(show="*")
    password.pack()
    tk.Label(text='Your password (repeat)').pack()
    password2 = tk.Entry(show="*")
    password2.pack()

    def new_user():
        user_data = [last_name, first_name, patronimic, login, password, password2]
        user_data_str = ''
        if not password.get() == password2.get():
            messagebox.showerror("Ошибка", "Пароли не совпадают!!!")
            print(password, password2)
            return
        for i in user_data[:-1]:
            if not i.get():
                messagebox.showerror("Ошибка", "Не все поля заполнены!!!")
                return
            else:
                user_data_str += "'" + i.get() + "', "
        q_new_user = """
            INSERT INTO users (last_name, first_name, patronimic, login, password, rights, exist) VALUES
            (""" + user_data_str + """
            FALSE, TRUE);
            """
        cursor.execute(q_new_user)
        connection.commit()
        messagebox.showinfo("Супер", "Вы успешно зарегистрировались!")
        
        

    enter_buttom = tk.Button(text='Зарегистрироваться',
                             command=new_user).pack()



frame.pack()
authorize = tk.Button(frame, text='Авторизация', command=authorize).pack()
registration = tk.Button(frame, text='Регистрация', command=registration).pack()

screen.mainloop()

