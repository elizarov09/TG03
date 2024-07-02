import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message

# Укажите токен вашего бота
API_TOKEN = '7055051091:AAE8zmUdXdAqRUs9dRJZa4B1xZzRNp6Fkh4'

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


# Определение состояний
class Form(StatesGroup):
    name = State()
    age = State()
    grade = State()


# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await message.answer("Привет! Как тебя зовут?")
    await state.set_state(Form.name)


# Получение имени
@dp.message(Form.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Сколько тебе лет?")
    await state.set_state(Form.age)


# Получение возраста
@dp.message(Form.age)
async def process_age(message: Message, state: FSMContext):
    try:
        age = int(message.text)
        await state.update_data(age=age)
        await message.answer("В каком классе ты учишься?")
        await state.set_state(Form.grade)
    except ValueError:
        await message.answer("Пожалуйста, введи число.")


# Получение класса
@dp.message(Form.grade)
async def process_grade(message: Message, state: FSMContext):
    await state.update_data(grade=message.text)
    user_data = await state.get_data()

    await save_data(user_data)

    await message.answer("Спасибо! Твои данные сохранены.")
    await state.clear()


# Сохранение данных в базу данных
async def save_data(user_data):
    conn = sqlite3.connect('school_data.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO students (name, age, grade) VALUES (?, ?, ?)",
                   (user_data['name'], user_data['age'], user_data['grade']))
    conn.commit()
    conn.close()


# Запуск бота
async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
