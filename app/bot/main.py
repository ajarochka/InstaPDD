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
from django.db.models import Count

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'IPDD.settings')

import django

django.setup()

from django.contrib.auth import get_user_model

UserModel = get_user_model()

from aiogram.types import ReplyKeyboardRemove, Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from apps.category.models import Violator, Category
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import StatesGroup, State
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async
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
    address = State()
    description = State()


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


@dp.callback_query(F.data.casefold() == 'cancel')
async def cancel_cb_handler(query: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    msg = 'Cancelling state %r' % current_state
    await query.answer('Canceled.')
    await bot.delete_message(query.from_user.id, query.message.message_id)
    await bot.send_message(query.from_user.id, msg, reply_markup=ReplyKeyboardRemove())


@dp.message(Command('new_post'))
async def new_post_step_one(message: Message, state: FSMContext) -> None:
    violator_inline_builder = InlineKeyboardBuilder()
    violator_inline_builder.adjust(3)
    async for obj in Violator.objects.annotate(count=Count('categories')).filter(count__gt=0):
        violator_inline_builder.button(text=obj.name, callback_data=f'violator:{obj.id}')
    violator_inline_builder.row(InlineKeyboardButton(text='Cancel', callback_data='cancel'))
    current_state = await state.get_state()
    if current_state:
        await state.clear()
    await state.set_state(PostForm.violator_id)
    await message.answer('Please choose the violator:', reply_markup=violator_inline_builder.as_markup())


@dp.callback_query(F.data.casefold().startswith('violator:'), PostForm.violator_id)
async def violator_cb_handler(query: CallbackQuery, state: FSMContext):
    data = try_parse_query_data(query.data)
    category_inline_builder = InlineKeyboardBuilder()
    category_inline_builder.adjust(3)
    async for obj in Category.objects.filter(violator_id=data):
        category_inline_builder.button(text=obj.name, callback_data=f'category:{obj.id}')
    category_inline_builder.row(InlineKeyboardButton(text='Cancel', callback_data='cancel'))
    await state.set_state(PostForm.category_id)
    await bot.edit_message_text('Please select category:', query.from_user.id, query.message.message_id)
    await bot.edit_message_reply_markup(
        query.from_user.id, query.message.message_id,
        reply_markup=category_inline_builder.as_markup()
    )
    await query.answer('Violator selected.')


@dp.callback_query(F.data.casefold().startswith('category:'), PostForm.category_id)
async def category_cb_handler(query: CallbackQuery, state: FSMContext):
    data = try_parse_query_data(query.data)
    await state.update_data(category_id=data)
    await state.set_state(PostForm.address)
    await query.answer('category selected.')
    await bot.edit_message_text('Please enter the address:', query.from_user.id, query.message.message_id)


@dp.message(PostForm.address)
async def new_post_step_two(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await state.set_state(PostForm.description)
    await bot.send_message(message.from_user.id, 'Please enter the description:')


@dp.message(PostForm.description)
async def new_post_step_two(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    data = await state.get_data()
    # TODO: improve code quality, user sync_to_async fr filter.
    user = None
    async for obj in UserModel.objects.filter(username__iexact='telegram'):
        user = obj
    await sync_to_async(Post.objects.create)(user=user, **data)
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
