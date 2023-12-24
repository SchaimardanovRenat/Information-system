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

c.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        data TEXT NOT NULL,
        user_id INTEGER,
        price TEXT NOT NULL,
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
c.execute('''create table if not exists admin (
                id integer primary key autoincrement,

                foreign key (user_id) references users (user_id)
              )''')


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
        c.execute("INSERT INTO sotrudniki (name, data, user_id, age) VALUES (?, ?, ?, ?)",
                  (name, hashed_password, role, age))
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
        return user  # возвращаем информацию о пользователе
    else:
        print("Неверные данные для авторизации.")
        return None


def user_menu():
    print("меню пользователя:")
    print("1. просмотреть товары в корзине")
    print("2. добавить товар в корзину")
    print("3. удалить товар из корзины")
    print("4. оформить заказ")
    print("5. отфильтровать товары по цене")

    choice = input("выберите действие (1-5): ")

    if choice == "1":
        user_id = input("введите id пользователя: ")
        view_cart_items(user_id)
    elif choice == "2":
        user_id = input("введите id пользователя: ")
        item_id = input("введите id товара для добавления в корзину: ")
        add_to_cart(user_id, item_id)
    elif choice == "3":
        user_id = input("введите id пользователя: ")
        item_id = input("введите id товара для удаления из корзины: ")
        remove_from_cart(user_id, item_id)
    elif choice == "4":
        user_id = 1  # здесь нужно получить идентификатор пользователя
        order_id = input("введите id заказа: ")
        item_id = input("введите id товара: ")
        quantity = int(input("введите количество товара: "))

        # выполнение SQL-запроса
        c.execute('''
            INSERT INTO orders (name, data, user_id, price)
            VALUES (?, ?, ?, ?)
        ''', (order_id, item_id, user_id, quantity))

        # сохранение изменений
        conn.commit()

    elif choice == "5":
        min_price = int(input("введите минимальную цену: "))
        max_price = int(input("введите максимальную цену: "))
        filter_items_by_price(min_price, max_price)
    else:
        print("некорректный ввод данных. попробуйте снова.")


# функция для просмотра товаров в корзине пользователя
def view_cart_items(user_id):
    c.execute("select * from orders where user_id = ?", (user_id,))
    cart_items = c.fetchall()
    if not cart_items:
        print("ваша корзина пуста.")
    else:
        print("товары в корзине:")
        for item in cart_items:
            print(f"id товара: {item[0]}, название: {item[1]}, количество: {item[2]}")


# функция для добавления товара в корзину пользователя
def add_to_cart(user_id, item_id):
    c.execute("select * from sklad_of_items where id = ?", (item_id,))
    item = c.fetchone()
    if item:
        item_id = item[0]
        item_name = item[1]
        item_data = item[2]
        item_price = item[3]
        c.execute("insert into orders (item_id, user_id, name, data, price, quantity) values (?, ?, ?, ?, ?, ?)",
                  (item_id, user_id, item_name, item_data, item_price, 1))
        conn.commit()
        print(f"товар \"{item_name}\" добавлен в корзину пользователя!")
    else:
        print("такого товара не существует.")


# функция для удаления товара из корзины пользователя
def remove_from_cart(user_id, item_id):
    c.execute("delete from orders where item_id = ? and user_id = ?", (item_id, user_id))
    conn.commit()
    print("товар удален из корзины пользователя!")


# функция для сохранения заказа
def save_order(user_id, order_id, item_id, quantity):
    c.execute("select * from sklad_of_items where id = ?", (item_id,))
    item = c.fetchone()
    if item:
        item_name = item[1]
        item_price = item[3]
        c.execute("insert into orders (user_id, order_id, item_id, name, price, quantity) values (?, ?, ?, ?, ?, ?)",
                  (user_id, order_id, item_id, item_name, item_price, quantity))
        conn.commit()
        print("заказ успешно оформлен!")
    else:
        print("такого товара не существует.")


# функция для фильтрации товаров по цене
def filter_items_by_price(min_price, max_price):
    c.execute("select * from orders where price >= ? and price <= ?", (min_price, max_price))
    filtered_items = c.fetchall()
    if not filtered_items:
        print("товары не найдены.")
    else:
        print("отфильтрованные товары:")
        for item in filtered_items:
            print(f"id товара: {item[0]}, название: {item[1]}, количество: {item[2]}")


# функция для просмотра и удаления данных из таблицы sklad
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


# функция для просмотра, изменения и удаления данных пользователей и сотрудников
def admin_menu():
    print("Меню администратора:")
    print("1. Просмотреть данные пользователей")
    print("2. Изменить данные пользователя")
    print("3. Удалить пользователя")
    print("4. Просмотреть данные сотрудников")
    print("5. Изменить данные сотрудника")
    print("6. Удалить сотрудника")
    print("7. Фильтроватть данные о возрасте сотрудников")
    # посмотреть склад
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
    # sotrudnik_id no such column in
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
            register(username, password, role)

        elif choice == "2":
            username = input("Введите имя пользователя: ")
            password = input("Введите пароль: ")
            role = input("Выберите роль: ")
            user = login(username, password, role)
            user_id = user[0]

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

