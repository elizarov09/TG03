import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, Message

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
    await message.answer(
        "Привет! Я бот для сбора данных учеников. Используй команды:\n"
        "/start - начать работу\n"
        "/help - помощь и описание команд\n"
        "/my_data - показать мои данные\n"
        "/all_data - показать данные всех учеников\n"
        "Сейчас давай начнем с твоих данных. Как тебя зовут?"
    )
    await state.set_state(Form.name)


# Команда /help
@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "Я бот для сбора данных учеников. Вот доступные команды:\n"
        "/start - начать работу\n"
        "/help - помощь и описание команд\n"
        "/my_data - показать мои данные\n"
        "/all_data - показать данные всех учеников"
    )


# Команда /my_data
@dp.message(Command("my_data"))
async def my_data(message: Message, state: FSMContext):
    user_id = message.from_user.id
    conn = sqlite3.connect('school_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE id=?", (user_id,))
    data = cursor.fetchone()
    conn.close()

    if data:
        await message.answer(f"Твои данные:\nИмя: {data[1]}\nВозраст: {data[2]}\nКласс: {data[3]}")
    else:
        await message.answer("Ты еще не ввел свои данные. Используй /start чтобы начать.")


# Команда /all_data
@dp.message(Command("all_data"))
async def all_data(message: Message):
    conn = sqlite3.connect('school_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    all_students = cursor.fetchall()
    conn.close()

    if all_students:
        response = "Данные всех учеников:\n"
        for student in all_students:
            response += f"ID: {student[0]}, Имя: {student[1]}, Возраст: {student[2]}, Класс: {student[3]}\n"
        await message.answer(response)
    else:
        await message.answer("Нет данных учеников.")


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

    await save_data(user_data, message.from_user.id)

    await message.answer("Спасибо! Твои данные сохранены.")
    await state.clear()


# Сохранение данных в базу данных
async def save_data(user_data, user_id):
    conn = sqlite3.connect('school_data.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO students (id, name, age, grade) VALUES (?, ?, ?, ?)",
                   (user_id, user_data['name'], user_data['age'], user_data['grade']))
    conn.commit()
    conn.close()


# Установка команд в меню бота
async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Запустить бота"),
        BotCommand(command="/help", description="Помощь по использованию бота"),
        BotCommand(command="/my_data", description="Показать мои данные"),
        BotCommand(command="/all_data", description="Показать данные всех учеников"),
    ]
    await bot.set_my_commands(commands)


# Запуск бота
async def main():
    await set_commands(bot)
    await dp.start_polling(bot)


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
