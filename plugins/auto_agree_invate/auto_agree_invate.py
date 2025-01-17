from graia.ariadne import Ariadne
from graia.ariadne.event.mirai import BotInvitedJoinGroupRequestEvent
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema
from loguru import logger

from starbot.utils import config

master_qq = config.get("MASTER_QQ")

channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[BotInvitedJoinGroupRequestEvent]))
async def _GroupInvite(app: Ariadne, event: BotInvitedJoinGroupRequestEvent):
    logger.info(f"触发事件 : 邀请加入群聊[{event.source_group}]({event.group_name}) qq[{event.supplicant}]({event.nickname})")
    if master_qq == "":
        logger.info(f"未配置MASTER_QQ")
        return
    await event.accept()
    log_info = f"同意加入群聊[{event.source_group}]({event.group_name}) 邀请人[{event.supplicant}]({event.nickname})"
    send_message = f"同意加入群聊[{event.source_group}]({event.group_name}) 邀请人[{event.supplicant}]({event.nickname})"
    logger.info(log_info)
    await app.send_friend_message(master_qq, send_message)
