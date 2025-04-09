from graia.ariadne import Ariadne
from graia.ariadne.event.mirai import BotInvitedJoinGroupRequestEvent
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema
from loguru import logger

from starbot.utils import config, redis

master_qq = config.get("MASTER_QQ")
prefix = config.get("COMMAND_PREFIX")

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


@channel.use(ListenerSchema(listening_events=[BotInvitedJoinGroupRequestEvent]))
async def _GroupInvite(app: Ariadne, event: BotInvitedJoinGroupRequestEvent):
    event_inner = f"群聊[{event.group_name}]({event.source_group}) 邀请人[{event.nickname}]({event.supplicant})"
    logger.info(f"触发事件: 邀请加入群聊 {event_inner}")
    if master_qq == "":
        logger.info(f"未配置MASTER_QQ")
        return
    if event.supplicant == master_qq:
        logger.info(f"主人邀请自动通过 {event_inner}")
        await event.accept()
        return
    if await check_bot_mode_public(app.account):
        logger.info(f"公开模式，自动通过群聊邀请 {event_inner}")
        await event.accept()
        return
    else:
        logger.info(f"私人模式，拒绝群聊邀请 {event_inner}")
        await event.reject()
        return
