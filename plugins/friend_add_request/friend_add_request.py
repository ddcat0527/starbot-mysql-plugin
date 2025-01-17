from typing import List

from graia.ariadne import Ariadne
from graia.ariadne.message.element import Image
from graia.ariadne.event.mirai import NewFriendRequestEvent
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema
from loguru import logger

import asyncio

from starbot.painter.PicGenerator import PicGenerator, Color
from starbot.utils import config

prefix = config.get("COMMAND_PREFIX")
master_qq = config.get("MASTER_QQ")

channel = Channel.current()


def _draw_pic(messages: List, width=1200, height=100000):
    if messages is None or len(messages) == 0:
        return None
    pic = PicGenerator(width, height)
    pic.set_pos(50, 50).draw_rounded_rectangle(0, 0, width, height, 35, Color.WHITE).copy_bottom(35)
    for message in messages:
        pic.draw_text_multiline(50, message)
    # 底部版权信息，请务必保留此处
    pic.draw_text_right(25, "Designed By StarBot", Color.GRAY)
    pic.draw_text_right(25, "https://github.com/Starlwr/StarBot", Color.LINK)
    pic.draw_text_right(25, f"Created by {__package__}", Color.GREEN)
    pic.crop_and_paste_bottom()
    return Image(base64=pic.base64())


@channel.use(ListenerSchema(listening_events=[NewFriendRequestEvent]))
async def _FriendAddRequest(app: Ariadne, event: NewFriendRequestEvent):
    event_inner = f"qq[{event.supplicant}]({event.nickname}) 内容({event.message})"
    logger.info(f"触发事件: 好友申请 {event_inner}")
    if master_qq == "":
        logger.info(f"未配置MASTER_QQ，忽略好友申请处理")
        return
    await event.accept()
    logger.info(f"自动通过好友申请 {event_inner}")
    if event.supplicant != master_qq:
        accept_message = [f"bot功能：B站动态直播订阅",
                          f"主人qq{master_qq}",
                          f"私聊和群聊发送 {prefix}订阅帮助 获取B站动态直播订阅帮助"]
        await asyncio.sleep(2)
        await app.send_friend_message(event.supplicant, _draw_pic(accept_message))
