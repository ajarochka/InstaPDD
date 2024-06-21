from bot.main import bot_delete_message, CHANNEL_NAME, bot_send_post, bot
from apps.post.models import Post, PostMedia
from apps.post.choices import PostMediaType
from asgiref.sync import async_to_sync
from collections.abc import Iterable
from django.core.files import File
from constance import config
from IPDD.celery import app
from PIL import Image
import tempfile
import ffmpeg
import os
import io


@app.task(name='on-post_approve')
def on_post_approve(post_id: int):
    post = Post.objects.get(id=post_id)
    messages = bot_send_post(CHANNEL_NAME, post.id)
    if not messages:
        return
    if not isinstance(messages, Iterable):
        messages = [messages]
    post.bot_message_id = ','.join([m.message_id for m in messages])
    post.save(update_fields='bot_message_id')


@app.task(name='on_post_reject')
def on_post_reject(post_id: int):
    post = Post.objects.get(id=post_id)
    for msg_id in post.bot_message_id.split(','):
        bot_delete_message(CHANNEL_NAME, msg_id)
    post.bot_message_id = None
    post.save(update_fields='bot_message_id')


@app.task(name='process_media')
def process_media(post_id: int | str, file_id: str, file_uid: str, mime_type: str):
    fp = io.BytesIO()
    async_to_sync(bot.download(file_id, fp))()
    if mime_type == PostMediaType.IMAGE:
        img = Image.open(fp)
        width, height = img.size
        if width > 1920:
            height = 1920 * round(height / width, 2)
            width = 1920
        if height > 1080:
            width = 1080 * round(width / height, 2)
            height = 1080
        img = img.resize((width, height))
        img.save(fp, format='jpeg', quality=80, optimize=True)
    elif mime_type == PostMediaType.VIDEO:
        # TODO: Scale video down if too big resolution.
        with tempfile.NamedTemporaryFile() as tmp_file:
            data = ffmpeg.probe(tmp_file)
            for stream in data.get('streams', []):
                if stream.get('codec_type') != 'video':
                    continue
                duration = stream.get('duration')
                if duration > config.MAX_VIDEO_DURATION:
                    input = ffmpeg.input(tmp_file)
                    output_file_name = os.path.join(tempfile.gettempdir(), file_id + '_output')
                    output = ffmpeg.output(input.trim(0, config.MAX_VIDEO_DURATION), output_file_name)
                    output.run()
                    with open(output_file_name, 'rb') as of:
                        fp.write(of.read())
                    os.remove(output_file_name)
    PostMedia.objects.create(
        post_id=post_id, file=File(fp, file_uid), file_id=file_id, file_type=mime_type
    )
