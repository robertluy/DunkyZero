from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

main = ReplyKeyboardMarkup(resize_keyboard=True)  # ресайз под устройство
main.add('Каталог').add('Корзина').add('Удалить из корзины').add('Уведомить о заполнении корзины')

deleting_elements = ReplyKeyboardMarkup(resize_keyboard=True)  # ресайз под устройство
deleting_elements.add('Удалить все').add('Удалить все лоты номера').add('Удалить первый лот номера').add('Отмена')

catalog_list = InlineKeyboardMarkup(row_width=2)  # инлайн клавиатура, 2 столбца
catalog_list.add(InlineKeyboardButton(text='Футболки', callback_data='t-shirt'),
                 InlineKeyboardMarkup(text='Кроссовки', callback_data='sneakers'),
                 InlineKeyboardMarkup(text='Другое', callback_data='others'))

cancel = ReplyKeyboardMarkup(resize_keyboard=True)  # ресайз под устройство
cancel.add('Отмена')

# клавиатуры клиента
