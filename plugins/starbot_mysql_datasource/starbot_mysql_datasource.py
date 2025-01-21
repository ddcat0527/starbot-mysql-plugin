import asyncio
from typing import List, Optional, Union
from creart import create
from graia.ariadne import Ariadne
from graia.ariadne.event.message import FriendMessage, GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Image, AtAll, Plain
from graia.ariadne.message.parser.twilight import Twilight, FullMatch, UnionMatch, ElementMatch, ArgumentMatch, \
    ResultValue, ParamMatch, SpacePolicy
from graia.ariadne.model import Friend, Group, Member, MemberPerm
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema
from graia.broadcast.interrupt import InterruptControl
from graia.broadcast.interrupt.waiter import Waiter
from loguru import logger
import base64

from starbot.utils import config
from starbot.core.model import PushType

from .mysql_utils import ObjMysql, check_not_mysql_datasource, check_mysql_datasource, create_auto_follow_task, \
    draw_image_pic, draw_pic, check_at_object, get_message_help, select_uname_and_room_id
from .mysql_trans import datasource_trans_to_mysql

prefix = config.get("COMMAND_PREFIX")
master_qq = config.get("MASTER_QQ")

channel = Channel.current()
inc = create(InterruptControl)

add_describe = ["添加订阅", "watch"]
delete_describe = ["删除订阅", "unwatch"]
list_describe = ["查询订阅", "list"]
reload_uid = ["重载订阅", "reloaduid"]
add_logo = ["设置立绘", "setlogo"]
clear_logo = ["清除立绘", "clearlogo"]
set_message = ["设置推送信息", "setmessage"]
check_describe_abnormal = ["检测异常订阅", "checkabnormal"]
clear_describe_abnormal = ["清除异常订阅", "clearabnormal"]
trans_to_mysql = ["数据源转储", "datasourcetrans"]
help_cmd = ["订阅帮助"]

describe_cmd = {
    add_describe[0]: {
        "cmd": add_describe,
        "describe_group": [f"{prefix}[{' | '.join(add_describe)}] uid",
                           "可选参数：[-t | --type] [news | live | live_on | all] 订阅类型[动态，开播和下播，开播，全部推送(默认)]",
                           "可选参数：[-a | --atall] [news | live | all | no] at全体需要管理员权限[动态，开播，动态和开播，无(默认)]",
                           "可选参数：[-r | --report] [time | danmu | all] 直播报告内容[直播时长(默认)，直播时长和弹幕云词，全部信息]",
                           "注意：uid若已在本群订阅，则本次添加视为更新配置",
                           "为防止被滥用，该命令需要群管理员及以上权限可用",
                           f"示例: {prefix}{add_describe[0]} 123456",
                           f"示例: {prefix}{add_describe[0]} 123456 -t all -a no -r time"],
        "describe_friend": [f"{prefix}[{' | '.join(add_describe)}] uid",
                            "可选参数：[-t | --type] [news | live | live_on | all] 订阅类型[动态，开播和下播，开播，全部推送(默认)]",
                            "可选参数：[-r | --report] [time | danmu | all] 直播报告内容[直播时长(默认)，直播时长和弹幕云词，全部信息]",
                            "注意：uid若已被私聊订阅，则本次添加视为更新配置",
                            f"示例: {prefix}{add_describe[0]} 123456",
                            f"示例: {prefix}{add_describe[0]} 123456 -t all -r time"],
        "describe_admin": [f"{prefix}[{' | '.join(add_describe)}] uid",
                           "可选参数：[-g | --group] [group_num] 订阅发布群号",
                           "可选参数：[-t | --type] [news | live | live_on | all] 订阅类型[动态，开播和下播，开播，全部推送(默认)]",
                           "可选参数：[-a | --atall] [news | live | all | no] at全体[动态，开播，动态和开播，无(默认)]，对群监听有效",
                           "可选参数：[-r | --report] [time | danmu | all] 直播报告内容[直播时长(默认)，直播时长和弹幕云词，全部信息]",
                           "注意：uid若已被私聊订阅，则本次添加视为更新配置",
                           f"示例: {prefix}{add_describe[0]} 123456 -g 456789",
                           f"示例: {prefix}{add_describe[0]} 123456 -g 456789 -t all -a no -r time"]
    },
    delete_describe[0]: {
        "cmd": delete_describe,
        "describe_group": [f"{prefix}[{' | '.join(delete_describe)}] uid",
                           "为防止被滥用，该命令需要群管理员及以上权限可用",
                           f"示例: {prefix}{delete_describe[0]} 123456"],
        "describe_friend": [f"{prefix}[{' | '.join(delete_describe)}] uid",
                            f"示例: {prefix}{delete_describe[0]} 123456"],
        "describe_admin": [f"{prefix}[{' | '.join(delete_describe)}] uid",
                           "可选参数：[-g | --group] [group_num] 订阅所在群号",
                           f"示例: {prefix}{delete_describe[0]} 123456 -g 456789"],
    },
    list_describe[0]: {
        "cmd": list_describe,
        "describe_group": [f"{prefix}[{' | '.join(list_describe)}]",
                           "可选参数：[-t | --text] [true | false] 是否使用文字模式发送[是，否(默认)]",
                           f"示例: {prefix}{list_describe[0]}",
                           f"示例: {prefix}{list_describe[0]} -t true"],
        "describe_friend": [f"{prefix}[{' | '.join(list_describe)}]",
                            "可选参数：[-t | --text] [true | false] 是否使用文字模式发送[是，否(默认)]",
                            "查询私聊订阅信息",
                            f"示例: {prefix}{list_describe[0]}",
                            f"示例: {prefix}{list_describe[0]} -t true"],
        "describe_admin": [f"{prefix}[{' | '.join(list_describe)}]",
                           "可选参数：[-t | --text] [true | false] 是否使用文字模式发送[是，否(默认)]",
                           "查询所有订阅信息",
                           f"示例: {prefix}{list_describe[0]}",
                           f"示例: {prefix}{list_describe[0]} -t true"],
    },
    reload_uid[0]: {
        "cmd": reload_uid,
        "describe_group": [],
        "describe_friend": [],
        "describe_admin": [f"{prefix}[{' | '.join(reload_uid)}] uid",
                           "从数据库重新载入订阅目标",
                           f"示例: {prefix}{reload_uid[0]} uid"],
    },
    add_logo[0]: {
        "cmd": add_logo,
        "describe_group": [f"{prefix}[{' | '.join(add_logo)}] uid",
                           "设置直播报告立绘，发送命令后根据命令交互完成设置",
                           "注意：uid需要在该群被订阅才能成功",
                           "为防止被滥用，该命令需要群管理员及以上权限可用",
                           f"示例: {prefix}{add_logo[0]} uid"],
        "describe_friend": [f"{prefix}[{' | '.join(add_logo)}] uid",
                            "设置直播报告立绘，发送命令后根据命令交互完成设置",
                            "注意：uid需要被订阅才能成功",
                            f"示例: {prefix}{add_logo[0]} uid"],
        "describe_admin": [f"{prefix}[{' | '.join(add_logo)}] uid",
                           "可选参数：[-g | --group] [group_num] 订阅所在群号",
                           "设置直播报告立绘，发送命令后根据命令交互完成设置",
                           "注意：uid需要被订阅才能成功",
                           f"示例: {prefix}{add_logo[0]} -g 456789 uid"]
    },
    clear_logo[0]: {
        "cmd": clear_logo,
        "describe_group": [f"{prefix}[{' | '.join(clear_logo)}] uid",
                           "清除直播报告立绘",
                           "注意：uid需要在该群被订阅才能成功",
                           "为防止被滥用，该命令需要群管理员及以上权限可用",
                           f"示例: {prefix}{clear_logo[0]} uid"],
        "describe_friend": [f"{prefix}[{' | '.join(clear_logo)}] uid",
                            "清除直播报告立绘",
                            "注意：uid需要被订阅才能成功",
                            f"示例: {prefix}{clear_logo[0]} uid"],
        "describe_admin": [f"{prefix}[{' | '.join(clear_logo)}] uid",
                           "可选参数：[-g | --group] [group_num] 订阅所在群号",
                           "清除直播报告立绘",
                           "注意：uid需要被订阅才能成功",
                           f"示例: {prefix}{clear_logo[0]} -g 456789 uid"]
    },
    set_message[0]: {
        "cmd": set_message,
        "describe_group": [f"{prefix}[{' | '.join(set_message)}] uid",
                           "必选参数：[-t | --type] [news | live_on | live_off]  类型[动态提醒，开播提醒，下播提醒]",
                           "设置动态提醒，开播提醒和下播提醒",
                           "注意：uid需要在该群被订阅才能成功",
                           "为防止被滥用，该命令需要群管理员及以上权限可用",
                           f"示例: {prefix}{set_message[0]} uid -t live_on"],
        "describe_friend": [f"{prefix}[{' | '.join(set_message)}] uid",
                            "必选参数：[-t | --type] [news | live_on | live_off]  类型[动态提醒，开播提醒，下播提醒]",
                            "设置动态提醒，开播提醒和下播提醒",
                            "注意：uid需要被订阅才能成功",
                            f"示例: {prefix}{set_message[0]} uid -t live_on"],
        "describe_admin": [f"{prefix}[{' | '.join(set_message)} uid]",
                           "可选参数：[-g | --group] [group_num] 订阅所在群号",
                           "必选参数：[-t | --type] [news | live_on | live_off]  类型[动态提醒，开播提醒，下播提醒]",
                           "设置动态提醒，开播提醒和下播提醒",
                           "注意：uid需要被订阅才能成功",
                           f"示例: {prefix}{set_message[0]} -g 456789 uid -t live_on"]
    },
    check_describe_abnormal[0]: {
        "cmd": check_describe_abnormal,
        "describe_group": [],
        "describe_friend": [],
        "describe_admin": [f"{prefix}[{' | '.join(check_describe_abnormal)}]",
                           "查询已经失效的订阅及其所在群聊",
                           "功能未验证，请谨慎使用",
                           "注意：存在因为qqnt问题导致查询信息错误，请务必手动确认结果",
                           f"示例: {prefix}{check_describe_abnormal[0]}"]
    },
    clear_describe_abnormal[0]: {
        "cmd": clear_describe_abnormal,
        "describe_group": [],
        "describe_friend": [],
        "describe_admin": [f"{prefix}[{' | '.join(clear_describe_abnormal)}]",
                           "清除所有已经失效的订阅",
                           "功能未验证，请谨慎使用",
                           f"示例: {prefix}{clear_describe_abnormal[0]}"]
    },
    trans_to_mysql[0]: {
        "cmd": trans_to_mysql,
        "describe_group": [],
        "describe_friend": [],
        "describe_admin": [f"{prefix}[{' | '.join(trans_to_mysql)}]",
                           "该命令可在其他数据源下使用，用处是将内存中的订阅信息插入mysql数据库中",
                           f"示例: {prefix}{trans_to_mysql[0]}"]
    }
}


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight(
            ElementMatch(At, optional=True),
            FullMatch(prefix),
            UnionMatch(*add_describe).space(SpacePolicy.FORCE),
            "uid" @ ParamMatch(),
            "type" @ ArgumentMatch("-t", "--type", type=str, choices=["news", "live", "live_on", "all"], default="all",
                                   optional=True),
            "atall" @ ArgumentMatch("-a", "--atall", type=str, choices=["news", "live", "all", "no"], default="no",
                                    optional=True),
            "report" @ ArgumentMatch("-r", "--report", type=str, choices=["time", "danmu", "all"], default="time",
                                     optional=True)
        )],
    )
)
async def _AddListenGroup(app: Ariadne, sender: Group, member: Member, message: MessageChain,
                          uid: MessageChain = ResultValue(),
                          type: Optional[str] = ResultValue(), atall: Optional[str] = ResultValue(),
                          report: Optional[str] = ResultValue()):
    if check_not_mysql_datasource():
        return
    if check_at_object(app.account, message) is False:
        return
    uid = uid.display
    if uid == "" or not uid.isdigit():
        logger.info(f"群[{sender.name}]({sender.id}) 触发命令 : {add_describe[0]} uid输入不合法({uid})")
        await app.send_message(sender, MessageChain(draw_pic(f"uid输入不合法({uid})，操作失败", width=800)))
        return
    uid = int(uid)
    group = sender.id
    bot = app.account
    logger.info(
        f"群[{sender.name}]({sender.id}) 触发命令 : {add_describe[0]} ({uid = }, {group = }, {type = }, {atall = }, {report = })")
    if master_qq == "" or f"{member.id}" != f"{master_qq}":
        person = await app.get_member(group, member.id)
        if person.permission < MemberPerm.Administrator:
            logger.info(
                f"群[{sender.name}]({sender.id}) 触发命令 : {add_describe[0]} 权限不足({member.id = }, {person.permission = })")
            await app.send_message(sender,
                                   MessageChain(draw_pic("权限不足，操作失败，仅群管理员和群主可操作", width=800)))
            return
    obj_mysql = ObjMysql()
    await obj_mysql.init_target(bot, uid, group)
    obj_mysql.set_report_obj(type, atall, report)
    await obj_mysql.save()
    uname, _ = obj_mysql.get_target_uname_and_roomid()
    create_auto_follow_task()
    logger.info(f"群[{sender.name}]({sender.id}) 触发命令 : {add_describe[0]} 成功 [{uname}]({uid})")
    await app.send_message(sender, MessageChain(draw_pic(f"{uname}(UID:{uid})添加订阅成功", width=800)))


@channel.use(
    ListenerSchema(
        listening_events=[FriendMessage],
        inline_dispatchers=[Twilight(
            ElementMatch(At, optional=True),
            FullMatch(prefix),
            UnionMatch(*add_describe).space(SpacePolicy.FORCE),
            "uid" @ ParamMatch(),
            "group" @ ArgumentMatch("-g", "--group", type=int, default=0, optional=True),
            "type" @ ArgumentMatch("-t", "--type", type=str, choices=["news", "live", "live_on", "all"], default="all",
                                   optional=True),
            "atall" @ ArgumentMatch("-a", "--atall", type=str, choices=["news", "live", "all", "no"], default="no",
                                    optional=True),
            "report" @ ArgumentMatch("-r", "--report", type=str, choices=["time", "danmu", "all"], default="time",
                                     optional=True)
        )],
    )
)
async def _AddListenFriend(app: Ariadne, sender: Friend, uid: MessageChain = ResultValue(),
                           group: Optional[int] = ResultValue(),
                           type: Optional[str] = ResultValue(), atall: Optional[str] = ResultValue(),
                           report: Optional[str] = ResultValue()):
    if check_not_mysql_datasource():
        return
    uid = uid.display
    if uid == "" or not uid.isdigit():
        logger.info(f"好友[{sender.nickname}]({sender.id}) 触发命令 :{add_describe[0]} uid输入不合法({uid})")
        await app.send_message(sender, MessageChain(draw_pic(f"uid输入不合法({uid})，操作失败", width=800)))
        return
    uid = int(uid)
    bot = app.account
    logger.info(
        f"好友[{sender.nickname}]({sender.id}) 触发命令 : {add_describe[0]} ({uid = }, {group = }, {type = }, {atall = }, {report = })")
    if group != 0:
        if master_qq == "" or master_qq != sender.id:
            # 功能需要配置MASTER_QQ
            return
        group_check = await app.get_group(group)
        if group_check is None:
            logger.info(f"好友[{sender.nickname}]({sender.id}) 触发命令 : {add_describe[0]} bot未加入群聊({group})")
            await app.send_message(sender, MessageChain(draw_pic(f"bot未加入群聊({group})，操作失败", width=800)))
            return
        source = group
        source_type = PushType.Group
        msg_prefix = f"群聊{group} "
    else:
        friend_check = await app.get_friend(sender.id)
        if friend_check is None:
            logger.info(f"好友[{sender.nickname}]({sender.id}) 触发命令 : {add_describe[0]} bot未添加好友({sender.id})")
            await app.send_message(sender, MessageChain(draw_pic(f"bot未添加好友({sender.id})，操作失败", width=800)))
            return
        source = sender.id
        source_type = PushType.Friend
        msg_prefix = ""
        atall = "no"  # 好友监听不存在atall属性，直接覆写为no
    obj_mysql = ObjMysql()
    await obj_mysql.init_target(bot, uid, source, source_type)
    obj_mysql.set_report_obj(type, atall, report)
    await obj_mysql.save()
    uname, _ = obj_mysql.get_target_uname_and_roomid()
    create_auto_follow_task()
    logger.info(f"好友[{sender.nickname}]({sender.id}) 触发命令 : {add_describe[0]} 成功 {msg_prefix}[{uname}]({uid})")
    await app.send_message(sender, MessageChain(draw_pic(f"{msg_prefix}{uname}(UID:{uid})添加订阅成功", width=800)))


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight(
            ElementMatch(At, optional=True),
            FullMatch(prefix),
            UnionMatch(*delete_describe).space(SpacePolicy.FORCE),
            "uid" @ ParamMatch()
        )],
    )
)
async def _DelListenGroup(app: Ariadne, sender: Group, member: Member, message: MessageChain,
                          uid: MessageChain = ResultValue()):
    if check_not_mysql_datasource():
        return
    if check_at_object(app.account, message) is False:
        return
    uid = uid.display
    if uid == "" or not uid.isdigit():
        logger.info(f"群[{sender.name}]({sender.id}) 触发命令 : {delete_describe[0]} uid输入不合法({uid})")
        await app.send_message(sender, MessageChain(draw_pic(f"uid输入不合法({uid})，操作失败", width=800)))
        return
    uid = int(uid)
    group = sender.id
    bot = app.account
    logger.info(f"群[{sender.name}]({sender.id}) 触发命令 : {delete_describe[0]} ({uid = }, {group = })")

    if master_qq == "" or f"{member.id}" != f"{master_qq}":
        person = await app.get_member(group, member.id)
        if person.permission < MemberPerm.Administrator:
            logger.info(
                f"群[{sender.name}]({sender.id}) 触发命令 : {delete_describe[0]} 权限不足({member.id = }, {person.permission = })")
            await app.send_message(sender,
                                   MessageChain(draw_pic("权限不足，操作失败，仅群管理员和群主可操作", width=800)))
            return
    obj_mysql = ObjMysql()
    result = await obj_mysql.check_uid_exist(uid, group)
    if not result:
        logger.info(f"群[{sender.name}]({sender.id}) 触发命令 : {delete_describe[0]} uid未被订阅({uid = })")
        await app.send_message(sender, MessageChain(draw_pic("uid未被订阅，操作失败", width=800)))
        return
    await obj_mysql.init_target(bot, uid, group)
    await obj_mysql.delete()
    uname, _ = obj_mysql.get_target_uname_and_roomid()
    logger.info(f"群[{sender.name}]({sender.id}) 触发命令 : {delete_describe[0]} 成功{uname}({uid})")
    await app.send_message(sender, MessageChain(draw_pic(f"{uname}({uid})删除订阅成功", width=800)))


@channel.use(
    ListenerSchema(
        listening_events=[FriendMessage],
        inline_dispatchers=[Twilight(
            ElementMatch(At, optional=True),
            FullMatch(prefix),
            UnionMatch(*delete_describe).space(SpacePolicy.FORCE),
            "uid" @ ParamMatch(),
            "group" @ ArgumentMatch("-g", "--group", type=int, default=0, optional=True)
        )],
    )
)
async def _DelListenFriend(app: Ariadne, sender: Friend, uid: MessageChain = ResultValue(),
                           group: Optional[int] = ResultValue()):
    if check_not_mysql_datasource():
        return
    uid = uid.display
    if uid == "" or not uid.isdigit():
        logger.info(f"好友[{sender.nickname}]({sender.id}) 触发命令 : {delete_describe[0]} uid输入不合法({uid})")
        await app.send_message(sender, MessageChain(draw_pic(f"uid输入不合法({uid})，操作失败", width=800)))
        return
    uid = int(uid)
    bot = app.account
    logger.info(f"好友[{sender.nickname}]({sender.id}) 触发命令 : {delete_describe[0]} ({uid = }, {group = })")

    if group != 0:
        if master_qq == "" or master_qq != sender.id:
            # 功能需要配置MASTER_QQ
            return
        source = group
        source_type = PushType.Group
        msg_prefix = f"群聊{group} "
    else:
        source = sender.id
        source_type = PushType.Friend
        msg_prefix = ""

    obj_mysql = ObjMysql()
    result = await obj_mysql.check_uid_exist(uid, source, source_type)
    if not result:
        logger.info(f"好友[{sender.nickname}]({sender.id}) 触发命令 : {delete_describe[0]} uid未被订阅({uid = })")
        await app.send_message(sender, MessageChain(draw_pic("uid未被订阅，操作失败", width=800)))
        return
    await obj_mysql.init_target(bot, uid, source, source_type)
    await obj_mysql.delete()
    uname, _ = obj_mysql.get_target_uname_and_roomid()
    logger.info(
        f"好友[{sender.nickname}]({sender.id}) 触发命令 : {delete_describe[0]} 成功 {msg_prefix}[{uname}]({uid})")
    await app.send_message(sender, MessageChain(draw_pic(f"{msg_prefix}{uname}({uid})删除订阅成功", width=800)))


@channel.use(
    ListenerSchema(
        listening_events=[FriendMessage],
        inline_dispatchers=[Twilight(
            ElementMatch(At, optional=True),
            FullMatch(prefix),
            UnionMatch(*trans_to_mysql)
        )],
    )
)
async def _TransToMysql(app: Ariadne, sender: Friend):
    if check_mysql_datasource():
        return
    if master_qq == "" or master_qq != sender.id:
        # 功能需要配置MASTER_QQ
        return
    logger.info(f"主人[{sender.nickname}]({sender.id}) 触发命令 : {trans_to_mysql[0]}")
    result, message = await datasource_trans_to_mysql()
    if not result:
        await app.send_message(sender, MessageChain(draw_pic(f"{trans_to_mysql[0]} 失败，原因：{message}")))
    await app.send_message(sender, MessageChain(draw_pic(f"{trans_to_mysql[0]} 成功", width=800)))


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight(
            ElementMatch(At, optional=True),
            FullMatch(prefix),
            UnionMatch(*list_describe),
            "text" @ ArgumentMatch("-t", "--text", type=str, choices=["true", "false"], default="false", optional=True),
        )],
    )
)
async def _GetUpList(app: Ariadne, sender: Group, message: MessageChain, text: Optional[str] = ResultValue()):
    if check_not_mysql_datasource():
        return
    if check_at_object(app.account, message) is False:
        return
    if text == "false":
        text_mode = False
    else:
        text_mode = True
    logger.info(f"群[{sender.name}]({sender.id}) 触发命令 : {list_describe[0]}, {text = }")
    group = sender.id
    obj_mysql = ObjMysql()
    width = 1200
    result = obj_mysql.get_ups_by_target_with_pic_struct(group, PushType.Group, width=width)
    if not result:
        result = ["未查询到订阅"]
    logger.info(f"群[{sender.name}]({sender.id}) 触发命令 : {list_describe[0]} 成功 \n{result}")
    if text_mode:
        res = "\n".join(result)
    else:
        res = draw_pic(result, width=width)
    await app.send_message(sender, MessageChain(res))


@channel.use(
    ListenerSchema(
        listening_events=[FriendMessage],
        inline_dispatchers=[Twilight(
            ElementMatch(At, optional=True),
            FullMatch(prefix),
            UnionMatch(*list_describe),
            "text" @ ArgumentMatch("-t", "--text", type=str, choices=["true", "false"], default="false", optional=True),
        )],
    )
)
async def _GetUpListAll(app: Ariadne, sender: Friend, text: Optional[str] = ResultValue()):
    if check_not_mysql_datasource():
        return
    if text == "false":
        text_mode = False
    else:
        text_mode = True
    logger.info(f"好友[{sender.nickname}]({sender.id}) 触发命令 : {list_describe[0]}, {text = }")
    obj_mysql = ObjMysql()
    width = 1200
    if master_qq == "" or master_qq != sender.id:
        result = obj_mysql.get_ups_by_target_with_pic_struct(sender.id, PushType.Friend, width=width)
    else:
        result = obj_mysql.get_up_list_with_pic_struct(width=width)
        res_temp = []
        if text_mode:
            for result_inner in result:
                res_temp.append("#" + result_inner.get("section"))
                res_temp.append(" ".join(result_inner.get("context")))
            result = res_temp
    if not result:
        result = ["未查询到订阅"]
    logger.info(f"好友[{sender.nickname}]({sender.id}) 触发命令 : {list_describe[0]} 成功 \n{result}")
    if text_mode:
        res = "\n".join(result)
    else:
        res = draw_pic(result, width=width)
    await app.send_message(sender, MessageChain(res))


@channel.use(
    ListenerSchema(
        listening_events=[FriendMessage],
        inline_dispatchers=[Twilight(
            ElementMatch(At, optional=True),
            FullMatch(prefix),
            UnionMatch(*reload_uid).space(SpacePolicy.FORCE),
            "uid" @ ParamMatch(),
        )],
    )
)
async def _ReloadUid(app: Ariadne, sender: Friend, uid: MessageChain = ResultValue()):
    if check_not_mysql_datasource():
        return
    uid = uid.display
    logger.info(f"好友[{sender.nickname}]({sender.id}) 触发命令 : {reload_uid[0]} {uid = }")
    if uid == "" or not uid.isdigit():
        logger.info(f"好友[{sender.nickname}]({sender.id}) 触发命令 : {delete_describe[0]} uid输入不合法({uid})")
        await app.send_message(sender, MessageChain(draw_pic(f"uid输入不合法({uid})，操作失败", width=800)))
        return
    uid = int(uid)
    if master_qq == "" or master_qq != sender.id:
        return
    obj_mysql = ObjMysql()
    result = await obj_mysql.check_uid_exist_with_all(uid)
    if not result:
        logger.info(f"好友[{sender.nickname}]({sender.id}) 触发命令 : {delete_describe[0]} uid未被订阅({uid = })")
        await app.send_message(sender, MessageChain(draw_pic("uid未被订阅，操作失败", width=800)))
        return
    await obj_mysql.reload(uid)
    uname, _ = await select_uname_and_room_id(uid)
    logger.info(f"群[{sender.nickname}]({sender.id}) 触发命令 : {add_logo[0]} 成功 {uname}({uid})")
    await app.send_message(sender, MessageChain(draw_pic(f"{uname}({uid}){add_logo[0]}成功", width=800)))


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight(
            ElementMatch(At, optional=True),
            FullMatch(prefix),
            UnionMatch(*add_logo).space(SpacePolicy.FORCE),
            "uid" @ ParamMatch()
        )],
    )
)
async def _SetLogoGroup(app: Ariadne, sender: Group, member: Member, message: MessageChain,
                        uid: MessageChain = ResultValue()):
    if check_not_mysql_datasource():
        return
    if check_at_object(app.account, message) is False:
        return
    uid = uid.display
    if uid == "" or not uid.isdigit():
        logger.info(f"群[{sender.name}]({sender.id}) 触发命令 : {add_logo[0]} uid输入不合法({uid})")
        await app.send_message(sender, MessageChain(draw_pic(f"uid输入不合法({uid})，操作失败", width=800)))
        return
    uid = int(uid)
    group = sender.id
    bot = app.account
    logger.info(f"群[{sender.name}]({sender.id}) 触发命令 : {add_logo[0]} {uid = } {group = })")

    if master_qq == "" or f"{member.id}" != f"{master_qq}":
        person = await app.get_member(group, member.id)
        if person.permission < MemberPerm.Administrator:
            logger.info(
                f"群[{sender.name}]({sender.id}) 触发命令 : {add_logo[0]} 权限不足({member.id = }, {person.permission = })")
            await app.send_message(sender,
                                   MessageChain(draw_pic("权限不足，操作失败，仅群管理员和群主可操作", width=800)))
            return
    obj_mysql = ObjMysql()
    result = await obj_mysql.check_uid_exist(uid, group)
    if not result:
        logger.info(f"群[{sender.name}]({sender.id}) 触发命令 : {add_logo[0]} uid未被订阅({uid = })")
        await app.send_message(sender, MessageChain(draw_pic("uid未被订阅，操作失败", width=800)))
        return
    time_out = 60
    await app.send_message(sender, MessageChain(f"请在{time_out}秒内发送立绘图片"))

    @Waiter.create_using_function([GroupMessage])
    async def words_waiter(s: Group, m: Member, msg: MessageChain):
        if sender.id == s.id and member.id == m.id:
            return msg

    try:
        ret_msg = await inc.wait(words_waiter, timeout=time_out)  # 强烈建议设置超时时间否则将可能会永远等待
    except asyncio.TimeoutError:
        result = "超时自动取消"
        logger.info(f"好友[{sender.name}]({sender.id}) 命令: {add_logo[0]} 失败 原因：{result}")
        await app.send_message(sender, MessageChain(result))
    else:
        image = None
        image_count = 0
        for element in ret_msg.content:
            if isinstance(element, Image):
                image = element
                image_count += 1
        if image is None or image_count > 1:
            result = "操作失败，请确认发送的图片数量为1"
            logger.info(f"好友[{sender.name}]({sender.id}) 命令: {add_logo[0]} 失败 原因：{result}")
            await app.send_message(sender, MessageChain(result))
            return
        await obj_mysql.init_target(bot, uid, group)
        logo_base64 = base64.b64encode(await image.get_bytes()).decode('ascii')
        obj_mysql.set_report_logo(logo_base64)
        await obj_mysql.save()
        uname, _ = obj_mysql.get_target_uname_and_roomid()
        logger.info(f"群[{sender.name}]({sender.id}) 触发命令 : {add_logo[0]} 成功 {uname}({uid})")
        await app.send_message(sender, MessageChain(draw_pic(f"{uname}({uid}){add_logo[0]}成功", width=800)))
        await app.send_message(sender, MessageChain(draw_image_pic(logo_base64, "直播报告立绘")))


@channel.use(
    ListenerSchema(
        listening_events=[FriendMessage],
        inline_dispatchers=[Twilight(
            ElementMatch(At, optional=True),
            FullMatch(prefix),
            UnionMatch(*add_logo).space(SpacePolicy.FORCE),
            "uid" @ ParamMatch(),
            "group" @ ArgumentMatch("-g", "--group", type=int, default=0, optional=True)
        )],
    )
)
async def _SetLogoFriend(app: Ariadne, sender: Friend, uid: MessageChain = ResultValue(),
                         group: Optional[int] = ResultValue()):
    if check_not_mysql_datasource():
        return
    uid = uid.display
    if uid == "" or not uid.isdigit():
        logger.info(f"好友[{sender.nickname}]({sender.id}) 触发命令 : {add_logo[0]} uid输入不合法({uid})")
        await app.send_message(sender, MessageChain(draw_pic(f"uid输入不合法({uid})，操作失败", width=800)))
        return
    uid = int(uid)
    bot = app.account
    logger.info(f"好友[{sender.nickname}]({sender.id}) 触发命令 : {add_logo[0]} ({uid = }, {group = })")

    if group != 0:
        if master_qq == "" or master_qq != sender.id:
            # 功能需要配置MASTER_QQ
            return
        source = group
        source_type = PushType.Group
        msg_prefix = f"群聊{group} "
    else:
        source = sender.id
        source_type = PushType.Friend
        msg_prefix = ""

    obj_mysql = ObjMysql()
    result = await obj_mysql.check_uid_exist(uid, source, source_type)
    if not result:
        logger.info(f"好友[{sender.nickname}]({sender.id}) 触发命令 : {add_logo[0]} uid未被订阅({uid = })")
        await app.send_message(sender, MessageChain(draw_pic("uid未被订阅，操作失败", width=800)))
        return
    time_out = 60
    await app.send_message(sender, MessageChain(f"请在{time_out}秒内发送立绘图片"))

    @Waiter.create_using_function([FriendMessage])
    async def words_waiter(s: Friend, msg: MessageChain):
        if sender.id == s.id:
            return msg

    try:
        ret_msg = await inc.wait(words_waiter, timeout=time_out)  # 强烈建议设置超时时间否则将可能会永远等待
    except asyncio.TimeoutError:
        result = "超时自动取消"
        logger.info(f"好友[{sender.nickname}]({sender.id}) 命令: {add_logo[0]} 失败 原因：{result}")
        await app.send_message(sender, MessageChain(result))
    else:
        image = None
        image_count = 0
        for element in ret_msg.content:
            if isinstance(element, Image):
                image = element
                image_count += 1
        if image is None or image_count > 1:
            result = "操作失败，请确认发送的图片数量为1"
            logger.info(f"好友[{sender.nickname}]({sender.id}) 命令: {add_logo[0]} 失败 原因：{result}")
            await app.send_message(sender, MessageChain(result))
            return
        await obj_mysql.init_target(bot, uid, source, source_type)
        logo_base64 = base64.b64encode(await image.get_bytes()).decode('ascii')
        obj_mysql.set_report_logo(logo_base64)
        await obj_mysql.save()
        uname, _ = obj_mysql.get_target_uname_and_roomid()
        logger.info(f"好友[{sender.nickname}]({sender.id}) 触发命令 : {add_logo[0]} 成功 {msg_prefix}[{uname}]({uid})")
        await app.send_message(sender,
                               MessageChain(draw_pic(f"{msg_prefix}{uname}({uid}){add_logo[0]}成功", width=800)))
        await app.send_message(sender, MessageChain(draw_image_pic(logo_base64, "直播报告立绘")))


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight(
            ElementMatch(At, optional=True),
            FullMatch(prefix),
            UnionMatch(*clear_logo).space(SpacePolicy.FORCE),
            "uid" @ ParamMatch()
        )],
    )
)
async def _ClearLogoGroup(app: Ariadne, sender: Group, member: Member, message: MessageChain,
                          uid: MessageChain = ResultValue()):
    if check_not_mysql_datasource():
        return
    if check_at_object(app.account, message) is False:
        return
    uid = uid.display
    if uid == "" or not uid.isdigit():
        logger.info(f"群[{sender.name}]({sender.id}) 触发命令 : {clear_logo[0]} uid输入不合法({uid})")
        await app.send_message(sender, MessageChain(draw_pic(f"uid输入不合法({uid})，操作失败", width=800)))
        return
    uid = int(uid)
    group = sender.id
    bot = app.account
    logger.info(f"群[{sender.name}]({sender.id}) 触发命令 : {clear_logo[0]} {uid = } {group = })")

    if master_qq == "" or f"{member.id}" != f"{master_qq}":
        person = await app.get_member(group, member.id)
        if person.permission < MemberPerm.Administrator:
            logger.info(
                f"群[{sender.name}]({sender.id}) 触发命令 : {clear_logo[0]} 权限不足({member.id = }, {person.permission = })")
            await app.send_message(sender,
                                   MessageChain(draw_pic("权限不足，操作失败，仅群管理员和群主可操作", width=800)))
            return
    obj_mysql = ObjMysql()
    result = await obj_mysql.check_uid_exist(uid, group)
    if not result:
        logger.info(f"群[{sender.name}]({sender.id}) 触发命令 : {clear_logo[0]} uid未被订阅({uid = })")
        await app.send_message(sender, MessageChain(draw_pic("uid未被订阅，操作失败", width=800)))
        return
    await obj_mysql.init_target(bot, uid, group)
    obj_mysql.clear_report_logo()
    await obj_mysql.save()
    uname, _ = obj_mysql.get_target_uname_and_roomid()
    logger.info(f"群[{sender.name}]({sender.id}) 触发命令 : {clear_logo[0]} 成功{uname}({uid})")
    await app.send_message(sender, MessageChain(draw_pic(f"{uname}({uid}){clear_logo[0]}成功", width=800)))


@channel.use(
    ListenerSchema(
        listening_events=[FriendMessage],
        inline_dispatchers=[Twilight(
            ElementMatch(At, optional=True),
            FullMatch(prefix),
            UnionMatch(*clear_logo).space(SpacePolicy.FORCE),
            "uid" @ ParamMatch(),
            "group" @ ArgumentMatch("-g", "--group", type=int, default=0, optional=True)
        )],
    )
)
async def _ClearLogoFriend(app: Ariadne, sender: Friend, uid: MessageChain = ResultValue(),
                           group: Optional[int] = ResultValue()):
    if check_not_mysql_datasource():
        return
    uid = uid.display
    if uid == "" or not uid.isdigit():
        logger.info(f"好友[{sender.nickname}]({sender.id}) 触发命令 : {clear_logo[0]} uid输入不合法({uid})")
        await app.send_message(sender, MessageChain(draw_pic(f"uid输入不合法({uid})，操作失败", width=800)))
        return
    uid = int(uid)
    bot = app.account
    logger.info(f"好友[{sender.nickname}]({sender.id}) 触发命令 : {clear_logo[0]} ({uid = }, {group = })")
    if group != 0:
        if master_qq == "" or master_qq != sender.id:
            # 功能需要配置MASTER_QQ
            return
        source = group
        source_type = PushType.Group
        msg_prefix = f"群聊{group} "
    else:
        source = sender.id
        source_type = PushType.Friend
        msg_prefix = ""
    obj_mysql = ObjMysql()
    result = await obj_mysql.check_uid_exist(uid, source, source_type)
    if not result:
        logger.info(f"好友[{sender.nickname}]({sender.id}) 触发命令 : {clear_logo[0]} uid未被订阅({uid = })")
        await app.send_message(sender, MessageChain(draw_pic("uid未被订阅，操作失败", width=800)))
        return
    await obj_mysql.init_target(bot, uid, source, source_type)
    obj_mysql.clear_report_logo()
    await obj_mysql.save()
    uname, _ = obj_mysql.get_target_uname_and_roomid()
    logger.info(f"好友[{sender.nickname}]({sender.id}) 触发命令 : {clear_logo[0]} 成功 {msg_prefix}[{uname}]({uid})")
    await app.send_message(sender, MessageChain(draw_pic(f"{msg_prefix}{uname}({uid}){clear_logo[0]}成功", width=800)))


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight(
            ElementMatch(At, optional=True),
            FullMatch(prefix),
            UnionMatch(*set_message).space(SpacePolicy.FORCE),
            "uid" @ ParamMatch(),
            "message_type" @ ArgumentMatch("-t", "--type", type=str, choices=["news", "live_on", "live_off"]),
        )],
    )
)
async def _SetMessageGroup(app: Ariadne, sender: Group, member: Member, message: MessageChain,
                           uid: MessageChain = ResultValue(), message_type: Optional[str] = ResultValue()):
    if check_not_mysql_datasource():
        return
    if check_at_object(app.account, message) is False:
        return
    uid = uid.display
    if uid == "" or not uid.isdigit():
        logger.info(f"群[{sender.name}]({sender.id}) 触发命令 : {set_message[0]} uid输入不合法({uid})")
        await app.send_message(sender, MessageChain(draw_pic(f"uid输入不合法({uid})，操作失败", width=800)))
        return
    uid = int(uid)
    group = sender.id
    bot = app.account
    logger.info(f"群[{sender.name}]({sender.id}) 触发命令 : {set_message[0]} {uid = } {group = } {message_type = })")

    if master_qq == "" or f"{member.id}" != f"{master_qq}":
        person = await app.get_member(group, member.id)
        if person.permission < MemberPerm.Administrator:
            logger.info(
                f"群[{sender.name}]({sender.id}) 触发命令 : {set_message[0]} 权限不足({member.id = }, {person.permission = })")
            await app.send_message(sender,
                                   MessageChain(draw_pic("权限不足，操作失败，仅群管理员和群主可操作", width=800)))
            return
    obj_mysql = ObjMysql()
    result = await obj_mysql.check_uid_exist(uid, group)
    if not result:
        logger.info(f"群[{sender.name}]({sender.id}) 触发命令 : {set_message[0]} uid未被订阅({uid = })")
        await app.send_message(sender, MessageChain(draw_pic("uid未被订阅，操作失败", width=800)))
        return
    timeout_s = 600
    await app.send_message(sender, MessageChain(get_message_help(message_type) + f"\nat元素和图片能够被正确识别\n请在{timeout_s}秒内发送内容:"))

    @Waiter.create_using_function([GroupMessage])
    async def words_waiter(s: Group, m: Member, msg: MessageChain):
        if sender.id == s.id and member.id == m.id:
            return msg

    try:
        ret_msg = await inc.wait(words_waiter, timeout=timeout_s)  # 强烈建议设置超时时间否则将可能会永远等待
    except asyncio.TimeoutError:
        result = "超时自动取消"
        logger.info(f"群[{sender.name}]({sender.id}) 命令: {set_message[0]} 失败 原因：{result}")
        await app.send_message(sender, MessageChain(result))
    else:
        msg = ""
        for element in ret_msg.content:
            if isinstance(element, Image):
                msg += "{base64pic=" + base64.b64encode(await element.get_bytes()).decode('ascii') + "}"
            if isinstance(element, At):
                msg += "{at" + f"{element.target}" + "}"
            if isinstance(element, AtAll):
                msg += "{atall}"
            if isinstance(element, Plain):
                msg += element.text
        await obj_mysql.init_target(bot, uid, group)
        obj_mysql.set_message_inner(message_type, msg)
        await obj_mysql.save()
        uname, _ = obj_mysql.get_target_uname_and_roomid()
        logger.info(f"群[{sender.name}]({sender.id}) 触发命令 : {set_message[0]} 成功 {uname}({uid})")
        await app.send_message(sender, MessageChain(draw_pic(f"{uname}({uid}){set_message[0]}成功", width=800)))


@channel.use(
    ListenerSchema(
        listening_events=[FriendMessage],
        inline_dispatchers=[Twilight(
            ElementMatch(At, optional=True),
            FullMatch(prefix),
            UnionMatch(*set_message).space(SpacePolicy.FORCE),
            "uid" @ ParamMatch(),
            "message_type" @ ArgumentMatch("-t", "--type", type=str, choices=["news", "live_on", "live_off"]),
            "group" @ ArgumentMatch("-g", "--group", type=int, default=0, optional=True)
        )],
    )
)
async def _SetMessageFriend(app: Ariadne, sender: Friend, uid: MessageChain = ResultValue(),
                            message_type: Optional[str] = ResultValue(), group: Optional[int] = ResultValue()):
    if check_not_mysql_datasource():
        return
    uid = uid.display
    if uid == "" or not uid.isdigit():
        logger.info(f"好友[{sender.nickname}]({sender.id}) 触发命令 : {set_message[0]} uid输入不合法({uid})")
        await app.send_message(sender, MessageChain(draw_pic(f"uid输入不合法({uid})，操作失败", width=800)))
        return
    uid = int(uid)
    bot = app.account
    logger.info(f"好友[{sender.nickname}]({sender.id}) 触发命令 : {set_message[0]} ({uid = }, {group = })")

    if group != 0:
        if master_qq == "" or master_qq != sender.id:
            # 功能需要配置MASTER_QQ
            return
        source = group
        source_type = PushType.Group
        msg_prefix = f"群聊{group} "
    else:
        source = sender.id
        source_type = PushType.Friend
        msg_prefix = ""

    obj_mysql = ObjMysql()
    result = await obj_mysql.check_uid_exist(uid, source, source_type)
    if not result:
        logger.info(f"好友[{sender.nickname}]({sender.id}) 触发命令 : {set_message[0]} uid未被订阅({uid = })")
        await app.send_message(sender, MessageChain(draw_pic("uid未被订阅，操作失败", width=800)))
        return
    timeout_s = 600
    await app.send_message(sender, MessageChain(get_message_help(message_type) + f"\n图片能够被正确识别\n请在{timeout_s}秒内发送内容:"))

    @Waiter.create_using_function([FriendMessage])
    async def words_waiter(s: Friend, msg: MessageChain):
        if sender.id == s.id:
            return msg

    try:
        ret_msg = await inc.wait(words_waiter, timeout=60)  # 强烈建议设置超时时间否则将可能会永远等待
    except asyncio.TimeoutError:
        result = "超时自动取消"
        logger.info(f"好友[{sender.nickname}]({sender.id}) 命令: {set_message[0]} 失败 原因：{result}")
        await app.send_message(sender, MessageChain(result))
    else:
        msg = ""
        for element in ret_msg.content:
            if isinstance(element, Image):
                msg += "{base64pic=" + base64.b64encode(await element.get_bytes()).decode('ascii') + "}"
            if isinstance(element, Plain):
                msg += element.text
        await obj_mysql.init_target(bot, uid, group)
        obj_mysql.set_message_inner(message_type, msg)
        await obj_mysql.save()
        uname, _ = obj_mysql.get_target_uname_and_roomid()
        logger.info(
            f"好友[{sender.nickname}]({sender.id}) 触发命令 : {set_message[0]} 成功 {msg_prefix}[{uname}]({uid})")
        await app.send_message(sender,
                               MessageChain(draw_pic(f"{msg_prefix}{uname}({uid}){set_message[0]}成功", width=800)))


@channel.use(
    ListenerSchema(
        listening_events=[FriendMessage],
        inline_dispatchers=[Twilight(
            ElementMatch(At, optional=True),
            FullMatch(prefix),
            UnionMatch(*check_describe_abnormal)
        )],
    )
)
async def _CheckDescribeAbnormal(app: Ariadne, sender: Friend):
    if check_not_mysql_datasource():
        return
    if master_qq == "" or master_qq != sender.id:
        # 功能需要配置MASTER_QQ
        return
    logger.info(f"好友[{sender.nickname}]({sender.id}) 触发命令 : {check_describe_abnormal[0]}")
    obj_mysql = ObjMysql()
    group_set, friend_set = obj_mysql.get_all_groups_and_friends()
    bot_group_list: List[Group] = await app.get_group_list()
    bot_group_set = {x.id for x in bot_group_list}
    bot_friend_list: List[Friend] = await app.get_friend_list()
    bot_friend_set = {x.id for x in bot_friend_list}
    group_abnormal_describe = group_set - bot_group_set
    friend_abnormal_describe = friend_set - bot_friend_set
    if len(group_abnormal_describe) < 1 or len(friend_abnormal_describe) < 1:
        result = "无异常订阅"
        logger.info(f"好友[{sender.nickname}]({sender.id}) 触发命令 : {check_describe_abnormal[0]} 成功 \n{result}")
        image = draw_pic(result)
        await app.send_message(sender, MessageChain(image))
        return
    abnormal_list = []
    if len(group_abnormal_describe) > 1:
        group_abnormal = {"section": "异常订阅群号", "context": list(group_abnormal_describe)}
        abnormal_list.append(group_abnormal)
    if len(friend_abnormal_describe) > 1:
        friend_abnormal = {"section": "异常订阅好友", "context": list(friend_abnormal_describe)}
        abnormal_list.append(friend_abnormal)
    result = f"异常订阅群号: {group_abnormal_describe}\n异常订阅好友: {friend_abnormal_describe}"
    logger.info(f"好友[{sender.nickname}]({sender.id}) 触发命令 : {check_describe_abnormal[0]} 成功 \n{result}")
    image = draw_pic(abnormal_list)
    await app.send_message(sender, MessageChain(image))


@channel.use(
    ListenerSchema(
        listening_events=[FriendMessage],
        inline_dispatchers=[Twilight(
            ElementMatch(At, optional=True),
            FullMatch(prefix),
            UnionMatch(*clear_describe_abnormal)
        )],
    )
)
async def _ClearDescribeAbnormal(app: Ariadne, sender: Friend):
    if check_not_mysql_datasource():
        return
    if master_qq == "" or master_qq != sender.id:
        # 功能需要配置MASTER_QQ
        return
    logger.info(f"好友[{sender.nickname}]({sender.id}) 触发命令 : {clear_describe_abnormal[0]}")
    obj_mysql = ObjMysql()
    group_set, friend_set = obj_mysql.get_all_groups_and_friends()
    bot_group_list: List[Group] = await app.get_group_list()
    bot_group_set = {x.id for x in bot_group_list}
    bot_friend_list: List[Friend] = await app.get_friend_list()
    bot_friend_set = {x.id for x in bot_friend_list}
    group_abnormal_describe = group_set - bot_group_set
    friend_abnormal_describe = friend_set - bot_friend_set
    if len(group_abnormal_describe) < 1 or len(friend_abnormal_describe) < 1:
        result = "无异常订阅"
        logger.info(f"好友[{sender.nickname}]({sender.id}) 触发命令 : {check_describe_abnormal[0]} 成功 \n{result}")
        image = draw_pic(result)
        await app.send_message(sender, MessageChain(image))
        return
    abnormal_list = []
    if len(group_abnormal_describe) > 1:
        group_abnormal = {"section": "清除异常订阅群号", "context": list(group_abnormal_describe)}
        abnormal_list.append(group_abnormal)
    if len(friend_abnormal_describe) > 1:
        friend_abnormal = {"section": "清除异常订阅好友", "context": list(friend_abnormal_describe)}
        abnormal_list.append(friend_abnormal)
    bot = app.account
    up_list = obj_mysql.get_ups_by_targets(friend_abnormal_describe, group_abnormal_describe)
    for up in up_list:
        obj_mysql = ObjMysql()
        await obj_mysql.init_target(bot, up[0], up[1])
        await obj_mysql.delete()
    result = f"清除异常订阅群号: {group_abnormal_describe}\n清除异常订阅好友: {friend_abnormal_describe}"
    logger.info(f"好友[{sender.nickname}]({sender.id}) 触发命令 : {check_describe_abnormal[0]} 成功 \n{result}")
    abnormal_list.append("清除异常订阅成功")
    image = draw_pic(abnormal_list)
    await app.send_message(sender, MessageChain(image))


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage, FriendMessage],
        inline_dispatchers=[Twilight(
            ElementMatch(At, optional=True),
            FullMatch(prefix),
            UnionMatch(*help_cmd)
        )],
    )
)
async def _MysqlHelp(app: Ariadne, sender: Union[Friend, Group], message: MessageChain):
    if check_not_mysql_datasource():
        return
    if check_at_object(app.account, message) is False:
        return
    if isinstance(sender, Group):
        log_type = "群"
        context_type = "describe_group"
        help_cmd_sub_title = "群聊命令帮助"
    else:
        if master_qq == sender.id:
            log_type = "主人"
            context_type = "describe_admin"
            help_cmd_sub_title = "主人命令帮助"
        else:
            log_type = "好友"
            context_type = "describe_friend"
            help_cmd_sub_title = "私聊命令帮助"

    logger.info(f"{log_type}[{sender.id}] 触发命令 : {help_cmd[0]}")
    pic_context = []
    for key, value in describe_cmd.items():
        # 组装绘图结构
        if len(value.get(context_type)) > 0:
            cmd = {
                "section": key,
                "context": value.get(context_type)
            }
            pic_context.append(cmd)
    image = draw_pic(pic_context, help_cmd[0], help_cmd_sub_title, width=1500)
    await app.send_message(sender, MessageChain(image))
