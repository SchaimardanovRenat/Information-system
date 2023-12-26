import sqlite3
import hashlib

# создание подключения к базе данных
conn = sqlite3.connect('info_system.db')
c = conn.cursor()

# создание таблиц
c.execute('''CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL ,
                role TEXT NOT NULL,
                password TEXT
              )''')

c.execute('''create table if not exists sklad_of_items (
                id integer primary key autoincrement,
                name text not null,
                data text not null
              )''')
# c.execute('''ALTER TABLE sklad_of_items ADD COLUMN price REAL''')
c.execute("INSERT INTO sklad_of_items (name, data, price) VALUES ('Товар1', '2022-09-01', 10.99)")
c.execute("INSERT INTO sklad_of_items (name, data, price) VALUES ('Товар2', '2022-09-02', 19.99)")

c.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        data TEXT NOT NULL,
        user_id INTEGER,
        price REAL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
''')


c.execute('''create table if not exists sotrudniki (
                id integer primary key autoincrement,
                name text not null ,
                data text not null,
                user_id integer,
                age text not null,
                foreign key (user_id) references users (user_id)
              )''')
# c.execute('''ALTER TABLE sotrudniki ADD COLUMN age text not null''')
c.execute('''INSERT INTO sotrudniki (name, data, user_id, age) 
              VALUES (?, ?, ?, ?)''', ("Имя сотрудника", "Дата сотрудника", 1, "Возраст сотрудника"))

c.execute('''create table if not exists admin (
                id integer primary key autoincrement,
                
                foreign key (user_id) references users (user_id)
              )''')
def filter_items_by_price(min_price, max_price):
    c.execute('''SELECT * FROM sklad_of_items WHERE price >= ? and price <= ?''', (min_price, max_price))
    items = c.fetchall()
    return items
# функция для хеширования пароля
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register(username, password, role):
    allowed_roles = ['user', 'admin', 'sotrudnik']  # Список разрешенных ролей

    if role not in allowed_roles:
        print("Ошибка регистрации: выбрана недопустимая роль!")
        print("Пожалуйста, выберите одну из следующих ролей:", ", ".join(allowed_roles))
        return
    elif role == allowed_roles[0]:
        hashed_password = hash_password(password)
        c.execute("insert into users (username, password, role) values (?, ?, ?)", (username, hashed_password, role))
        conn.commit()
        print("Новый клиент добавлен")

    elif role == allowed_roles[2]:
        hashed_password = hash_password(password)
        print("Укажите ваше имя")
        name = input()
        print("Укажите ваш возраст")
        age = input()
        c.execute("INSERT INTO sotrudniki (name, data, user_id, age) VALUES (?, ?, ?, ?)", (name, hashed_password, role, age))
        conn.commit()
        print("Регистрация успешна!")
    elif role == allowed_roles[1]:
        hashed_password = hash_password(password)
        c.execute("insert into admin (username, password, role) values (?, ?, ?)", (username, hashed_password, role))
        conn.commit()
        print("Регистрация успешна!")

# функция для авторизации пользователя
def login(username, password, role):
    hashed_password = hash_password(password)
    c.execute("select * from users where username = ? and password = ? and role = ?", (username, hashed_password, role))
    user = c.fetchone()
    if user:
        print("Авторизация успешна!")
        return user
    else:
        print("Неверные данные для авторизации.")
        return None
# на пустые значения выдает ошибку
# авторизация проверка на ввод пустых и не своих значений и менб пользователя
# функция для просмотра и удаления данных из таблицы sklad
def create_user(username):
    c.execute("INSERT INTO sklad_of_items (name) VALUES (?)", (username,))
    conn.commit()
    print("Пользователь успешно создан!")

def view_items():
    c.execute("SELECT * FROM sklad_of_items")
    items = c.fetchall()
    if len(items) > 0:
        for item in items:
            print(f"ID: {item[0]}\tНаименование: {item[1]}\tДанные: {item[2]}")
    else:
        print("Корзина пуста.")

def delete_item(item_id):
    c.execute("DELETE FROM sklad_of_items WHERE id = ?", (item_id,))
    conn.commit()
    print(f"Товар с ID {item_id} успешно удален из корзины.")

def update_item(item_id, new_data):
    c.execute("UPDATE sklad_of_items SET data = ? WHERE id = ?", (new_data, item_id))
    conn.commit()
    print(f"Товар с ID {item_id} успешно обновлен.")

def filter_items(min_price, max_price):
    c.execute("SELECT * FROM sklad_of_items WHERE price BETWEEN ? AND ?", (min_price, max_price))
    items = c.fetchall()
    if len(items) > 0:
        for item in items:
            print(f"ID: {item[0]}\tНаименование: {item[1]}\tДанные: {item[2]}")
    else:
        print("Товары не найдены.")

def place_order():
    c.execute("DELETE FROM sklad_of_items")
    conn.commit()
    print("Заказ успешно оформлен.")

def user_menu():
    while True:
        print("Меню пользователя:")
        print("1. Просмотреть товары в корзине")
        print("2. Удалить товары из корзины")
        print("3. Изменить товары в корзине")
        print("4. Фильтровать товары по цене")
        print("5. Оформить заказ")
        print("6. Выйти из меню")

        choice = input("Выберите действие: ")

        if choice == "1":
            view_items()
        elif choice == "2":
            item_id = input("Введите ID товара: ")
            delete_item(item_id)
        elif choice == "3":
            item_id = input("Введите ID товара: ")
            new_data = input("Введите новые данные: ")
            update_item(item_id, new_data)
        elif choice == "4":
            min_price = float(input("Введите минимальную цену: "))
            max_price = float(input("Введите максимальную цену: "))
            filter_items(min_price, max_price)
        elif choice == "5":
            place_order()
        elif choice == "6":
            break
        else:
            print("Неверный выбор. Попробуйте еще раз.")

def sklad_menu(user_id):
    c.execute("select role from users where user_id = ?", (user_id,))
    role = c.fetchone()[0]
    if role != "sotrudnik" and role != "admin":
        print("Недостаточно прав для доступа к данным таблицы sklad!")
        return
    else:
        print("Привет, работяга!")
        print("Меню склада:")
        print("1. Просмотреть данные")
        print("2. Добавить товар")
        print("3. Удалить товар")
        print("4. Отфильтровать товар")

        choice = input("Выберите действие (1-3): ")
    if choice == "1":
        c.execute("select * from sklad_of_items")
        sklad_data = c.fetchall()
        print("Товары на складе:")
        for item in sklad_data:
            print(item)

    elif choice == "2":
        item_name = input("Введите название товара: ")
        item_data = input("Введите данные о товаре: ")
        c.execute("insert into sklad_of_items (name, data) values (?, ?)", (item_name, item_data))
        conn.commit()
        print("Товар успешно добавлен на склад!")

    elif choice == "3":
        item_id = input("Введите идентификатор товара: ")
        c.execute("delete from sklad_of_items where id = ?", (item_id,))
        conn.commit()
        print("Товар успешно удален со склада!")
    elif choice == "4":
        min_price = float(input("Введите минимальную цену товара: "))
        max_price = float(input("Введите максимальную цену товара: "))
        filtered_items = filter_items_by_price(min_price, max_price)
        for item in filtered_items:
            print(item)

# функция для просмотра, изменения и удаления данных пользователей и сотрудников
def admin_menu():
    while True:
        print("Меню администратора:")
        print("1. Просмотреть данные пользователей")
        print("2. Изменить данные пользователя")
        print("3. Удалить пользователя")
        print("4. Просмотреть данные сотрудников")
        print("5. Изменить данные сотрудника")
        print("6. Удалить сотрудника")
        print("7. Фильтроватть данные о возрасте сотрудников")
        print("8. Выйти")

        choice = input("Выберите действие (1-6): ")

        if choice == "1":
            c.execute("select * from users")
            users_data = c.fetchall()
            print("Данные пользователей:")
            for user in users_data:
                print(user)

        elif choice == "2":
            user_id = input("Введите идентификатор пользователя: ")
            new_username = input("Введите новое имя пользователя: ")
            c.execute("update users set username = ? where user_id = ?", (new_username, user_id))
            conn.commit()
            print("Данные пользователя успешно изменены!")

        elif choice == "3":
            user_id = input("Введите идентификатор пользователя: ")
            c.execute("delete from users where user_id = ?", (user_id,))
            conn.commit()
            print("Пользователь успешно удален!")

        elif choice == "4":
            c.execute("SELECT * FROM sotrudniki")
            sotrudniki_data = c.fetchall()
            print("Данные сотрудников:")
            for row in sotrudniki_data:
                print(row)

        elif choice == "5":
            sotrudnik_id = input("Введите идентификатор сотрудника: ")
            new_sotrudnik_name = input("Введите новое имя сотрудника: ")
            c.execute("update sotrudniki set name = ? where user_id = ?", (new_sotrudnik_name, sotrudnik_id))
            conn.commit()
            print("Данные сотрудника успешно изменены!")

        elif choice == "6":
            sotrudnik_id = input("Введите идентификатор сотрудника: ")
            c.execute("delete from sotrudniki where user_id = ?", (sotrudnik_id,))
            conn.commit()
            print("Сотрудник успешно удален!")
        elif choice == "7":
            min_age = input("Введите минимальный возраст: ")
            max_age = input("Введите максимальный возраст: ")
            c.execute("select * from sotrudniki where age >= ? and age <= ?", (min_age, max_age))
            filtered_data = c.fetchall()
            print("Отфильтрованные данные о сотрудниках по возрасту:")
            for row in filtered_data:
                print(row)
        elif choice == "8":
            break

# основная функция
def main():
    while True:
        print("1. Регистрация")
        print("2. Авторизация")
        print("3. Выход")
        choice = input("Выберите действие (1-3): ")

        if choice == "1":
            username = input("Введите имя пользователя: ")
            password = input("Введите пароль: ")
            role = input("выбрать роль")
            register( username, password, role)

        elif choice == "2":
            username = input("Введите имя пользователя: ")
            password = input("Введите пароль: ")
            role = input("Выберите роль: ")
            user = login(username, password, role)
            user_id = user[0]
            user_role = user[3]
            if user_id is not None:
                c.execute("SELECT role FROM users WHERE user_id = ?", (user_id,))
                role = c.fetchone()[0]
                if role == "admin":
                    print("Добро пожаловать в меню администратора!")
                    admin_menu()
                elif role == "sotrudnik":
                    print("Добро пожаловать в меню сотрудника!")
                    sklad_menu(user_id)
                elif role == "user":
                    print("Добро пожаловать в меню пользователя!")
                    user_menu()
                else:
                    print("Роль не распознана!")
            else:
                print("Необходима авторизация!")
        elif choice == "3":
            break
        else:
            print("Некорректный ввод")

    # закрытие подключения к базе данных
    conn.close()

# запуск программы
if __name__ == "__main__":
    main()

