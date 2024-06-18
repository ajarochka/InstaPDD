# from bot.main import bot_delete_message, CHANNEL_NAME, bot_send_post
from collections.abc import Iterable
from apps.post.models import Post
from IPDD.celery import app


# @app.task(name='on-post_approve')
# def on_post_approve(post_id: int):
#     post = Post.objects.get(id=post_id)
#     messages = bot_send_post(CHANNEL_NAME, post.id)
#     if not messages:
#         return
#     if not isinstance(messages, Iterable):
#         messages = [messages]
#     post.bot_message_id = ','.join([m.message_id for m in messages])
#     post.save(update_fields='bot_message_id')
#
#
# @app.tasl(name='on_post_reject')
# def on_post_reject(post_id: int):
#     post = Post.objects.get(id=post_id)
#     for msg_id in post.bot_message_id.split(','):
#         bot_delete_message(CHANNEL_NAME, msg_id)
#     post.bot_message_id = None
#     post.save(update_fields='bot_message_id')
