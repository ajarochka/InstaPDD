#
#                    _)
#   __ `__ \    _` |  |  __ \      __ \   |   |
#   |   |   |  (   |  |  |   |     |   |  |   |
#  _|  _|  _| \__,_| _| _|  _| _)  .__/  \__, |
#                                 _|     ____/
#

import sys
import io
import os

from aiogram.utils.formatting import Text, Bold

# Configure script before using Django ORM
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'IPDD.settings')

import django

django.setup()

from django.contrib.auth import get_user_model

UserModel = get_user_model()

from aiogram.types import ReplyKeyboardRemove, Message, CallbackQuery, InlineKeyboardButton, TelegramObject, PhotoSize
from aiogram import Bot, Dispatcher, types, F, BaseMiddleware
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from apps.category.models import Violator, Category
from typing import Callable, Dict, Any, Awaitable
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import StatesGroup, State
from apps.post.models import Post, PostImage
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async
from aiogram.enums import ParseMode
from django.core.files import File
from django.db.models import Count
import asyncio

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

BOT_TOKEN = '6914435384:AAEcg8rXUMelyzEsglTidsakLvl_fC-uHNc'
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher(storage=MemoryStorage())

commands_list = (
    ('/start', 'Start'),
    ('/help', 'Help'),
    ('/new_post', 'Create new post'),
    ('/my_posts', 'My posts'),
    ('/cancel', 'Cancel'),
)

commands = [types.BotCommand(command=com[0], description=com[1]) for com in commands_list]

HELP_MESSAGE = '''
Use /new_post command to create post
Follow the steps to fill the information
All fields are mandatory,
Please fill the information carefully.
'''

PAGE_SIZE = 3
YES = 'yes'
NO = 'no'

ask_inline_builder = InlineKeyboardBuilder()
ask_inline_builder.adjust(2)
ask_inline_builder.button(text='Yes', callback_data=f'callback:{YES}')
ask_inline_builder.button(text='No', callback_data=f'callback:{NO}')


class PostForm(StatesGroup):
    violator_id = State()
    category_id = State()
    photo = State()
    address = State()
    description = State()


class PostPageForm(StatesGroup):
    page = State()


def try_parse_query_data(data: str):
    try:
        ret = data.split(':')[1].strip()
        return ret
    except:
        return None


# This is a tricky middleware for processing the media group in one handler execution
class AlbumMiddleware(BaseMiddleware):
    """This middleware is for capturing media groups."""
    album_data: dict = {}

    def __init__(self, latency: int | float = 0.02):
        self.latency = latency
        super().__init__()

    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data: Dict[str, Any]) -> Any:
        if not event.media_group_id or not event.photo:
            return await handler(event, data)
        try:
            self.album_data[event.media_group_id].append(event.photo)
            return
        except KeyError:
            self.album_data[event.media_group_id] = [event.photo]
            await asyncio.sleep(self.latency)
            event.model_config["is_last"] = True
            data["album"] = self.album_data[event.media_group_id]
            await handler(event, data)
            if event.media_group_id and event.model_config.get("is_last"):
                del self.album_data[event.media_group_id]


@dp.message(CommandStart())
async def start_cmd_handler(message: types.Message, state: FSMContext):
    await state.clear()
    start_inline_builder = InlineKeyboardBuilder()
    start_inline_builder.adjust(2)
    start_inline_builder.button(text='Create new post', callback_data=f'start:post')
    start_inline_builder.button(text='Help!', callback_data=f'start:help')
    await message.reply('Welcome to IPDD!', reply_markup=start_inline_builder.as_markup())


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


@dp.message(Command('help'))
async def help_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(HELP_MESSAGE, reply_markup=ReplyKeyboardRemove())


@dp.callback_query(F.data.casefold() == 'start:help')
async def help_cb_handler(query: CallbackQuery, state: FSMContext):
    await state.clear()
    await query.answer('Help!')
    await bot.send_message(query.from_user.id, HELP_MESSAGE, reply_markup=ReplyKeyboardRemove())


@dp.message(Command('new_post'))
async def new_post_step_one(message: Message, state: FSMContext) -> None:
    await state.clear()
    violator_inline_builder = InlineKeyboardBuilder()
    violator_inline_builder.adjust(3)
    async for obj in Violator.objects.annotate(count=Count('categories')).filter(count__gt=0):
        violator_inline_builder.button(text=obj.name, callback_data=f'violator:{obj.id}')
    violator_inline_builder.row(InlineKeyboardButton(text='Cancel', callback_data='cancel'))
    await state.set_state(PostForm.violator_id)
    await message.answer('Please choose the violator:', reply_markup=violator_inline_builder.as_markup())


@dp.callback_query(F.data.casefold() == 'start:post')
async def new_post_step_one_cb(query: CallbackQuery, state: FSMContext):
    await state.clear()
    violator_inline_builder = InlineKeyboardBuilder()
    violator_inline_builder.adjust(3)
    async for obj in Violator.objects.annotate(count=Count('categories')).filter(count__gt=0):
        violator_inline_builder.button(text=obj.name, callback_data=f'violator:{obj.id}')
    violator_inline_builder.row(InlineKeyboardButton(text='Cancel', callback_data='cancel'))
    await state.set_state(PostForm.violator_id)
    await query.answer('New post.')
    await bot.send_message(
        query.from_user.id, 'Please choose the violator:',
        reply_markup=violator_inline_builder.as_markup()
    )


@dp.callback_query(F.data.casefold().startswith('violator:'), PostForm.violator_id)
async def new_post_step_two_cb(query: CallbackQuery, state: FSMContext):
    data = try_parse_query_data(query.data)
    if not data:
        return
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
async def new_post_step_three_cb(query: CallbackQuery, state: FSMContext):
    data = try_parse_query_data(query.data)
    if not data:
        return
    await state.update_data(category_id=data)
    await state.set_state(PostForm.photo)
    await query.answer('category selected.')
    await bot.edit_message_text('Please send the photo, max 3 allowed:', query.from_user.id, query.message.message_id)


@dp.message(PostForm.photo)
async def new_post_step_four(message: Message, state: FSMContext, album: list[PhotoSize] = None):
    photos = album or [message.photo]
    if not photos:
        await message.answer('Please send photos, max 3 allowed:')
        return
    photo_list = []
    for photo in photos[:3]:
        # Each photo has 4 resolutions, the last one has best quality.
        photo_list.append(photo[-1])
    await state.update_data(photo=photo_list)
    if len(photo_list) > 2:
        await state.set_state(PostForm.address)
        await bot.send_message(message.from_user.id, 'Please enter the address:')
        return
    await bot.send_message(message.from_user.id, 'Finish photo upload?', reply_markup=ask_inline_builder.as_markup())


@dp.callback_query(F.data.casefold().startswith('callback:'), PostForm.photo)
async def new_post_step_four_cb(query: CallbackQuery, state: FSMContext):
    if try_parse_query_data(query.data) == YES:
        await query.answer('Photo uploaded.')
        await state.set_state(PostForm.address)
        await bot.edit_message_text('Please enter the address:', query.from_user.id, query.message.message_id)
        return
    await bot.send_message(query.from_user.id, 'Please send more photo:')


@dp.message(PostForm.address)
async def new_post_step_five(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await state.set_state(PostForm.description)
    await bot.send_message(message.from_user.id, 'Please enter the description:')


@dp.message(PostForm.description)
async def new_post_step_six(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    data = await state.get_data()
    user, _ = await sync_to_async(UserModel.objects.get_or_create)(username=message.from_user.username)
    photos = data.pop('photo')
    post = await sync_to_async(Post.objects.create)(user=user, **data)
    for photo in photos:
        fp = io.BytesIO()
        await bot.download(photo.file_id, fp)
        await sync_to_async(PostImage.objects.create)(post=post, file=File(fp, photo.file_unique_id))
    await state.clear()
    msg = 'Thanks for your message, the request will be reviewed and we will return to you!'
    await message.answer(msg, reply_markup=ReplyKeyboardRemove())


@dp.message(Command('my_posts'))
async def my_posts(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(PostPageForm.page)
    user = None
    async for obj in UserModel.objects.filter(username=message.from_user.username):
        user = obj
    if not user:
        await message.answer('You do not posted anything yet.')
        return
    post_inline_builder = InlineKeyboardBuilder()
    queryset = await sync_to_async(Post.objects.filter)(user=user)
    count = await sync_to_async(queryset.count)()
    async for obj in queryset.order_by('-created_at')[:PAGE_SIZE]:
        ctg = await sync_to_async(Category.objects.get)(id=obj.category_id)
        txt = f'{ctg.name} | {obj.created_at.strftime("%d-%m-%Y %H:%M")} | {obj.get_status_display()}'
        post_inline_builder.row(InlineKeyboardButton(text=txt, callback_data=f'post:{obj.id}'))
    if count > PAGE_SIZE:
        post_inline_builder.row(InlineKeyboardButton(text='Next >', callback_data='posts_page:2'))
    await message.answer('Your posts:', reply_markup=post_inline_builder.as_markup())


@dp.callback_query(F.data.casefold().startswith('posts_page:'), PostPageForm.page)
async def posts_page_cb(query: CallbackQuery, state: FSMContext):
    user = None
    page = try_parse_query_data(query.data)
    async for obj in UserModel.objects.filter(username=query.from_user.username):
        user = obj
    if not user or not page or not page.isdigit():
        return await query.answer(f'Invalid page {page}')
    await query.answer(f'Posts page {page}')
    page = int(page)
    await state.update_data(page=page)
    post_inline_builder = InlineKeyboardBuilder()
    queryset = await sync_to_async(Post.objects.filter)(user=user)
    count = await sync_to_async(queryset.count)()
    async for obj in queryset.order_by('-created_at')[(page - 1) * PAGE_SIZE:page * PAGE_SIZE]:
        ctg = await sync_to_async(Category.objects.get)(id=obj.category_id)
        txt = f'{ctg.name} | {obj.created_at.strftime("%d-%m-%Y %H:%M")} | {obj.get_status_display()}'
        post_inline_builder.row(InlineKeyboardButton(text=txt, callback_data=f'post:{obj.id}'))
    prev_next_btn = []
    if page > 1:
        prev_next_btn.append(InlineKeyboardButton(text='< Prev', callback_data=f'posts_page:{page - 1}'))
    if count > page * PAGE_SIZE:
        prev_next_btn.append(InlineKeyboardButton(text='Next >', callback_data=f'posts_page:{page + 1}'))
    post_inline_builder.row(*prev_next_btn)
    await bot.edit_message_text(
        'Your posts:', query.from_user.id, query.message.message_id,
        reply_markup=post_inline_builder.as_markup()
    )


@dp.callback_query(F.data.casefold().startswith('post:'), PostPageForm.page)
async def post_info_cb(query: CallbackQuery, state: FSMContext):
    user = None
    post_id = try_parse_query_data(query.data)
    async for obj in UserModel.objects.filter(username=query.from_user.username):
        user = obj
    if not user or not post_id or not post_id.isdigit():
        return await query.answer(f'Invalid post id {post_id}')
    await query.answer('Post details')
    data = await state.get_data()
    page = data.get('page', 1)
    post_inline_builder = InlineKeyboardBuilder()
    post = await sync_to_async(Post.objects.get)(id=post_id)
    ctg = await sync_to_async(Category.objects.get)(id=post.category_id)
    txt = Text(
        Bold('Category'), ': ', ctg.name, '\n',
        Bold('Creation date'), ': ', post.created_at.strftime("%d-%m-%Y %H:%M"), '\n',
        Bold('Status'), ': ', post.get_status_display()
    )
    post_inline_builder.row(InlineKeyboardButton(text='< Back to list', callback_data=f'posts_page:{page}'))
    await bot.edit_message_text(
        txt.as_html(), query.from_user.id, query.message.message_id,
        reply_markup=post_inline_builder.as_markup()
    )


async def main() -> None:
    await bot.set_my_commands(commands)
    dp.message.middleware(AlbumMiddleware(0.04))
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
