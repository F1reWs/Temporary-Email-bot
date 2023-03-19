import logging
import json
import asyncio
import sqlite3
import time

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from config import API_TOKEN, admin
import keyboard as kb
from onesec_api import Mailbox
import os

class Form(StatesGroup):
    peremennaya = State()

storage = MemoryStorage()
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)


connection = sqlite3.connect('data.db')
q = connection.cursor()

q.execute('CREATE TABLE IF NOT EXISTS users (user_id integer)')
connection.commit()

class sender(StatesGroup):
    text = State()


@dp.message_handler(content_types=['text'], text='✉️ Получить почту')
async def takeamail(m: types.Message):
    q.execute(f"SELECT * FROM users WHERE user_id = {m.chat.id}")
    result = q.fetchall()
    if len(result) == 0:
        uid = 'user_id'
        sql = 'INSERT INTO users ({}) VALUES ({})'.format(uid, m.chat.id)
        q.execute(sql)
        connection.commit()
    print(f"@{m.from_user.username} [{m.from_user.id}] {m.from_user.full_name}")    
    ma = Mailbox('')
    email = f'{ma._mailbox_}@1secmail.com'
    await m.answer(
        '📫 Вот твоя почта: {}\nОтправляй письмо.\n'
        'Почта проверяется автоматически, каждые 5 секунд, если придет новое письмо, мы вас об этом оповестим!\n\n'
        '<b>Работоспособность почты - 10 минут!</b>'.format(email), parse_mode='HTML')
    timeout = 600
    timer = {}
    timeout_start = time.time()
    while time.time() < timeout_start + timeout:
        test = 0
        if test == 5:
            break
        test -= 1
        mb = ma.filtred_mail()
        if mb != 'not found':
            for i in mb:
                if i not in timer:
                    timer[i] = i
                    if isinstance(mb, list):
                        mf = ma.mailjobs('read', mb[0])
                        js = mf.json()
                        fromm = js['from']
                        theme = js['subject']
                        mes = js['textBody']
                        await m.answer(f'📩 Новое письмо:\n<b>От</b>: {fromm}\n<b>Тема</b>: {theme}\n<b>Сообщение</b>: {mes}', reply_markup=kb.menu, parse_mode='HTML')
                        print(f'📩 Новое письмо:\n<b>От</b>: {fromm}\n<b>Тема</b>: {theme}\n<b>Сообщение</b>: {mes}')
                        continue
        await asyncio.sleep(5)

@dp.message_handler(commands=['admin'])
async def adminstration(m: types.Message):
    if m.chat.id == admin:
        await m.answer('Добро пожаловать в админ панель.', reply_markup=kb.apanel)


@dp.message_handler(commands=['start'])
async def texthandler(m: types.Message):
    q.execute(f"SELECT * FROM users WHERE user_id = {m.chat.id}")
    result = q.fetchall()
    if len(result) == 0:
        uid = 'user_id'
        sql = 'INSERT INTO users ({}) VALUES ({})'.format(uid, m.chat.id)
        q.execute(sql)
        connection.commit()
    await m.reply(f'Приветствую тебя, {m.from_user.mention}\nЭтот бот создан для быстрого получения временной почты.\nИспользуй кнопки ниже 👇', reply_markup=kb.menu)


@dp.callback_query_handler(text='stats')
async def statistics(call):
    row = q.execute('SELECT * FROM users').fetchall()
    lenght = len(row)
    await call.message.answer('Всего пользователей: {}'.format(lenght))


@dp.callback_query_handler(text='rass')
async def usender(call):
    await call.message.answer('Введите текст для рассылки.\n\nДля отмены нажмите кнопку ниже 👇', reply_markup=kb.back)
    await sender.text.set()


@dp.message_handler(state=sender.text)
async def process_name(message: types.Message, state: FSMContext):
    info = q.execute('SELECT user_id FROM users').fetchall()
    if message.text == 'Отмена':
        await message.answer('Отмена! Возвращаю в главное меню.', reply_markup=kb.menu)
        await state.finish()
    else:
        await message.answer('Начинаю рассылку...', reply_markup=kb.menu)
        for i in range(len(info)):
            try:
                await bot.send_message(info[i][0], str(message.text))
            except:
                pass
        await message.answer('Рассылка завершена.')
        await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)