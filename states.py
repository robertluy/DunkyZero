from aiogram.dispatcher.filters.state import State, StatesGroup


# различные состояния, использующиеся в коде

class NewOrder(StatesGroup):
    type = State()  # типа товара
    name = State()  # название
    desc = State()  # описание
    price = State()  # цена
    photo = State()  # фото


class Rass(StatesGroup):
    txet = State()  # текст рассылки


class Del_item(StatesGroup):
    id = State()  # ид удалямеого для всех


class Del_usvera(StatesGroup):  # пользователем в своей
    delall = State()  # удлаить все в корзине
    delthisall_first = State()  # удалить по этому номеру все или первый


class Del_usvera_admin(StatesGroup):  # админом у пользователя
    name = State()  # тег пользователя
    delall = State()  # удлаить все в корзине
    delthisall_first = State()  # удалить по жтому номеру все или первый


class Smotrim_corzinu(StatesGroup):  # админом
    zhdem_tg_name = State()  # для просмтора корзины юзера


class Catal_usveru(StatesGroup):  # для инлайн клавы
    shirt = State()
    sneakers = State()
    others = State()
    corz = State()
