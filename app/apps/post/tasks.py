from bot.main import bot_delete_message, CHANNEL_NAME, bot_send_post
from apps.post.models import Post, PostMedia
from apps.post.choices import PostMediaType
from collections.abc import Iterable
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
def process_media(post_id: int | str):
    queryset = PostMedia.objects.filter(post_id=post_id)
    for photo in queryset:
        fp = io.BytesIO()
        if photo.file_type == PostMediaType.IMAGE:
            img = Image.open(photo.file.path)
            width, height = img.size
            if width > 1920:
                height = int(1920 * height / width)
                width = 1920
            if height > 1080:
                width = int(1080 * width / height)
                height = 1080
            img = img.resize((width, height))
            img.save(fp, format='jpeg', quality=80, optimize=True)
        with open(photo.file.path, 'wb') as f:
            f.write(fp.read())
        # elif photo.file_type == PostMediaType.VIDEO:
        #     # TODO: Scale video down if too big resolution.
        #     data = ffmpeg.probe(photo.file.path)
        #     for stream in data.get('streams', []):
        #         if stream.get('codec_type') != 'video':
        #             continue
        #         duration = stream.get('duration')
        #         if float(duration) > config.MAX_VIDEO_DURATION:
        #             input = ffmpeg.input(photo.file.path)
        #             output_file_name = os.path.join(tempfile.gettempdir(), photo.file_id + '_output')
        #             output = ffmpeg.output(
        #                 input.trim(start_frame=0, end_frame=config.MAX_VIDEO_DURATION),
        #                 output_file_name
        #             )
        #             output.run()
        #             with open(output_file_name, 'rb') as of:
        #                 fp.write(of.read())
        #             os.remove(output_file_name)
        #     pass
        # with open(photo.file.path, 'wb') as f:
        #     f.write(fp.read())
