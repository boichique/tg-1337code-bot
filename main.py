from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ContentType
from aiogram.utils import executor
import asyncio

import config
import queries
import funcs


bot = Bot(config.TOKEN_API)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=["help"])
async def print_help(message: types.Message):
    await message.answer("Доступные команды:\n\n" +
                         "/stat - вывод статистики за все время челленджа\n" +
                         "/today - вывод статистики по челленджу за сегодня\n" +
                         "/yesterday - вывод статистики по челленджу за вчера\n" +
                         "/week - вывод статистики по челленджу за неделю\n" +
                         "/daily - вывод сегодняшнего дейлика")


@dp.message_handler(commands=["stat"])
async def print_stat(message: types.Message):
    text = funcs.report_on_demand("все время", "За все время", queries.stat)
    await message.answer(text)


@dp.message_handler(commands=["today"])
async def print_today_stat(message: types.Message):
    text = funcs.report_on_demand("сегодня", "Сегодня", queries.today)
    await message.answer(text)


@dp.message_handler(commands=["yesterday"])
async def print_yesterday_stat(message: types.Message):
    text = funcs.report_on_demand("вчера", "Вчера", queries.yesterday)
    await message.answer(text)


@dp.message_handler(commands=["week"])
async def print_week_stat(message: types.Message):
    text = funcs.report_on_demand("эту неделю", "За эту неделю", queries.week)
    await message.answer(text)


@dp.message_handler(commands=["daily"])
async def send_dailyque(message: types.Message):
    text = funcs.get_daily_challenge()
    await message.answer(text, types.ParseMode.MARKDOWN)


@dp.message_handler(commands=["chatId"])                            # Команда для вывода id чата (id нужен для
async def print_chat_id(message: types.Message):                    # отправки сообщений по id)
    await message.answer(f"id этого чата - {message.chat.id}")


@dp.message_handler(content_types=[ContentType.PHOTO, ContentType.TEXT])
async def capture_challenge_report(message: types.Message):
    funcs.insert_report_into_table(message)
    # await message.answer("Запись о задаче была сохранена.")


async def schedule_messages():
    while True:
        text = funcs.get_daily_challenge()
        await bot.send_message(config.CHAT_ID, text, types.ParseMode.MARKDOWN)  # Ежедневная отправка дейликов по расписанию
        await asyncio.sleep(43200)
        message_id = await funcs.send_daily_stat()                              # Ежедневная отправка отчетов по расписанию и
        await bot.pin_chat_message(config.CHAT_ID, message_id)                  # пин отчета в чате
        await asyncio.sleep(43200)


async def shutdown():                                                           # Закрытие сессий бота
    await bot.session.close()
    await dp.storage.close()
    await dp.storage.wait_closed()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(schedule_messages())
    executor.start_polling(dp, skip_updates=True)
    loop.close()
