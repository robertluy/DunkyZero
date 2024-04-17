from aiogram import types, Dispatcher
from creating import dp, bot
from aiogram.dispatcher import FSMContext
from states import Catal_usveru, Del_usvera
from keyboards import keyboards_client as kb
import DatabaseDP as db
from keyboards import keyboards_admins as kba
from aiogram.dispatcher.filters import Text
import requests
import os

HELP_FILE_PATH_US = "user_help.txt"  # это файл-справка для клиента, такая структура более удобна для редактирования
HELP_FILE_PATH_AD = "admin_help.txt"  # это файл-справка для админа, такая структура более удобна для редактирования


# Функция для чтения содержимого файла справки юзвера
def read_help_file_us():
    with open(HELP_FILE_PATH_US, "r", encoding="utf-8") as file:
        return file.read()


# Функция для чтения содержимого файла справки админа
def read_help_file_ad():
    with open(HELP_FILE_PATH_AD, "r", encoding="utf-8") as file:
        return file.read()


# Функция для получения курса валюты из JSON
def get_exchange_rate(currency):
    # URL Центробанка России для получения курсов валют
    url = "https://www.cbr-xml-daily.ru/daily_json.js"
    response = requests.get(url)  # формируем запрос на получение по урл
    data = response.json()  # преобразуем данные формата json в словарь
    if currency in data['Valute']:  # Проверяем, есть ли указанная валюта в данных
        print(data['Valute'][currency]['Value'])
        return data['Valute'][currency]['Value']  # возваращаем курс
    else:
        return None  # возвращаем нан если нет информации


# Функция для конвертации валюты
def convert_currency(amount, to_currency):  # больше нужна для будущих улучшений, в основном, админу,
    # например для автоматического расчета стоимости товара клиентам по заранее установленным константам
    to_rate = get_exchange_rate(to_currency)  # получение стоимости валюты
    if to_rate is not None:
        converted_amount = amount * to_rate
        return converted_amount
    else:
        return None


# для выполнения требования тз, хотя мне это не нужно абсолютно, реализовав таким образом,
# хотя бы посмотрел как с апи обращаться
def sticker1s():
    url = 'https://api.giphy.com/v1/gifs/search?'  # URL API сервиса Giphy для поиска гифок
    params = {  # Параметры запроса
        'api_key': '7IOwQzY3vMYYE8SQYRihDBaNV3AwhlVC',  # API ключ
        'q': 'Walter White Wink GIF By Breaking Bad',  # поисковый запрос
        'limit': 1  # лимит результатов, чтобы получить 1
    }
    response = requests.get(url, params=params)  # было выше

    if response.status_code == 200:  # код 200 означает успешное выполнение запроса
        data = response.json()  # то же что и выше было
        if data['data']:
            gif_url = data['data'][0]['images']['original']['url']  # для понимания нужно перейти по ссылке
            # и посмотреть способ хранения данных
            return gif_url
        else:
            return None


# функция-вывод справки ролям
async def help_but_cl(message: types.Message):  # принимаю месседж, чтобы понять кому выводить
    if str(message.from_user.id) == os.getenv('ADMIN_ID'):  # проверка что админу
        help_text_ad = read_help_file_ad()  # получаю сообщение
        await message.answer('Вы читаете памятку помощи админу')
        await message.answer(help_text_ad)  # передаю сообщение роли
    else:  # то же самое, но другой роли
        help_text_us = read_help_file_us()
        await message.answer('Вы читаете памятку помощи клиенту')
        await message.answer(help_text_us)


# @dp.message_handler(commands=['start'])
async def start(message: types.Message):  # то что происходит при /start
    await message.answer_sticker('CAACAgIAAxkBAAMZZLD7LJq2aaGAHn-OgkVQKDkM9LgAAk0DAAJSOrAFWJ0Eu-ZdkqUvBA')
    await db.cmd_start_db(message.from_user.id,
                          message.from_user.username)  # добавляю пользователя в бд, если его там еще нет
    if str(message.from_user.id) == os.getenv('ADMIN_ID'):  # проверяю на админа, чтобы отдать правильную калвиатуру
        await message.answer(f'Вы админ', reply_markup=kba.main_admin)
    else:
        await message.answer(f'Здравствуйте, {message.from_user.first_name}', reply_markup=kb.main)
    await help_but_cl(message)  # вызываю сообщение - посянение команд, оно само определит для кого вызвается


# @dp.message_handler(text='Корзина')
async def cmd_cot(message: types.Message):  # ловлю запрос пользователя на корзину из кнопочной клавиатуры
    ot = await db.korz_show(message.from_user.id)  # получаю список товаров пользователя
    if ot == 0:  # проверка на пустоту корзины
        if str(message.from_user.id) == os.getenv('ADMIN_ID'):  # проверка кто спрашивал
            await message.answer('Пусто', reply_markup=kba.main_admin)
        else:
            await message.answer('Пусто', reply_markup=kb.main)
    else:
        for i in range(
                len(ot)):  # выдаю пользователю все данные по его карточкам согласно выбранной мной схеме хранения
            await bot.send_photo(message.from_user.id, ot[i][4])
            await bot.send_message(message.from_user.id,
                                   text=f"номер слота: {ot[i][0]},\nНазвание: {ot[i][1]},\nОписание: {ot[i][2]},"
                                        f"\nЦена: {ot[i][3]}")
        if str(message.from_user.id) == os.getenv('ADMIN_ID'):
            await message.answer('ваш заказ', reply_markup=kba.main_admin)
        else:
            await message.answer('ваш заказ', reply_markup=kb.main)


# @dp.message_handler(text='Контакты')
async def cmd_contacts(message: types.Message):  # уведомление админов о выборе товаров
    await message.answer(f'С вами скоро свяжутся @RealRobertL')
    await message.answer('Курс юаня по ЦБ: ' + str(convert_currency(1, "CNY")) + ' рубля')  # доп запрос № 1
    await message.answer('Курс доллара по ЦБ: ' + str(convert_currency(1, "USD")) + ' рубля')  # доп запрос № 2
    await bot.send_animation(message.from_user.id, sticker1s())  # основной запрос
    await bot.send_message(os.getenv('GROUP_ID'), "------------------")  # отправка уведомления в чат админов
    await bot.send_message(os.getenv('GROUP_ID'), f"!пользователь добавил товар!")
    await bot.send_message(os.getenv('GROUP_ID'), f"@{message.from_user.username}")


# @dp.message_handler(text='Каталог')
async def cmd_catalog(message: types.Message):  # показываю инлайн клаву
    await message.answer(f'Пожалуйста:', reply_markup=kb.catalog_list)


async def cmd_del_usveraaa(message: types.Message):  # вызов удаления товара
    await message.answer("Выберите действие:", reply_markup=kb.deleting_elements)
    await Del_usvera.delall.set()  # присовение состояния, чтобы ловить сообщения заданными хендлерами


async def del_all(message: types.Message, state: FSMContext):  # сюда перехожу с этим состоянием
    async with state.proxy() as data:  # Этот код использует объект состояния для временного хранения данных в рамках
        # этого класса стейта
        data['id'] = message.from_user.id  # адишник пользователя
        data['text'] = message.text  # способ удаления
    if data['text'] != 'Удалить все':  # если не этот способ, перехожу в следующее состояние
        await message.answer(f'Введите номер лота, который хотите удалить')
        await Del_usvera.next()
    else:  # если этот способ, удаляю все товары из корзины
        print(data['text'])
        await db.del_all(state)  # функция удаляющая все товары в этой корзине
        await message.answer(f'Пусто', reply_markup=kb.main)
        await state.finish()  # выход из класса состояния


async def del_this_all_first(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['num'] = message.text  # полчаю что удалить
    if data['text'] != 'Удалить все лоты номера':  # удалить первый лот номера
        print('this me', message)
        back = await db.del_this_first(state)  # выполняю удаление
        if back == 0:  # если ничего не было удалено
            await message.answer(f'Нечего удалять', reply_markup=kb.main)
        else:
            await message.answer(f'Удалено', reply_markup=kb.main)
        await state.finish()
    else:  # удалить все лоты номеру
        print(data['num'])
        back = await db.del_this_all(state)  # функция в бд
        if back == 0:
            await message.answer(f'Ничего удалять', reply_markup=kb.main)
        else:
            await message.answer(f'Удалено', reply_markup=kb.main)
        await state.finish()


async def callback_quary_keyboard(callback_query: types.CallbackQuery):  # обработка инлайн клавиатуры
    if callback_query.data == 't-shirt':  # если футболка
        sh = await db.get_shirts()
        for i in range(len(sh)):  # вывожу что есть
            await bot.send_photo(callback_query.from_user.id, sh[i][4])
            await bot.send_message(callback_query.from_user.id,
                                   text=f"номер слота: {sh[i][0]},\nНазвание:\n {sh[i][1]},\nОписание: \n {sh[i][2]},"
                                        f"\nЦена:\n {sh[i][3]}")
        await Catal_usveru.corz.set()  # состояние корзины назначаю
        await bot.send_message(callback_query.from_user.id, 'введите номер, понравившегося лота',
                               reply_markup=kb.cancel)  # возможность выйти
    elif callback_query.data == 'sneakers':  # то же но для кроссовок
        sn = await db.get_sneakers()
        for i in range(len(sn)):
            await bot.send_photo(callback_query.from_user.id, sn[i][4])
            await bot.send_message(callback_query.from_user.id,
                                   text=f"номер слота: {sn[i][0]},\nНазвание:\n {sn[i][1]},\nОписание: \n {sn[i][2]},"
                                        f"\nЦена:\n {sn[i][3]}")
        await Catal_usveru.corz.set()
        await bot.send_message(callback_query.from_user.id, 'введите номер, понравившегося лота',
                               reply_markup=kb.cancel)  # возможность выйти
    elif callback_query.data == 'others':  # то же но для другого
        ot = await db.get_others()
        for i in range(len(ot)):
            await bot.send_photo(callback_query.from_user.id, ot[i][4])
            await bot.send_message(callback_query.from_user.id,
                                   text=f"номер слота: {ot[i][0]},\nНазвание:\n {ot[i][1]},\nОписание: \n {ot[i][2]},"
                                        f"\nЦена:\n {ot[i][3]}")
        await Catal_usveru.corz.set()
        await bot.send_message(callback_query.from_user.id, 'введите номер понравившегося лота',
                               reply_markup=kb.cancel)  # возможность выйти


# @dp.message_handler(state=Catal_usveru.corz)
async def corzina_pokupaski(message: types.Message, state: FSMContext):  # перехват номера лота, выбранного юзвером
    us_id = message.from_user.id
    us_name = message.from_user.username
    ot = await db.el_choose(us_id, message.text, us_name)  # добавляю товар в корзину
    if ot == 0:  # если пусто
        await state.finish()
        await message.answer(f'неверное имя, попробуйте верное название',
                             reply_markup=kb.catalog_list)  # возвращаю того на каталог
    else:
        for i in range(len(ot)):  # вывожу то что добавили, чтобы было наглядно
            await bot.send_photo(us_id, ot[i][4])
            await bot.send_message(message.from_user.id,
                                   text=f"номер слота: {ot[i][0]},\n {ot[i][1]},\n {ot[i][2]},"
                                        f"\n {ot[i][3]}")
        await state.finish()
        if str(message.from_user.id) == os.getenv('ADMIN_ID'):
            await message.answer('добавлено', reply_markup=kba.main_admin)
        else:
            await message.answer('добавлено', reply_markup=kb.main)
            '''await bot.send_message(os.getenv('ADMIN_ID'), f"пользователь @{us_name} добавил следующий товар:")
            await bot.send_photo(os.getenv('ADMIN_ID'), ot[0][4])
            await bot.send_message(os.getenv('ADMIN_ID'),
                                   text=f"номер слота: {ot[i][0]},\n {ot[i][1]},\n {ot[i][2]},"
                                        f"\n {ot[i][3]}")'''  # убрано, так как неудобно смотреть таким образом


async def cmd_cancel(message: types.Message, state: FSMContext):  # отлавливатель отмен
    if str(message.from_user.id) == os.getenv('ADMIN_ID'):
        cur_st = await state.get_state()  # полчаю нынешнее состояние
        await message.answer(f'отменяю', reply_markup=kba.main_admin)
        if cur_st is None:
            return
        await state.finish()  # завершаю состояние
    else:
        cur_st = await state.get_state()
        await message.answer(f'отменяю', reply_markup=kb.main)
        if cur_st is None:
            return
        await state.finish()


def register_handler_client(dp: Dispatcher):  # назначение хендлеров функциям хендлеры, уже устал писать
    # комменты, здесь и так все понятно должно быть, функции и команды подписаны понятнейшим образом
    dp.register_message_handler(cmd_cancel, state='*', commands='Отмена')
    dp.register_message_handler(cmd_cancel, Text(equals='Отмена', ignore_case=True), state='*')
    dp.register_message_handler(start, commands=['start'])
    dp.register_message_handler(help_but_cl, commands=['help'])
    dp.register_message_handler(cmd_cot, text='Корзина')
    dp.register_message_handler(cmd_del_usveraaa, text='Удалить из корзины')
    dp.register_message_handler(del_all, state=Del_usvera.delall)
    dp.register_message_handler(del_this_all_first, state=Del_usvera.delthisall_first)
    dp.register_message_handler(cmd_contacts, text='Уведомить о заполнении корзины')
    dp.register_message_handler(cmd_catalog, text='Каталог')
    dp.register_message_handler(corzina_pokupaski, state=Catal_usveru.corz)
    dp.register_callback_query_handler(callback_quary_keyboard)
