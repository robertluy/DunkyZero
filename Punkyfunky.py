from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import keyboards as kb
import DatabaseDP as db
import os

load_dotenv()
storage = MemoryStorage()
bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher(bot=bot, storage=storage)


class NewOrder(StatesGroup):
    type = State()
    name = State()
    desc = State()
    price = State()
    photo = State()


class Rass(StatesGroup):
    txet = State()


class Del_item(StatesGroup):
    id = State()


class Catal_usveru(StatesGroup):
    shirt = State()
    sneakers = State()
    others = State()
    corz = State()


async def on_startup(_):
    await db.start_db()
    print('запуск прошел')


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer_sticker('CAACAgIAAxkBAAMZZLD7LJq2aaGAHn-OgkVQKDkM9LgAAk0DAAJSOrAFWJ0Eu-ZdkqUvBA')
    await db.cmd_start_db(message.from_user.id)
    if str(message.from_user.id) == os.getenv('ADMIN_ID'):
        await message.answer(f'Вы админ', reply_markup=kb.main_admin)
    else:
        await message.answer(f'Здравствуйте, {message.from_user.first_name}', reply_markup=kb.main)


@dp.message_handler(text='Корзина')
async def cmd_cot(message: types.Message):
    ot = await db.korz_show(message.from_user.id)
    for i in range(len(ot)):
        await bot.send_photo(message.from_user.id, ot[i][4])
        await bot.send_message(message.from_user.id,
                               text=f"номер слота: {ot[i][0]},\n {ot[i][1]},\n {ot[i][2]},"
                                    f"\n {ot[i][3]}")
    if str(message.from_user.id) == os.getenv('ADMIN_ID'):
        await message.answer('ваш заказ', reply_markup=kb.main_admin)
    else:
        await message.answer('ваш заказ', reply_markup=kb.main)


@dp.message_handler(text='Контакты')
async def cmd_contacts(message: types.Message):
    await message.answer(f'@TovarischComrade')


@dp.message_handler(text='Каталог')
async def cmd_catalog(message: types.Message):
    await message.answer(f'Пожалуйста:', reply_markup=kb.catalog_list)


@dp.callback_query_handler()
async def callback_quary_keyboard(callback_query: types.CallbackQuery):
    if callback_query.data == 't-shirt':
        await Catal_usveru.shirt.set()
        sh = await db.get_shirts()
        for i in range(len(sh)):
            await bot.send_photo(callback_query.from_user.id, sh[i][4])
            await bot.send_message(callback_query.from_user.id,
                                   text=f"номер слота: {sh[i][0]},\n {sh[i][1]},\n {sh[i][2]},"
                                        f"\n {sh[i][3]}")
        await Catal_usveru.corz.set()
        await bot.send_message(callback_query.from_user.id, 'введите номер, понравившегося лота',
                               reply_markup=kb.cancel)
    elif callback_query.data == 'sneakers':
        await Catal_usveru.sneakers.set()
        sn = await db.get_sneakers()
        for i in range(len(sn)):
            await bot.send_photo(callback_query.from_user.id, sn[i][4])
            await bot.send_message(callback_query.from_user.id,
                                   text=f"номер слота: {sn[i][0]},\n {sn[i][1]},\n {sn[i][2]},"
                                        f"\n {sn[i][3]}")
        await Catal_usveru.corz.set()
        await bot.send_message(callback_query.from_user.id, 'введите номер, понравившегося лота',
                               reply_markup=kb.cancel)
    elif callback_query.data == 'others':
        await Catal_usveru.others.set()
        ot = await db.get_others()
        for i in range(len(ot)):
            await bot.send_photo(callback_query.from_user.id, ot[i][4])
            await bot.send_message(callback_query.from_user.id,
                                   text=f"номер слота: {ot[i][0]},\n {ot[i][1]},\n {ot[i][2]},"
                                        f"\n {ot[i][3]}")
        await Catal_usveru.corz.set()
        await bot.send_message(callback_query.from_user.id, 'введите номер, понравившегося лота',
                               reply_markup=kb.cancel)


@dp.message_handler(state=Catal_usveru.corz)
async def corzina_pokupaski(message: types.Message, state: FSMContext):
    us_id = message.from_user.id
    ot = await db.el_choose(us_id, message.text)
    print(ot)
    for i in range(len(ot)):
        await bot.send_photo(us_id, ot[i][4])
        await bot.send_message(message.from_user.id,
                               text=f"номер слота: {ot[i][0]},\n {ot[i][1]},\n {ot[i][2]},"
                                    f"\n {ot[i][3]}")
    await state.finish()
    if str(message.from_user.id) == os.getenv('ADMIN_ID'):
        await message.answer('добавлено', reply_markup=kb.main_admin)
    else:
        await message.answer('добавлено', reply_markup=kb.main)
        await bot.send_message(os.getenv('ADMIN_ID'), f"пользователь @{us_id} добавил следующий товар:")
        await bot.send_photo(os.getenv('ADMIN_ID'), ot[0][4])
        await bot.send_message(os.getenv('ADMIN_ID'),
                               text=f"номер слота: {ot[i][0]},\n {ot[i][1]},\n {ot[i][2]},"
                                    f"\n {ot[i][3]}")


@dp.message_handler(text='Админ-панель')
async def cmd_admin_panel(message: types.Message):
    if str(message.from_user.id) == os.getenv('ADMIN_ID'):
        await message.answer(f'Вы вошли в админ-панель', reply_markup=kb.admin_panel)
    else:
        await message.answer(f'Не понимаю вас, {message.from_user.first_name}')


@dp.message_handler(text='Добавить товар')
async def cmd_add_item(message: types.Message):
    if str(message.from_user.id) == os.getenv('ADMIN_ID'):
        await NewOrder.type.set()
        await message.answer('Начнем добавлять', reply_markup=kb.catalog_list)
    else:
        await message.answer(f'Не понимаю вас, {message.from_user.first_name}')


@dp.message_handler(text='Отмена', state='*')
async def cmd_cancel(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    if str(message.from_user.id) == os.getenv('ADMIN_ID'):
        await state.reset_data()
        await message.answer(f'отменяю', reply_markup=kb.main_admin)
        await state.finish()
    else:
        await message.answer(f'отменяю', reply_markup=kb.catalog_list)


@dp.callback_query_handler(state=NewOrder.type)
async def add_item_type(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['type'] = call.data
    await call.message.answer(f'название товара', reply_markup=kb.cancel)
    await NewOrder.next()


@dp.message_handler(state=NewOrder.name)
async def add_item_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await message.answer(f'описание', reply_markup=kb.cancel)
    await NewOrder.next()


@dp.message_handler(state=NewOrder.desc)
async def add_item_desc(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['desc'] = message.text
    await message.answer(f'цена', reply_markup=kb.cancel)
    await NewOrder.next()


@dp.message_handler(state=NewOrder.price)
async def add_item_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['price'] = message.text
    await message.answer(f'Фото:', reply_markup=kb.cancel)
    await NewOrder.next()


@dp.message_handler(content_types=['photo'], state=NewOrder.photo)
async def add_item_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['photo'] = message.photo[-1].file_id
    mm = await db.add_item(state)
    await message.answer(f'запомните id {mm[0]} для удаления товара {mm[1]}')
    await message.answer(f'создано', reply_markup=kb.admin_panel)
    await state.finish()


@dp.message_handler(content_types=['sticker'])
async def check_sticker(message: types.Message):
    await message.answer(message.sticker.file_id)


@dp.message_handler(content_types=['photo', 'document'])
async def forward_message(message: types.Message):
    await bot.forward_message(os.getenv('GROUP_ID'), message.from_user.id, message.message_id)
    await message.answer('ожидайте')


@dp.message_handler(text='Удалить товар')
async def del_item_vision(message: types.Message):
    if str(message.from_user.id) == os.getenv('ADMIN_ID'):
        await Del_item.id.set()
        await message.answer('Введите id: ', reply_markup=kb.cancel)
    else:
        await message.answer(f'Не понимаю вас, {message.from_user.first_name}')


@dp.message_handler(state=Del_item.id)
async def choose_item_del(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['id'] = message.text
    await db.del_item(state)
    await message.answer('удаление завершено', reply_markup=kb.main_admin)
    await state.finish()


@dp.message_handler(text='Сделать рассылку')
async def ras_items(message: types.Message):
    if str(message.from_user.id) == os.getenv('ADMIN_ID'):
        await message.answer('введите текст рассылки', reply_markup=kb.cancel)
        await Rass.txet.set()
    else:
        await message.answer(f'Не понимаю вас, {message.from_user.first_name}')


@dp.message_handler(state=Rass.txet)
async def send_text_rass(message: types.Message, state: FSMContext):
    mas = await db.ras_items()
    soob = message.text
    for i in range(len(mas)):
        await bot.send_message(int(str(mas[i])[1:-2]), soob)
    await message.answer('end', reply_markup=kb.main_admin)
    await state.finish()


@dp.message_handler()
async def answer(message: types.Message):
    await message.reply(f'Не понимаю вас, {message.from_user.first_name}')


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
