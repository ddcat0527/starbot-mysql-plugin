from typing import List

from graia.ariadne import Ariadne
from graia.ariadne.message.element import Image
from graia.ariadne.event.mirai import NewFriendRequestEvent
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema
from loguru import logger

import asyncio

from starbot.painter.PicGenerator import PicGenerator, Color
from starbot.utils import config, redis

prefix = config.get("COMMAND_PREFIX")
master_qq = config.get("MASTER_QQ")

channel = Channel.current()


async def __exists_mode_status(qq_num: int) -> bool:
    return await redis.hexists(f"StarBotModeStatus", qq_num)


async def __get_mode_status(qq_num: int) -> int:
    return await redis.hgeti(f"StarBotModeStatus", qq_num)


async def check_bot_mode_public(qq_num: int) -> bool:
    """
    :param qq_num: bot qq号
    :return: False为私有状态，True为公开状态 如果键值对不存在兼容旧版本为公开状态返回True
    """
    if await __exists_mode_status(qq_num) and await __get_mode_status(qq_num) == 1:
        return False
    return True


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
    event_inner = f"qq[{event.nickname}]({event.supplicant}) 内容({event.message})"
    logger.info(f"触发事件: 好友申请 {event_inner}")
    if master_qq == "":
        logger.info(f"未配置MASTER_QQ，忽略好友申请处理")
        return
    if event.supplicant == master_qq:
        logger.info(f"主人好友申请自动通过 {event_inner}")
        await event.accept()
        return
    if await check_bot_mode_public(app.account):
        logger.info(f"公开模式，自动通过好友申请 {event_inner}")
        await event.accept()
        accept_message = [f"bot功能：B站动态直播订阅",
                          f"主人qq{master_qq}",
                          f"私聊和群聊发送 {prefix}订阅帮助 获取B站动态直播订阅帮助"]
        await asyncio.sleep(2)
        await app.send_friend_message(event.supplicant, _draw_pic(accept_message))
        return
    else:
        logger.info(f"私人模式，拒绝好友申请 {event_inner}")
        await event.reject()
        return

