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

# Configure script before using Django ORM
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'IPDD.settings')

import django

django.setup()

from aiogram import Bot, Dispatcher, types, F, BaseMiddleware
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from apps.category.models import Violator, Category
from typing import Callable, Dict, Any, Awaitable
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.formatting import Text, Bold
from django.contrib.auth import get_user_model
from apps.post.models import Post, PostImage
from aiogram.fsm.context import FSMContext
from django.contrib.gis.geos import Point
from apps.post.choices import PostStatus
from asgiref.sync import sync_to_async
from aiogram.enums import ParseMode
from django.core.files import File
from django.db.models import Count
from enum import StrEnum
import asyncio
from aiogram.types import (
    InlineKeyboardButton,
    ReplyKeyboardRemove,
    TelegramObject,
    CallbackQuery,
    FSInputFile,
    PhotoSize,
    Message,
)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

BOT_TOKEN = '6914435384:AAEcg8rXUMelyzEsglTidsakLvl_fC-uHNc'
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher(storage=MemoryStorage())

UserModel = get_user_model()

commands_list = (
    ('/start', 'Start'),
    ('/help', 'Help'),
    ('/new_post', 'Create new post'),
    ('/my_posts', 'My posts'),
    ('/search', 'Search by license plate'),
    ('/cancel', 'Cancel'),
)

commands = [types.BotCommand(command=com[0], description=com[1]) for com in commands_list]

HELP_MESSAGE = '''
Use /new_post command to create post.
Follow the steps to fill the information.
All fields are mandatory.
Please fill the information carefully.
'''

PAGE_SIZE = 3
YES = 'yes'
NO = 'no'

UPDATE_FIELDS_LIST = (
    ('category_id', 'Category'),
    ('photo', 'Photo'),
    ('license_plate', 'License plate'),
    ('location', 'Location'),
    ('address', 'Address'),
    ('description', 'Description'),
)


class PostAction(StrEnum):
    UPDATE = 'update'
    DELETE = 'delete'


class PostCreateForm(StatesGroup):
    violator_id = State()
    category_id = State()
    location = State()
    photo = State()
    address = State()
    license_plate = State()
    description = State()


class PostUpdateForm(StatesGroup):
    post_id = State()
    location = State()
    photo = State()
    address = State()
    license_plate = State()
    description = State()


class PostPageForm(StatesGroup):
    page = State()


class PostSearchForm(StatesGroup):
    license_plate = State()


STATE_TEXT_MAP = {
    PostCreateForm.violator_id: 'New post violator',
    PostCreateForm.category_id: 'New post category',
    PostCreateForm.photo: 'New post step photo',
    PostCreateForm.location: 'New post step location',
    PostCreateForm.address: 'New post step address',
    PostCreateForm.license_plate: 'New post step license plate',
    PostCreateForm.description: 'New post step description',
    PostSearchForm.license_plate: 'Search',
    PostPageForm.page: 'Post list',
}


def try_parse_query_data(data: str):
    try:
        data = data.split(':')
        ret = {}
        for i in range(0, len(data), 2):
            ret[data[i]] = data[i + 1]
        return ret
    except:
        return None


# This is a tricky middleware for processing the media group in one handler execution.
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
    start_inline_builder.button(text='Create new post', callback_data=f'start:post')
    start_inline_builder.button(text='Help!', callback_data=f'start:help')
    start_inline_builder.adjust(2)
    await message.reply('Welcome to IPDD!', reply_markup=start_inline_builder.as_markup())


@dp.message(Command('cancel'))
@dp.message(F.text.casefold() == 'cancel')
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    msg = 'Cancelled state: %s' % STATE_TEXT_MAP[current_state]
    await message.answer(msg, reply_markup=ReplyKeyboardRemove())


@dp.callback_query(F.data.casefold() == 'cancel')
async def cancel_cb_handler(query: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    msg = 'Cancelled state: %s' % STATE_TEXT_MAP[current_state]
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


@dp.message(Command('search'))
async def search_handler(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(PostSearchForm.license_plate)
    await message.answer('Please enter some license plate number:', reply_markup=ReplyKeyboardRemove())


@dp.message(Command('new_post'))
async def new_post(message: Message, state: FSMContext) -> None:
    await state.clear()
    violator_inline_builder = InlineKeyboardBuilder()
    async for obj in Violator.objects.annotate(count=Count('categories')).filter(count__gt=0):
        violator_inline_builder.button(text=obj.name, callback_data=f'violator:{obj.id}')
    violator_inline_builder.adjust(2)
    await state.set_state(PostCreateForm.violator_id)
    await message.answer(
        'Please choose the violator:',
        reply_markup=violator_inline_builder.as_markup()
    )


@dp.callback_query(F.data.casefold() == 'start:post')
async def new_post_cb(query: CallbackQuery, state: FSMContext):
    await query.answer('New post.')
    return await new_post(query.message, state)


@dp.callback_query(F.data.casefold().startswith('violator:'), PostCreateForm.violator_id)
async def new_post_step_one_cb(query: CallbackQuery, state: FSMContext):
    data = try_parse_query_data(query.data)
    if not data:
        return
    await query.answer('Violator selected.')
    category_inline_builder = InlineKeyboardBuilder()
    async for obj in Category.objects.filter(violator_id=data.get('violator')):
        category_inline_builder.button(text=obj.name, callback_data=f'category:{obj.id}')
    category_inline_builder.adjust(2)
    await state.set_state(PostCreateForm.category_id)
    await bot.edit_message_text(
        'Please select category:', query.from_user.id,
        query.message.message_id, reply_markup=category_inline_builder.as_markup()
    )


@dp.callback_query(F.data.casefold().startswith('category:'), PostCreateForm.category_id)
async def new_post_step_two_cb(query: CallbackQuery, state: FSMContext):
    data = try_parse_query_data(query.data)
    if not data:
        return
    await state.update_data(category_id=data.get('category'))
    await query.answer('category selected.')
    await state.set_state(PostCreateForm.photo)
    await bot.edit_message_text(
        'Please send photos, max 3 allowed:', query.from_user.id, query.message.message_id
    )


@dp.message(PostCreateForm.photo)
async def new_post_step_three(message: Message, state: FSMContext, album: list[PhotoSize] = None):
    photos = album or [message.photo]
    if not photos:
        return await message.answer('Please send photos, max 3 allowed:')
    data = await state.get_data()
    photo_list = data.get('photo', [])
    ask_inline_builder = InlineKeyboardBuilder()
    ask_inline_builder.button(text='Yes', callback_data=f'finish:{YES}')
    ask_inline_builder.button(text='No', callback_data=f'finish:{NO}')
    if len(photo_list) < 3:
        for photo in photos[:3 - len(photo_list)]:
            # Each photo has 4 resolutions, the last one has the best quality.
            photo_list.append(photo[-1])
        await state.update_data(photo=photo_list)
    if len(photo_list) > 2:
        await state.set_state(PostCreateForm.location)
        ask_inline_builder = InlineKeyboardBuilder()
        ask_inline_builder.button(text='Skip this step', callback_data=f'finish:{YES}')
        await bot.send_message(
            message.from_user.id, 'Please send the location:', reply_markup=ask_inline_builder.as_markup()
        )
    else:
        await bot.send_message(
            message.from_user.id, 'Finish photo upload?',
            reply_markup=ask_inline_builder.as_markup()
        )


@dp.callback_query(F.data.casefold().startswith('finish:'), PostCreateForm.photo)
async def new_post_step_three_cb(query: CallbackQuery, state: FSMContext):
    data = try_parse_query_data(query.data)
    if not data:
        return
    if data.get('finish') == YES:
        await query.answer('Photo uploaded.')
        await state.set_state(PostCreateForm.location)
        ask_inline_builder = InlineKeyboardBuilder()
        ask_inline_builder.button(text='Skip this step', callback_data=f'finish:{YES}')
        return await bot.edit_message_text(
            'Please send the location:', query.from_user.id,
            query.message.message_id, reply_markup=ask_inline_builder.as_markup()
        )
    await bot.edit_message_text('Please send more photo:', query.from_user.id, query.message.message_id)


@dp.message(PostCreateForm.location)
async def new_post_step_four(message: Message, state: FSMContext):
    if not message.location:
        ask_inline_builder = InlineKeyboardBuilder()
        ask_inline_builder.button(text='Skip this step', callback_data=f'finish:{YES}')
        return await message.answer('Please send the location:', reply_markup=ask_inline_builder.as_markup())
    await state.update_data(location=message.location)
    await state.set_state(PostCreateForm.address)
    address_inline_builder = InlineKeyboardBuilder()
    address_inline_builder.button(text='Skip this step', callback_data=f'finish:{YES}')
    await message.answer('Please send the address:', reply_markup=address_inline_builder.as_markup())


@dp.callback_query(F.data.casefold().startswith('finish:'), PostCreateForm.location)
async def new_post_step_four_cb(query: CallbackQuery, state: FSMContext):
    data = try_parse_query_data(query.data)
    if not data:
        return
    if data.get('finish') == YES:
        await query.answer('Location skipped.')
        await state.set_state(PostCreateForm.address)
        return await bot.edit_message_text(
            'Please send the address:',
            query.from_user.id, query.message.message_id
        )
    # The following code is nlikely to be called.
    ask_inline_builder = InlineKeyboardBuilder()
    ask_inline_builder.button(text='Skip this step', callback_data=f'finish:{YES}')
    await bot.edit_message_text(
        'Please send the location:', query.from_user.id,
        query.message.message_id, reply_markup=ask_inline_builder.as_markup()
    )


@dp.message(PostCreateForm.address)
async def new_post_step_five(message: Message, state: FSMContext):
    ask_inline_builder = InlineKeyboardBuilder()
    ask_inline_builder.button(text='Skip this step', callback_data=f'finish:{YES}')
    await state.update_data(address=message.text)
    await state.set_state(PostCreateForm.license_plate)
    await bot.send_message(
        message.from_user.id, 'Please enter the license plate:',
        reply_markup=ask_inline_builder.as_markup()
    )


@dp.callback_query(F.data.casefold().startswith('finish:'), PostCreateForm.address)
async def new_post_step_five_cb(query: CallbackQuery, state: FSMContext):
    data = try_parse_query_data(query.data)
    if not data:
        return
    ask_inline_builder = InlineKeyboardBuilder()
    ask_inline_builder.button(text='Skip this step', callback_data=f'finish:{YES}')
    if data.get('finish') == YES:
        await query.answer('Address skipped.')
        await state.set_state(PostCreateForm.license_plate)
        return await bot.edit_message_text(
            'Please send the license plate:',
            query.from_user.id, query.message.message_id,
            reply_markup=ask_inline_builder.as_markup()
        )
    # The following code is nlikely to be called.
    await bot.edit_message_text(
        'Please send the address:', query.from_user.id,
        query.message.message_id, reply_markup=ask_inline_builder.as_markup()
    )


@dp.message(PostCreateForm.license_plate)
async def new_post_step_six(message: Message, state: FSMContext):
    await state.update_data(license_plate=message.text)
    await state.set_state(PostCreateForm.description)
    await bot.send_message(message.from_user.id, 'Please enter the description:')


@dp.callback_query(F.data.casefold().startswith('finish:'), PostCreateForm.license_plate)
async def new_post_step_six_cb(query: CallbackQuery, state: FSMContext):
    data = try_parse_query_data(query.data)
    if not data:
        return
    ask_inline_builder = InlineKeyboardBuilder()
    ask_inline_builder.button(text='Skip this step', callback_data=f'finish:{YES}')
    if data.get('finish') == YES:
        await query.answer('License plate skipped.')
        await state.set_state(PostCreateForm.license_plate)
        return await bot.edit_message_text(
            'Please send the description:',
            query.from_user.id, query.message.message_id,
            reply_markup=ask_inline_builder.as_markup()
        )
    # The following code is nlikely to be called.
    await bot.edit_message_text(
        'Please send the license plate:', query.from_user.id,
        query.message.message_id, reply_markup=ask_inline_builder.as_markup()
    )


@dp.message(PostCreateForm.description)
async def new_post_step_seven(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    data = await state.get_data()
    user, _ = await sync_to_async(UserModel.objects.get_or_create)(username=message.from_user.username)
    photos = data.pop('photo')
    location = data.pop('location', None)
    if location:
        data['location'] = Point(x=location.longitude, y=location.latitude)
    post = await sync_to_async(Post.objects.create)(user=user, **data)
    for photo in photos:
        fp = io.BytesIO()
        await bot.download(photo.file_id, fp)
        await sync_to_async(PostImage.objects.create)(
            post=post, file=File(fp, photo.file_unique_id), file_id=photo.file_id
        )
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
        post_inline_builder.row(
            InlineKeyboardButton(text='Next >', callback_data=f'posts_page:2:user:{user.id}'),
            InlineKeyboardButton(text='>>', callback_data=f'posts_page:{int(-(count // -PAGE_SIZE))}:user:{user.id}')
        )
    await message.answer('Your posts:', reply_markup=post_inline_builder.as_markup())


@dp.callback_query(F.data.casefold().startswith('posts_page:'), PostPageForm.page)
async def posts_page_cb(query: CallbackQuery, state: FSMContext):
    data = try_parse_query_data(query.data)
    if not data:
        return
    user_id = data.get('user')
    page = data.get('posts_page', '1')
    user = await sync_to_async(UserModel.objects.get)(id=user_id)
    if not user_id or not page or not page.isdigit():
        return await query.answer(f'Invalid page {page}.')
    await query.answer(f'Posts page {page}.')
    page = int(page)
    await state.update_data(page=page)
    post_inline_builder = InlineKeyboardBuilder()
    queryset = await sync_to_async(Post.objects.filter)(user=user)
    count = await sync_to_async(queryset.count)()
    async for obj in queryset.order_by('-created_at')[(page - 1) * PAGE_SIZE:page * PAGE_SIZE]:
        ctg = await sync_to_async(Category.objects.get)(id=obj.category_id)
        txt = f'{ctg.name} | {obj.created_at.strftime("%d-%m-%Y %H:%M")} | {obj.get_status_display()}'
        post_inline_builder.row(InlineKeyboardButton(text=txt, callback_data=f'post:{obj.id}:user:{user_id}'))
    prev_next_btn = []
    if page > 1:
        prev_next_btn.extend([
            InlineKeyboardButton(text='<<', callback_data=f'posts_page:1:user:{user_id}'),
            InlineKeyboardButton(text='< Prev', callback_data=f'posts_page:{page - 1}:user:{user_id}')
        ])
    if count > page * PAGE_SIZE:
        prev_next_btn.extend([
            InlineKeyboardButton(text='Next >', callback_data=f'posts_page:{page + 1}:user:{user_id}'),
            InlineKeyboardButton(text='>>', callback_data=f'posts_page:{int(-(count // -PAGE_SIZE))}:user:{user_id}')
        ])
    post_inline_builder.row(*prev_next_btn)
    await bot.delete_message(query.from_user.id, query.message.message_id)
    await bot.send_message(
        query.from_user.id, 'Your posts:',
        reply_markup=post_inline_builder.as_markup()
    )


@dp.callback_query(F.data.casefold().startswith('post:'), PostPageForm.page)
async def post_info_cb(query: CallbackQuery, state: FSMContext):
    data = try_parse_query_data(query.data)
    if not data:
        return
    post_id = data.get('post')
    photo_num = int(data.get('photo_num', 0))
    if not post_id or not post_id.isdigit():
        return await query.answer(f'Invalid post id {post_id}.')
    await query.answer('Post details.')
    state_data = await state.get_data()
    page = state_data.get('page', 1)
    post_inline_builder = InlineKeyboardBuilder()
    post = await sync_to_async(Post.objects.get)(id=post_id)
    ctg = await sync_to_async(Category.objects.get)(id=post.category_id)
    queryset = await sync_to_async(PostImage.objects.filter)(post_id=post_id)
    photo_count = await sync_to_async(queryset.count)()
    photo = None
    if photo_count > photo_num:
        photos = await sync_to_async(list)(queryset)
        photo = photos[photo_num]
    post_controls = []
    if post.status < PostStatus.REJECTED:
        post_controls.append(InlineKeyboardButton(
            text='Update post', callback_data=f'post_action:{PostAction.UPDATE}:post:{post_id}')
        )
    if post.status < PostStatus.APPROVED:
        post_controls.append(InlineKeyboardButton(
            text='Delete post', callback_data=f'post_action:{PostAction.DELETE}:post:{post_id}')
        )
    if photo_count > 1:
        num = (photo_num + 1) % photo_count
        post_controls.append(InlineKeyboardButton(
            text='Next photo >', callback_data=f'post:{post_id}:photo_num:{num}')
        )
    post_inline_builder.row(*post_controls)
    post_inline_builder.row(InlineKeyboardButton(
        text='< Back to list', callback_data=f'posts_page:{page}:user:{post.user_id}')
    )
    txt = Text(
        Bold('Category'), ': ', ctg.name, '\n',
        Bold('Creation date'), ': ', post.created_at.strftime("%d-%m-%Y %H:%M"), '\n',
        Bold('Status'), ': ', post.get_status_display(), '\n',
    )
    if post.license_plate:
        txt += Text(Bold('License plate'), ':', post.license_plate, '\n')
    if post.location:
        txt += Text(
            Bold('Location'), ':\n',
            '  Longitude: ', post.location.x, '\n',
            '  Latitude; ', post.location.y, '\n'
        )
    txt += Text(
        Bold('Address'), ': ', post.address, '\n',
        Bold('Description'), ': ', post.description
    )
    await bot.delete_message(query.from_user.id, query.message.message_id)
    # TODO: check if Telegram has the file for "file_id"
    if photo:
        media = photo.file_id if photo.file_id else FSInputFile(photo.file.path)
        msg = await bot.send_photo(
            query.from_user.id, media, caption=txt.as_html(),
            reply_markup=post_inline_builder.as_markup()
        )
        if not photo.file_id:
            photo.file_id = msg.photo[-1].file_id
            await sync_to_async(photo.save)()
    else:
        await bot.send_message(
            query.from_user.id, txt.as_html(),
            reply_markup=post_inline_builder.as_markup()
        )


@dp.callback_query(F.data.casefold().startswith(f'post:'))
async def back_to_post_cb(query: CallbackQuery, state: FSMContext):
    data = try_parse_query_data(query.data)
    page = data.get('page')
    await state.clear()
    await state.set_state(PostPageForm.page)
    await state.update_data(page=page)
    await post_info_cb(query, state)


@dp.message(PostSearchForm.license_plate)
async def search_license_plate(message: Message, state: FSMContext):
    license_plate = message.text
    await state.update_data(license_plate=license_plate)
    post_inline_builder = InlineKeyboardBuilder()
    queryset = await sync_to_async(Post.objects.filter)(license_plate__iexact=license_plate, status=PostStatus.APPROVED)
    count = await sync_to_async(queryset.count)()
    async for obj in queryset.order_by('-created_at')[:PAGE_SIZE]:
        ctg = await sync_to_async(Category.objects.get)(id=obj.category_id)
        txt = f'{ctg.name} | {obj.created_at.strftime("%d-%m-%Y %H:%M")}'
        post_inline_builder.row(InlineKeyboardButton(text=txt, callback_data=f'search_post_info:{obj.id}'))
    if count > 0:
        if count > PAGE_SIZE:
            post_inline_builder.row(
                InlineKeyboardButton(text='Next >', callback_data=f'search_page:2'),
                InlineKeyboardButton(text='>>', callback_data=f'search_page:{int(-(count // -PAGE_SIZE))}')
            )
        await message.answer('Found results:', reply_markup=post_inline_builder.as_markup())
    else:
        await state.clear()
        await message.answer('No matches found.')


@dp.callback_query(F.data.casefold().startswith('search_page:'), PostSearchForm.license_plate)
async def search_license_plate_cb(query: CallbackQuery, state: FSMContext):
    data = try_parse_query_data(query.data)
    if not data:
        return
    page = data.get('search_page', '1')
    state_data = await state.get_data()
    license_plate = state_data.get('license_plate')
    if not page or not page.isdigit():
        return await query.answer(f'Invalid page {page}.')
    await query.answer(f'Search page {page}.')
    page = int(page)
    post_inline_builder = InlineKeyboardBuilder()
    queryset = await sync_to_async(Post.objects.filter)(license_plate__iexact=license_plate, status=PostStatus.APPROVED)
    count = await sync_to_async(queryset.count)()
    async for obj in queryset.order_by('-created_at')[(page - 1) * PAGE_SIZE:page * PAGE_SIZE]:
        ctg = await sync_to_async(Category.objects.get)(id=obj.category_id)
        txt = f'{ctg.name} | {obj.created_at.strftime("%d-%m-%Y %H:%M")}'
        post_inline_builder.row(InlineKeyboardButton(text=txt, callback_data=f'search_post_info:{obj.id}:page:{page}'))
    prev_next_btn = []
    if page > 1:
        prev_next_btn.extend([
            InlineKeyboardButton(text='<<', callback_data=f'search_page:1'),
            InlineKeyboardButton(text='< Prev', callback_data=f'search_page:{page - 1}')
        ])
    if count > page * PAGE_SIZE:
        prev_next_btn.extend([
            InlineKeyboardButton(text='Next >', callback_data=f'search_page:{page + 1}'),
            InlineKeyboardButton(text='>>', callback_data=f'search_page:{int(-(count // -PAGE_SIZE))}')
        ])
    post_inline_builder.row(*prev_next_btn)
    await bot.delete_message(query.from_user.id, query.message.message_id)
    await bot.send_message(
        query.from_user.id, 'Found results:',
        reply_markup=post_inline_builder.as_markup()
    )


@dp.callback_query(F.data.casefold().startswith('search_post_info:'), PostSearchForm.license_plate)
async def search_license_plate_post_info_cb(query: CallbackQuery, state: FSMContext):
    data = try_parse_query_data(query.data)
    if not data:
        return
    post_id = data.get('search_post_info')
    page = data.get('page', 1)
    photo_num = int(data.get('photo_num', 0))
    if not post_id or not post_id.isdigit():
        return await query.answer(f'Invalid post id {post_id}.')
    await query.answer('Post details.')
    post_inline_builder = InlineKeyboardBuilder()
    post = await sync_to_async(Post.objects.get)(id=post_id)
    ctg = await sync_to_async(Category.objects.get)(id=post.category_id)
    queryset = await sync_to_async(PostImage.objects.filter)(post_id=post_id)
    photo_count = await sync_to_async(queryset.count)()
    photo = None
    if photo_count > photo_num:
        photos = await sync_to_async(list)(queryset)
        photo = photos[photo_num]
    post_controls = []
    if photo_count > 1:
        num = (photo_num + 1) % photo_count
        post_controls.append(InlineKeyboardButton(
            text='Next photo >', callback_data=f'search_post_info:{post_id}:page:{page}:photo_num:{num}')
        )
    post_inline_builder.row(*post_controls)
    post_inline_builder.row(InlineKeyboardButton(
        text='< Back to list', callback_data=f'search_page:{page}')
    )
    txt = Text(
        Bold('Category'), ': ', ctg.name, '\n',
        Bold('Creation date'), ': ', post.created_at.strftime("%d-%m-%Y %H:%M"), '\n',
        Bold('Status'), ': ', post.get_status_display(), '\n',
    )
    if post.license_plate:
        txt += Text(Bold('License plate'), ':', post.license_plate, '\n')
    if post.location:
        txt += Text(
            Bold('Location'), ':\n',
            '  Longitude: ', post.location.x, '\n',
            '  Latitude; ', post.location.y, '\n'
        )
    txt += Text(
        Bold('Address'), ': ', post.address, '\n',
        Bold('Description'), ': ', post.description
    )
    await bot.delete_message(query.from_user.id, query.message.message_id)
    # TODO: check if Telegram has the file for "file_id"
    if photo:
        media = photo.file_id if photo.file_id else FSInputFile(photo.file.path)
        msg = await bot.send_photo(
            query.from_user.id, media, caption=txt.as_html(),
            reply_markup=post_inline_builder.as_markup()
        )
        if not photo.file_id:
            photo.file_id = msg.photo[-1].file_id
            await sync_to_async(photo.save)()
    else:
        await bot.send_message(
            query.from_user.id, txt.as_html(),
            reply_markup=post_inline_builder.as_markup()
        )


@dp.callback_query(F.data.casefold().startswith(f'post_action:{PostAction.UPDATE}'), PostPageForm.page)
async def post_update_cb(query: CallbackQuery, state: FSMContext):
    data = try_parse_query_data(query.data)
    if not data:
        return
    post_id = data.get('post')
    await query.answer('Post update.')
    update_inline_builder = InlineKeyboardBuilder()
    for f in UPDATE_FIELDS_LIST:
        update_inline_builder.button(text=f[1], callback_data=f'post_update:{f[0]}:post:{post_id}')
    update_inline_builder.adjust(2)
    update_inline_builder.row(InlineKeyboardButton(
        text='< Back to post', callback_data=f'post:{post_id}'
    ))
    txt = 'Please select what you would like to update:'
    await bot.delete_message(query.from_user.id, query.message.message_id)
    await bot.send_message(
        query.from_user.id, txt, reply_markup=update_inline_builder.as_markup()
    )


@dp.callback_query(F.data.casefold().startswith(f'post_update:category_id'), PostPageForm.page)
async def post_update_category_cb(query: CallbackQuery, state: FSMContext):
    data = try_parse_query_data(query.data)
    post_id = data.get('post')
    post = await sync_to_async(Post.objects.get)(id=post_id)
    category = await sync_to_async(Category.objects.get)(id=post.category_id)
    state_data = await state.get_data()
    page = state_data.get('page', 1)
    await query.answer('Select category.')
    category_inline_builder = InlineKeyboardBuilder()
    async for obj in Category.objects.filter(violator_id=category.violator_id):
        category_inline_builder.button(
            text=obj.name, callback_data=f'update_complete:category_id:post:{post_id}:category_id:{obj.id}:page:{page}'
        )
    category_inline_builder.adjust(2)
    category_inline_builder.row(InlineKeyboardButton(
        text='< Back to post', callback_data=f'post:{post_id}:page:{page}'
    ))
    await state.clear()
    await state.set_state(PostCreateForm.category_id)
    txt = Text('Your current category is: ', Bold(category.name))
    await bot.edit_message_text(
        txt.as_html(), query.from_user.id, query.message.message_id,
        reply_markup=category_inline_builder.as_markup()
    )


@dp.callback_query(F.data.casefold().startswith(f'update_complete:category_id'))
async def post_update_category_complete_cb(query: CallbackQuery, state: FSMContext):
    data = try_parse_query_data(query.data)
    page = data.pop('page', 1)
    post_id = data.pop('post')
    category_id = data.pop('category_id')
    queryset = await sync_to_async(Post.objects.filter)(id=post_id)
    await sync_to_async(queryset.update)(category_id=category_id)
    await state.clear()
    await state.set_state(PostPageForm.page)
    await state.update_data(page=page)
    post_inline_builder = InlineKeyboardBuilder()
    post_inline_builder.row(InlineKeyboardButton(
        text='< Back to post', callback_data=f'post:{post_id}')
    )
    await bot.delete_message(query.from_user.id, query.message.message_id)
    await bot.send_message(
        query.from_user.id, 'Post category updated',
        reply_markup=post_inline_builder.as_markup()
    )


@dp.callback_query(F.data.casefold().startswith(f'post_update:photo'), PostPageForm.page)
async def post_update_photo_cb(query: CallbackQuery, state: FSMContext):
    data = try_parse_query_data(query.data)
    post_id = data.get('post')
    photo_num = int(data.get('photo_num', 0))
    queryset = await sync_to_async(PostImage.objects.filter)(post_id=post_id)
    photo_count = await sync_to_async(queryset.count)()
    state_data = await state.get_data()
    page = state_data.get('page', 1)
    await query.answer('Update photo.')
    photo_inline_builder = InlineKeyboardBuilder()
    photo = None
    photo_controls = []
    if photo_count > photo_num:
        photos = await sync_to_async(list)(queryset)
        photo = photos[photo_num]
    if photo_count > 1:
        photo_controls.append(
            InlineKeyboardButton(
                text='Delete', callback_data=f'post_update:delete_photo:post:{post_id}:photo:{photo.id}'
            )
        )
    if photo_count < 3:
        photo_controls.append(InlineKeyboardButton(
            text='Add photo', callback_data=f'post_update:add_photo:post:{post_id}:page:{page}')
        )
    if photo_count > 1:
        num = (photo_num + 1) % photo_count
        photo_controls.append(InlineKeyboardButton(
            text='Next photo >', callback_data=f'post_update:photo:post:{post_id}:page:{page}:photo_num:{num}')
        )
    photo_inline_builder.row(*photo_controls)
    photo_inline_builder.row(InlineKeyboardButton(
        text='< Back to post', callback_data=f'post:{post_id}')
    )
    await bot.delete_message(query.from_user.id, query.message.message_id)
    # TODO: check if Telegram has the file for "file_id"
    if photo:
        media = photo.file_id if photo.file_id else FSInputFile(photo.file.path)
        msg = await bot.send_photo(
            query.from_user.id, media, reply_markup=photo_inline_builder.as_markup()
        )
        if not photo.file_id:
            photo.file_id = msg.photo[-1].file_id
            await sync_to_async(photo.save)()
    else:
        await bot.send_message(
            query.from_user.id, 'No photo found.',
            reply_markup=photo_inline_builder.as_markup()
        )


@dp.callback_query(F.data.casefold().startswith(f'post_update:photo_delete'))
async def photo_update_delete_cb(query: CallbackQuery, state: FSMContext):
    data = try_parse_query_data(query.data)
    post_id = data.get('post')
    photo_id = data.get('photo')
    photo = await sync_to_async(PostImage.objects.get)(id=photo_id)
    await sync_to_async(photo.delete)()
    await bot.delete_message(query.from_user.id, query.message.message_id)
    photo_inline_builder = InlineKeyboardBuilder()
    photo_inline_builder.row(InlineKeyboardButton(
        text='< Back to post', callback_data=f'post_update:photo:post:{post_id}')
    )
    await bot.send_message(
        query.from_user.id, 'Post photo deleted',
        reply_markup=photo_inline_builder.as_markup()
    )


@dp.callback_query(F.data.casefold().startswith(f'post_update:add_photo'), PostPageForm.page)
async def photo_update_add_cb(query: CallbackQuery, state: FSMContext):
    await bot.delete_message(query.from_user.id, query.message.message_id)
    data = try_parse_query_data(query.data)
    msg = 'Please send photos, max 3 allowed, if exceeded, will substitute existing photo:'
    await state.set_state(PostUpdateForm.photo)
    await state.update_data(post_id=data.get('post'))
    await state.update_data(page=data.get('page'))
    await bot.send_message(query.from_user.id, msg)


@dp.message(PostUpdateForm.photo)
async def photo_update_add_complete(message: Message, state: FSMContext, album: list[PhotoSize] = None):
    photos = album or [message.photo]
    if not photos:
        msg = 'Please send photos, max 3 allowed, if exceeded, will substitute existing photo:'
        return await message.answer(msg)
    photos = photos[:3]
    data = await state.get_data()
    post_id = data.get('post_id')
    page = data.get('page', 1)
    queryset = await sync_to_async(PostImage.objects.filter)(post_id=post_id)
    count = await sync_to_async(queryset.count)()
    existing_photos = await sync_to_async(list)(queryset)
    while len(photos) + count > 3:
        p = existing_photos.pop()
        await sync_to_async(p.delete)()
    for photo in photos:
        # Each photo has 4 resolutions, the last one has the best quality.
        fp = io.BytesIO()
        await bot.download(photo[-1].file_id, fp)
        await sync_to_async(PostImage.objects.create)(
            post_id=post_id, file=File(fp, photo[-1].file_unique_id), file_id=photo[-1].file_id
        )
    await state.clear()
    post_inline_builder = InlineKeyboardBuilder()
    post_inline_builder.row(InlineKeyboardButton(
        text='< Back to post', callback_data=f'post:{post_id}:page:{page}')
    )
    await bot.send_message(message.from_user.id, 'Photo updated', reply_markup=post_inline_builder.as_markup())


@dp.callback_query(F.data.casefold().startswith(f'post_update:location'))
async def post_update_location_cb(query: CallbackQuery, state: FSMContext):
    data = try_parse_query_data(query.data)
    msg = 'Please send the location:'
    state_data = await state.get_data()
    page = state_data.get('page', 1)
    await state.set_state(PostUpdateForm.location)
    await state.update_data(post_id=data.get('post'))
    await state.update_data(page=page)
    await bot.send_message(query.from_user.id, msg)


@dp.message(PostUpdateForm.location)
async def post_update_location_complete(message: Message, state: FSMContext):
    if not message.location:
        return await message.answer('Please send the location:')
    data = await state.get_data()
    post_id = data.get('post_id')
    page = data.get('page', 1)
    location = Point(x=message.location.longitude, y=message.location.latitude)
    queryset = await sync_to_async(Post.objects.filter)(id=post_id)
    await sync_to_async(queryset.update)(location=location)
    await state.clear()
    post_inline_builder = InlineKeyboardBuilder()
    post_inline_builder.row(InlineKeyboardButton(
        text='< Back to post', callback_data=f'post:{post_id}:page:{page}')
    )
    await bot.send_message(message.from_user.id, 'Location updated', reply_markup=post_inline_builder.as_markup())


@dp.callback_query(F.data.casefold().startswith(f'post_update:address'))
async def post_update_address_cb(query: CallbackQuery, state: FSMContext):
    data = try_parse_query_data(query.data)
    msg = 'Please enter the address:'
    state_data = await state.get_data()
    page = state_data.get('page', 1)
    await state.set_state(PostUpdateForm.address)
    await state.update_data(post_id=data.get('post'))
    await state.update_data(page=page)
    await bot.send_message(query.from_user.id, msg)


@dp.message(PostUpdateForm.address)
async def post_update_address_complete(message: Message, state: FSMContext):
    data = await state.get_data()
    post_id = data.get('post_id')
    page = data.get('page', 1)
    queryset = await sync_to_async(Post.objects.filter)(id=post_id)
    await sync_to_async(queryset.update)(address=message.text)
    await state.clear()
    post_inline_builder = InlineKeyboardBuilder()
    post_inline_builder.row(InlineKeyboardButton(
        text='< Back to post', callback_data=f'post:{post_id}:page:{page}')
    )
    await bot.send_message(message.from_user.id, 'Address updated', reply_markup=post_inline_builder.as_markup())


@dp.callback_query(F.data.casefold().startswith(f'post_update:license_plate'))
async def post_update_license_plate_cb(query: CallbackQuery, state: FSMContext):
    data = try_parse_query_data(query.data)
    msg = 'Please enter the license plate:'
    state_data = await state.get_data()
    page = state_data.get('page', 1)
    await state.set_state(PostUpdateForm.license_plate)
    await state.update_data(post_id=data.get('post'))
    await state.update_data(page=page)
    await bot.send_message(query.from_user.id, msg)


@dp.message(PostUpdateForm.license_plate)
async def post_update_license_plate_complete(message: Message, state: FSMContext):
    data = await state.get_data()
    post_id = data.get('post_id')
    page = data.get('page', 1)
    queryset = await sync_to_async(Post.objects.filter)(id=post_id)
    await sync_to_async(queryset.update)(license_plate=message.text)
    await state.clear()
    post_inline_builder = InlineKeyboardBuilder()
    post_inline_builder.row(InlineKeyboardButton(
        text='< Back to post', callback_data=f'post:{post_id}:page:{page}')
    )
    await bot.send_message(message.from_user.id, 'License plate updated', reply_markup=post_inline_builder.as_markup())


@dp.callback_query(F.data.casefold().startswith(f'post_update:description'))
async def post_update_description_cb(query: CallbackQuery, state: FSMContext):
    data = try_parse_query_data(query.data)
    msg = 'Please enter the description:'
    state_data = await state.get_data()
    page = state_data.get('page', 1)
    await state.set_state(PostUpdateForm.address)
    await state.update_data(post_id=data.get('post'))
    await state.update_data(page=page)
    await bot.send_message(query.from_user.id, msg)


@dp.message(PostUpdateForm.description)
async def post_update_description_complete(message: Message, state: FSMContext):
    data = await state.get_data()
    post_id = data.get('post_id')
    page = data.get('page', 1)
    queryset = await sync_to_async(Post.objects.filter)(id=post_id)
    await sync_to_async(queryset.update)(description=message.text)
    await state.clear()
    post_inline_builder = InlineKeyboardBuilder()
    post_inline_builder.row(InlineKeyboardButton(
        text='< Back to post', callback_data=f'post:{post_id}:page:{page}')
    )
    await bot.send_message(message.from_user.id, 'Description updated', reply_markup=post_inline_builder.as_markup())


@dp.callback_query(F.data.casefold().startswith(f'post_action:{PostAction.DELETE}'), PostPageForm.page)
async def post_delete_cb(query: CallbackQuery, state: FSMContext):
    data = try_parse_query_data(query.data)
    post_id = data.get('post')
    post = await sync_to_async(Post.objects.get)(id=post_id)
    await sync_to_async(post.delete)()
    await query.answer('Post deleted.')
    post_inline_builder = InlineKeyboardBuilder()
    state_data = await state.get_data()
    page = state_data.get("page", 1)
    post_inline_builder.row(InlineKeyboardButton(
        text='< Back to list', callback_data=f'posts_page:{page}:user:{post.user_id}')
    )
    await bot.delete_message(query.from_user.id, query.message.message_id)
    await bot.send_message(
        query.from_user.id, 'Deleted post',
        reply_markup=post_inline_builder.as_markup()
    )


async def main() -> None:
    await bot.set_my_commands(commands)
    dp.message.middleware(AlbumMiddleware(0.04))
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
