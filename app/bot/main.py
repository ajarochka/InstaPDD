#
#                    _)
#   __ `__ \    _` |  |  __ \      __ \   |   |
#   |   |   |  (   |  |  |   |     |   |  |   |
#  _|  _|  _| \__,_| _| _|  _| _)  .__/  \__, |
#                                 _|     ____/
#

import sys
import os

# Configure script before using Django ORM
from asgiref.sync import sync_to_async

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'IPDD.settings')

import django

django.setup()

from aiogram.types import ReplyKeyboardRemove, Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from apps.category.models import Violator, Category
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import StatesGroup, State
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from apps.post.models import Post
import asyncio

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

BOT_TOKEN = '6914435384:AAEcg8rXUMelyzEsglTidsakLvl_fC-uHNc'
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher(storage=MemoryStorage())

commands_list = (
    ('/start', 'Start'),
    ('/new_post', 'Create new post'),
    ('/cancel', 'Cancel'),
)

commands = [types.BotCommand(command=com[0], description=com[1]) for com in commands_list]


class PostForm(StatesGroup):
    violator_id = State()
    category_id = State()
    description = State()


violator_inline_builder = InlineKeyboardBuilder()
violator_inline_builder.adjust(3)
for obj in Violator.objects.all():
    violator_inline_builder.button(text=obj.name, callback_data=f'violator:{obj.id}')


def try_parse_query_data(data: str):
    ret = data.split(':')[1].strip()
    return ret


@dp.message(CommandStart())
async def start_cmd_handler(message: types.Message):
    await message.reply('Welcome to IPDD!')


@dp.message(Command('cancel'))
@dp.message(F.text.casefold() == 'cancel')
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    msg = 'Cancelling state %r' % current_state
    await message.answer(msg, reply_markup=ReplyKeyboardRemove())


@dp.message(Command('new_post'))
async def new_post_step_one(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state:
        await state.clear()
    await state.set_state(PostForm.violator_id)
    await message.answer('Please choose the violator:', reply_markup=violator_inline_builder.as_markup())


@dp.callback_query(F.data.casefold().startswith('violator:'))
async def violator_cb_handler(query: CallbackQuery, state: FSMContext):
    data = try_parse_query_data(query.data)
    category_inline_builder = InlineKeyboardBuilder()
    category_inline_builder.adjust(3)
    async for obj in Category.objects.filter(violator_id=data):
        category_inline_builder.button(text=obj.name, callback_data=f'category:{obj.id}')
    await bot.edit_message_text('Please select category:', query.from_user.id, query.message.message_id)
    await bot.edit_message_reply_markup(
        query.from_user.id, query.message.message_id,
        reply_markup=category_inline_builder.as_markup()
    )
    await state.set_state(PostForm.category_id)
    await query.answer('Violator selected.')


@dp.callback_query(F.data.casefold().startswith('category:'))
async def category_cb_handler(query: CallbackQuery, state: FSMContext):
    await bot.edit_message_text('Please enter the description:', query.from_user.id, query.message.message_id)
    data = try_parse_query_data(query.data)
    await state.update_data(category_id=data)
    await state.set_state(PostForm.description)
    await query.answer('category selected.')


@dp.message(PostForm.description)
async def new_post_step_two(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    data = await state.get_data()
    await sync_to_async(Post.objects.create)(**data)
    await state.clear()
    msg = 'Thanks for your message, the request will be reviewed and we will return to you!'
    await message.answer(msg, reply_markup=ReplyKeyboardRemove())


async def bot_send_message(chat_id, message):
    await bot.send_message(chat_id, message, parse_mode=ParseMode.MARKDOWN)


async def main() -> None:
    await bot.set_my_commands(commands)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
