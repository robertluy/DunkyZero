import sqlite3 as sq

db = sq.connect('db_Dunk_Punk.db')
cur = db.cursor()


async def start_db():
    cur.execute("CREATE TABLE IF NOT EXISTS accounts("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "tg_id INTEGER, "
                "cart_id TEXT,"
                "checked INTEGER)")
    cur.execute("CREATE TABLE IF NOT EXISTS items("
                "i_id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "name TEXT, "
                "desc TEXT, "
                "price TEXT, "
                "photo BLOB, "
                "brand TEXT, "
                "visible INTEGER)")
    db.commit()


async def cmd_start_db(user_id):
    user = cur.execute("SELECT * FROM accounts WHERE tg_id = {key}".format(key=user_id)).fetchone()
    if not user:
        cur.execute("INSERT INTO accounts (tg_id) VALUES ({key})".format(key=user_id))
        db.commit()


async def add_item(state):
    async with state.proxy() as data:
        cur.execute("INSERT INTO items (name, desc, price, photo, brand, visible) VALUES (?, ?, ?, ?, ?, ?)",
                    (data['name'], data['desc'], data['price'], data['photo'], data['type'], 1))
        db.commit()
    mm = db.execute("SELECT * FROM items ORDER BY i_id DESC LIMIT 1").fetchone()
    return mm


async def del_item(state):
    async with state.proxy() as data:
        cur.execute(f"UPDATE items SET visible = 0 WHERE i_id = {data['id']}")
    db.commit()


async def ras_items():
    mas = cur.execute(f"SELECT tg_id FROM accounts").fetchall()
    db.commit()
    return mas


async def get_shirts():
    sh = []
    sh_tp = tuple(
        cur.execute(f"SELECT i_id, name, desc, price, photo FROM items WHERE visible = 1 AND brand = 't-shirt'"))
    for i in sh_tp:
        sh.append(list(i))
    db.commit()
    return sh


async def get_sneakers():
    sn = []
    sn_tp = tuple(
        cur.execute(f"SELECT i_id, name, desc, price, photo FROM items WHERE visible = 1 AND brand = 'sneakers'"))
    for i in sn_tp:
        sn.append(list(i))
    db.commit()
    return sn


async def get_others():
    ot = []
    ot_tp = tuple(
        cur.execute(f"SELECT i_id, name, desc, price, photo FROM items WHERE visible = 1 AND brand = 'others'"))
    for i in ot_tp:
        ot.append(list(i))
    db.commit()
    return ot


async def el_choose(id_acc, cart_num):
    ot = []
    ot_tp = tuple(cur.execute(f"SELECT * FROM items WHERE i_id = {cart_num}"))
    for i in ot_tp:
        ot.append(list(i))
    db.commit()
    try:
        tmp = str(db.execute(f"SELECT cart_id FROM accounts WHERE tg_id = {id_acc}").fetchone()[0])
        print(tmp)
        if tmp != 'None':
            cart_num = str(
                db.execute(f"SELECT cart_id FROM accounts WHERE tg_id = {id_acc}").fetchone()[0]) + '.' + cart_num
            print(cart_num)
    except (TypeError, AttributeError):
        pass
    mm = db.execute(f"UPDATE accounts SET cart_id = {cart_num} WHERE tg_id = {id_acc}")
    db.commit()
    return ot


async def korz_show(id_acc):
    ot = []
    cart_id = list(
        map(int, str(cur.execute(f"SELECT cart_id FROM accounts WHERE tg_id = {id_acc}").fetchone()[0]).split('.')))
    for i in cart_id:
        ot.append(list(tuple(cur.execute(f"SELECT * FROM items WHERE i_id = {i}"))[0]))
    print(ot)
    db.commit()
    return ot
