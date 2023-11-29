import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from dotenv import dotenv_values
from models import Client, Employee, TicketMessage, Ticket


logging.basicConfig(level=logging.INFO)

config = dotenv_values("../.env")
bot = Bot(token=config["TOKEN"])
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class Form(StatesGroup):
    waiting_for_text = State()
    waiting_for_status = State()
    waiting_for_employee = State()

status_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Открыт"),
            KeyboardButton(text="В работе"),
            KeyboardButton(text="Закрыт"),
        ]
    ],
    resize_keyboard=True
)

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer("Привет! Какую задачу вы хотите создать? Введите текст задачи.")
    await Form.waiting_for_text.set()


@dp.message_handler(state=Form.waiting_for_text)
async def process_text(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = message.text
    await message.answer("Выберите статус задачи:", reply_markup=status_keyboard)
    await Form.next()


@dp.message_handler(state=Form.waiting_for_status)
async def process_status(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['status'] = message.text
    await message.answer("Введите имя сотрудника, на которого назначить задачу.")
    await Form.next()


@dp.message_handler(state=Form.waiting_for_employee)
async def process_employee(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['employee'] = message.text
    data = await state.get_data()
    text = data['text']
    status = data['status']
    employee_name = data['employee']
    client, _ = await Client.get_or_create(telegram_id=message.from_user.id, defaults={'name': message.from_user.username})
    employee, _ = await Employee.get_or_create(username=employee_name, defaults={'password': 'password'})
    ticket = await Ticket.create(client=client, employee=employee, status=status)
    await TicketMessage.create(ticket=ticket, sender=message.from_user.username, message=text)
    await message.answer(f"Задача создана:\n{ticket}")

    await cmd_start(message)


if __name__ == '__main__':
    from aiogram import executor

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(executor.start_polling(dp, skip_updates=True))
    finally:
        loop.run_until_complete(bot.session.close())
        loop.close()


