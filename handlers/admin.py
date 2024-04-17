from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
import keyboards as kba
import DatabaseDP as db
from creating import dp, bot
from keyboards import keyboards_admins as kba
from keyboards import keyboards_client as kb
from states import NewOrder, Rass, Del_item, Smotrim_corzinu, Del_usvera_admin
from aiogram.dispatcher.filters import Text
import os


# @dp.message_handler(text='Админ-панель')
async def cmd_admin_panel(message: types.Message):
    if str(message.from_user.id) == os.getenv('ADMIN_ID'):
        await message.answer(f'Вы вошли в админ-панель', reply_markup=kba.admin_panel)
    else:
        await message.answer(f'Не понимаю вас, {message.from_user.first_name}', kb.main)


# @dp.message_handler(text='Добавить товар')
async def cmd_add_item(message: types.Message):
    # Обработчик команды для добавления элемента
    if str(message.from_user.id) == os.getenv('ADMIN_ID'):
        # Если пользователь - администратор, переходим к следующему состоянию
        await NewOrder.type.set()
        # Устанавливаем состояние для ожидания типа нового элемента
        await message.answer('Начнем добавлять', reply_markup=kba.catalog_list)
        # предоставляем кнопки с каталогом элементов для удобства выбора
    else:
        # Если пользователь не администратор, отправляем ему сообщение с уведомлением
        await message.answer(f'Не понимаю вас, {message.from_user.first_name}', kb.main)
        # Отправляем пользователю сообщение с уведомлением о непонимании его запроса


# @dp.callback_query_handler(state=NewOrder.type)
async def add_item_type(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['type'] = call.data
        # Сохраняем тип нового элемента, полученный из callback-кнопки, в состоянии FSM
    await call.message.answer(f'название товара')
    await NewOrder.next()
    # Переходим к следующему состоянию для ожидания следующего шага добавления элемента


# @dp.message_handler(state=NewOrder.name)
async def add_item_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
        # Сохраняем введенное название нового элемента в состоянии FSM
    if data['name'] == 'Отмена':
        # Если ввел "Отмена", отменяем операцию
        await message.answer(f'отменяю', reply_markup=kba.main_admin)
        # Отправляем сообщение об отмене и предоставляем кнопки основного меню администратора
        await state.finish()
        # Завершаем состояние
    else:
        await message.answer(f'описание')
        await NewOrder.next()
        # Переходим к следующему состоянию FSM для ожидания следующего шага добавления элемента


# @dp.message_handler(state=NewOrder.desc)
async def add_item_desc(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['desc'] = message.text
        # Сохраняем введенное пользователем описание нового элемента в состоянии
    if data['desc'] == 'Отмена':
        # Если пользователь ввел "Отмена", отменяем операцию
        await message.answer(f'отменяю', reply_markup=kba.main_admin)
        await state.finish()
    else:
        await message.answer(f'цена')
        # Отправляем сообщение с запросом на ввод цены элемента
        await NewOrder.next()


# @dp.message_handler(state=NewOrder.price)
async def add_item_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['price'] = message.text
    if data['price'] == 'Отмена':
        await message.answer(f'отменяю', reply_markup=kba.main_admin)
        await state.finish()
    else:
        await message.answer(f'Фото:', reply_markup=kba.cancel)
        await NewOrder.next()


# @dp.message_handler(content_types=['photo'], state=NewOrder.photo)
async def add_item_photo(message: types.Message, state: FSMContext):
    # Обработчик добавления фотографии нового элемента
    async with state.proxy() as data:
        data['photo'] = message.photo[-1].file_id
        # Сохраняем идентификатор файла фотографии
    mm = await db.add_item(state)
    # Добавляем элемент в базу данных, используя сохраненные данные
    await message.answer(f'запомните id {mm[0]} для удаления товара {mm[1]}')
    # Отправляем сообщение с id элемента и его названием для дальнейшего управления
    await message.answer(f'создано', reply_markup=kba.admin_panel)
    # Отправляем сообщение об успешном создании элемента и предоставляем кнопки панели администратора
    await state.finish()


# @dp.message_handler(text='Удалить товар')
async def del_item_vision(message: types.Message):  # удаляю товар из бд для всех
    if str(message.from_user.id) == os.getenv('ADMIN_ID'):
        await message.answer('Введите id: ', reply_markup=kba.cancel)
        await Del_item.id.set()  # состояние для получения id
    else:
        await message.answer(f'Не понимаю вас, {message.from_user.first_name}', kb.main)


# @dp.message_handler(state=Del_item.id)
async def choose_item_del(message: types.Message, state: FSMContext):  # получаю что удалить и выполняю запрос в бд
    async with state.proxy() as data:
        data['id'] = message.text
    if data['id'] == 'Отмена':
        await message.answer(f'отменяю', reply_markup=kba.main_admin)
    else:
        await db.del_item(state)
        await message.answer('удаление завершено', reply_markup=kba.main_admin)
    await state.finish()


# @dp.message_handler(text='Сделать рассылку')
async def ras_items(message: types.Message):  # получаю сообщение о необходимости рассылки
    if str(message.from_user.id) == os.getenv('ADMIN_ID'):
        await message.answer('введите текст рассылки', reply_markup=kba.cancel)
        await Rass.txet.set()
    else:
        await message.answer(f'Не понимаю вас, {message.from_user.first_name}', kb.main)


# @dp.message_handler(state=Rass.txet)
async def send_text_rass(message: types.Message, state: FSMContext):  # ловлю сооющение рассылки и рассылаю
    if message.text == 'Отмена':
        await message.answer(f'отменяю', reply_markup=kba.main_admin)
    else:
        mas = await db.ras_items()
        soob = 'Рассылка: ' + message.text
        print('lenmas', len(mas), 'mas:', mas)
        for i in range(len(mas)):
            print('i', mas[i])
            await bot.send_message(mas[i][0], soob)
        await message.answer('end', reply_markup=kba.main_admin)
    await state.finish()


async def user_exp(message: types.Message):  # кнопка взаимодействия с пользователем
    if str(message.from_user.id) == os.getenv('ADMIN_ID'):
        await message.answer('Начнем помогать пользователю!', reply_markup=kba.admin_user_exp)
    else:
        await message.answer(f'Не понимаю вас, {message.from_user.first_name}', kb.main)


async def corzina_uzvera_tg(message: types.Message):  # вывожу корзину пользователя
    if str(message.from_user.id) == os.getenv('ADMIN_ID'):
        await message.answer('tg_name: ', reply_markup=kba.cancel)
        await Smotrim_corzinu.zhdem_tg_name.set()
    else:
        await message.answer(f'Не понимаю вас, {message.from_user.first_name}', kb.main)


async def uzvera_tg(message: types.Message, state: FSMContext):  # получаю чью корзину вывести и вывожу
    async with state.proxy() as data:
        data['name'] = message.text
        print(data['name'])
        data['id'] = await db.get_id_from_name(data['name'][1:])
    if data['name'] == 'Отмена':
        await message.answer(f'отменяю', reply_markup=kba.main_admin)
    else:
        if data['id'] == 0:
            await message.answer('Нет такого', reply_markup=kba.main_admin)
        else:
            await bot.send_message(os.getenv('ADMIN_ID'), f"Корзина пользователя {data['name']}")
            ot = await db.korz_show(data['id'])
            print('ot', ot)
            if ot == 0:
                await message.answer('Пусто', reply_markup=kba.main_admin)
            else:
                for i in range(len(ot)):
                    await bot.send_photo(message.from_user.id, ot[i][4])
                    await message.answer(f"номер слота: {ot[i][0]},\n {ot[i][1]},\n {ot[i][2]},"f"\n {ot[i][3]}",
                                         reply_markup=kba.main_admin)
    await state.finish()


async def name_usvera(message: types.Message):  # полчаю тг юзера для удаления из его корзины
    if str(message.from_user.id) == os.getenv('ADMIN_ID'):
        await message.answer('tg_name: ', reply_markup=kba.cancel)
        await Del_usvera_admin.name.set()


async def del_tovar_usera(message: types.Message, state: FSMContext):  # почти то же самое что и у client, смотрите там
    if str(message.from_user.id) == os.getenv('ADMIN_ID'):
        async with state.proxy() as data:
            x = message.text
            data['name'] = x[1:]
        if x == 'Отмена':
            await message.answer(f'отменяю', reply_markup=kba.main_admin)
            await state.finish()
        else:
            await message.answer("Выберите действие:", reply_markup=kb.deleting_elements)
            await Del_usvera_admin.delall.set()


async def del_all_admin(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['id'] = await db.get_id_from_name(data['name'])
        data['text'] = message.text
    if data['text'] == 'Отмена':
        await message.answer(f'отменяю', reply_markup=kba.main_admin)
        await state.finish()
    elif data['id'] == 0:
        await message.answer('Нет такого', reply_markup=kba.main_admin)
        await state.finish()
    elif data['text'] != 'Удалить все':
        await message.answer(f'Введите номер лота, который хотите удалить')
        await Del_usvera_admin.next()
    else:
        await db.del_all(state)
        await message.answer(f'Пусто', reply_markup=kba.main_admin)
        await state.finish()


async def del_this_all_first_admin(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['num'] = message.text
    if data['text'] != 'Удалить все лоты номера':
        back = await db.del_this_first(state)
        if back == 0:
            await message.answer(f'Нечего удалять', reply_markup=kba.main_admin)
        else:
            await message.answer(f'Удалено', reply_markup=kba.main_admin)
    else:
        back = await db.del_this_all(state)
        if back == 0:
            await message.answer(f'Нечего удалять', reply_markup=kba.main_admin)
        else:
            await message.answer(f'Удалено', reply_markup=kba.main_admin)
    await state.finish()


# @dp.message_handler(state='*', text='Отмена')
async def cmd_cancel(message: types.Message, state: FSMContext):  # отлавливатель отмен
    if str(message.from_user.id) == os.getenv('ADMIN_ID'):
        cur_st = await state.get_state()
        await message.answer(f'отменяю', reply_markup=kba.main_admin)
        if cur_st is None:
            return
        await state.finish()
    else:
        cur_st = await state.get_state()
        await message.answer(f'отменяю', reply_markup=kb.main)
        if cur_st is None:
            return
        await state.finish()


# @dp.message_handler()
async def answer(message: types.Message):  # в самом конце, чтобы не словил не того, в Punkyfunky тоже в конце
    await message.reply(f'Не понимаю вас, {message.from_user.first_name}')


def register_handler_admin(dp: Dispatcher):
    dp.register_message_handler(cmd_cancel, state='*', commands='Отмена')
    dp.register_message_handler(cmd_cancel, Text(equals='Отмена', ignore_case=True), state='*')  # мб equals=
    dp.register_message_handler(cmd_admin_panel, text='Админ-панель')
    dp.register_message_handler(cmd_add_item, text='Добавить товар')
    dp.register_message_handler(user_exp, text='Взаимодействие с пользователем')
    dp.register_message_handler(corzina_uzvera_tg, text='Корзина по user tg')
    dp.register_message_handler(uzvera_tg, state=Smotrim_corzinu.zhdem_tg_name)
    dp.register_message_handler(name_usvera, text='Удалить товар юзера')
    dp.register_message_handler(del_tovar_usera, state=Del_usvera_admin.name)
    dp.register_message_handler(del_all_admin, state=Del_usvera_admin.delall)
    dp.register_message_handler(del_this_all_first_admin, state=Del_usvera_admin.delthisall_first)
    dp.register_callback_query_handler(add_item_type, state=NewOrder.type)
    dp.register_message_handler(add_item_name, state=NewOrder.name)
    dp.register_message_handler(add_item_desc, state=NewOrder.desc)
    dp.register_message_handler(add_item_price, state=NewOrder.price)
    dp.register_message_handler(add_item_photo, content_types=['photo'], state=NewOrder.photo)
    dp.register_message_handler(del_item_vision, text='Удалить товар')
    dp.register_message_handler(choose_item_del, state=Del_item.id)
    dp.register_message_handler(ras_items, text='Сделать рассылку')
    dp.register_message_handler(send_text_rass, state=Rass.txet)

    dp.register_message_handler(answer)
