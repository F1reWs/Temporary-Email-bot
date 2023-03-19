from aiogram import types



menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
menu.add(
	types.KeyboardButton('✉️ Получить почту')
)

apanel = types.InlineKeyboardMarkup(row_width=3)
apanel.add(
    types.InlineKeyboardButton(text='Статистика', callback_data='stats'),
	types.InlineKeyboardButton(text='Рассылка', callback_data='rass')
    )


back = types.ReplyKeyboardMarkup(resize_keyboard=True)
back.add(
    types.KeyboardButton('Отмена')
)