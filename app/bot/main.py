#
#                    _)
#   __ `__ \    _` |  |  __ \      __ \   |   |
#   |   |   |  (   |  |  |   |     |   |  |   |
#  _|  _|  _| \__,_| _| _|  _| _)  .__/  \__, |
#                                 _|     ____/
#

# Configure script before using Django ORM
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# sys.path.insert(0, BASE_DIR)
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Giraffe.settings')
#
# import django
# django.setup()

from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
import asyncio

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

API_KEY = ''
bot = Bot(token=API_KEY, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher(storage=MemoryStorage())

commands_list = (
    ('/start', 'Start'),
)

commands = [types.BotCommand(*com) for com in commands_list]


def setup_bot_commands():
    loop.run_until_complete(bot.set_my_commands(commands))


@dp.message(CommandStart())
async def start_cmd_handler(message: types.Message):
    await message.reply('Welcome to IPDD!')


def bot_send_message(chat_id, message):
    loop.run_until_complete(bot.send_message(chat_id, message, ParseMode.MARKDOWN))


async def main() -> None:
    setup_bot_commands()
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
