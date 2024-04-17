import sqlite3 as sq

# соединение хорошо бы закрывать, но я уже устал, и так работает, магазин не настолько большой чтобы были сбои
# эти правки и на проде можно внести
db = sq.connect('db_Dunk_Punk.db')
# Если указанный файл не существует, он будет создан.
# Если файл существует, будет установлено соединение с ним.
cur = db.cursor()  # Создаем курсор, который используется для выполнения SQL-запросов к базе данных.


async def start_db():  # создание таблиц если их еще нет
    cur.execute("CREATE TABLE IF NOT EXISTS accounts("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "tg_id INTEGER, "
                "tg_id_name TEXT, "
                "cart_id TEXT,"
                "checked INTEGER)")
    cur.execute("CREATE TABLE IF NOT EXISTS items("
                "i_id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "name TEXT, "
                "desc TEXT, "
                "price TEXT, "
                "photo BLOB, "
                "brand TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS corz("
                "c_id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "u_id INTEGER, "
                "i_id INTEGER, "
                "tg_id INTEGER, "
                "tg_id_name TEXT, "
                "amount INTEGER, "
                "FOREIGN KEY(u_id) REFERENCES accounts(id), "
                "FOREIGN KEY(i_id) REFERENCES items(i_id)"
                ")")
    db.commit()  # пояснять не буду, тут все внешние ключи и так указаны, некоторые поля на будущее


async def cmd_start_db(user_id, user_name):  # добавление пользователя в таблицу accounts
    user = list(cur.execute(f"SELECT id FROM accounts WHERE tg_id = ?", (user_id,)))
    print(user)
    if not user:
        cur.execute("INSERT INTO accounts (tg_id, tg_id_name) VALUES (?, ?)", (user_id, user_name))
        db.commit()


async def add_item(state):  # добавление товара в items
    async with state.proxy() as data:
        cur.execute("INSERT INTO items (name, desc, price, photo, brand) VALUES (?, ?, ?, ?, ?)",
                    (data['name'], data['desc'], data['price'], data['photo'], data['type']))
        db.commit()
    mm = db.execute("SELECT * FROM items ORDER BY i_id DESC LIMIT 1").fetchone()
    return mm


async def del_all(state):  # полное удаление товара у этого пользователя
    async with state.proxy() as data:
        print(data['id'])
        cur.execute(f"DELETE FROM corz WHERE tg_id = {data['id']}")
        db.commit()


async def del_this_all(state):  # частичное полное удаление товара у пользователя
    async with state.proxy() as data:
        ot_tp = tuple(cur.execute(f"SELECT * FROM corz WHERE i_id = {data['num']} AND tg_id = {data['id']}"))
        if len(ot_tp) == 0:
            return 0
        cur.execute(f"DELETE FROM corz WHERE i_id = {data['num']} AND tg_id = {data['id']}")
        db.commit()


async def del_this_first(state):  # другое частичное удаление товара у пользователя
    async with state.proxy() as data:
        ids = tuple(cur.execute(f"SELECT c_id FROM corz WHERE i_id = {data['num']} AND tg_id = {data['id']}"))
        if len(ids) == 0:
            return 0
        else:
            print(ids[0][0])
            cur.execute(f"DELETE FROM corz WHERE c_id = {ids[0][0]} AND tg_id = {data['id']}")
        db.commit()


async def del_item(state):  # удаление товара для всех (из items)
    async with state.proxy() as data:
        print('data[id', data)
        cur.execute(f"DELETE FROM items WHERE i_id = {data['id']}")
        cur.execute(f"DELETE FROM corz WHERE i_id = {data['id']}")  # удаляю этот товар у всех из корзин
    db.commit()


async def ras_items():  # возвращаю адишники кому разослать
    mas = tuple(cur.execute(f"SELECT tg_id FROM accounts").fetchall())
    ot = []
    for i in mas:
        ot.append(list(i))
    db.commit()
    return ot


async def get_shirts():  # возвращаю футболки для вывода каталога
    sh = []
    sh_tp = tuple(
        cur.execute(f"SELECT i_id, name, desc, price, photo FROM items WHERE brand = 't-shirt'"))
    for i in sh_tp:
        sh.append(list(i))
    db.commit()
    return sh


async def get_sneakers():  # возвращаю кроссовки для вывода каталога
    sn = []
    sn_tp = tuple(
        cur.execute(f"SELECT i_id, name, desc, price, photo FROM items WHERE brand = 'sneakers'"))
    for i in sn_tp:
        sn.append(list(i))
    db.commit()
    return sn


async def get_others():  # возвращаю другое для вывода каталога
    ot = []
    ot_tp = tuple(
        cur.execute(f"SELECT i_id, name, desc, price, photo FROM items WHERE brand = 'others'"))
    for i in ot_tp:
        ot.append(list(i))
    db.commit()
    return ot


async def el_choose(id_acc, cart_num, us_name):  # добавление в корзину пользователя
    ot = []
    ot_tp = tuple(cur.execute(f"SELECT * FROM items WHERE i_id = ?", (cart_num,)))
    if len(ot_tp) == 0:
        return 0
    for i in ot_tp:
        ot.append(list(i))
    u_id = list(cur.execute(f"SELECT id FROM accounts WHERE tg_id = ?", (id_acc,)))
    print('uid', u_id)
    cur.execute("INSERT INTO corz (u_id, i_id, tg_id, tg_id_name, amount) VALUES (?, ?, ?, ?, ?)",
                (list(u_id[0])[0], cart_num, id_acc, us_name, 1))
    db.commit()
    return ot


async def korz_show(id_acc):  # демонстрация корзины пользователя
    ot = []
    cart_id = list(cur.execute(f"SELECT i_id FROM corz WHERE tg_id = ?", (id_acc,)))
    if cart_id == []:
        return 0
    for i in cart_id:
        i = list(i)[0]
        print(i)
        tmp_tovari = list(cur.execute(f"SELECT * FROM items WHERE i_id = {i}"))
        if tmp_tovari:  # проверяю что запрос выдал какие-то данные, чтобы далее не было ошибки
            ot.append(list(tuple(tmp_tovari)[0]))  # tuple потому что бд выдает кортеж,
    db.commit()
    return ot


async def get_id_from_name(name_acc):  # возвращаю tg_id по tg_name
    t = list(cur.execute(f"SELECT tg_id FROM accounts WHERE tg_id_name = ?", (name_acc,)))
    if not t:
        return 0
    else:
        return list(t[0])[0]

# все запросы в бд в этом модуле
