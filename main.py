from starbot.core.bot import StarBot
from starbot.core.datasource import JsonDataSource, MySQLDataSource
from starbot.utils import config

config.set("MYSQL_USERNAME", your_mysql_username) # 替换成你的mysql username
config.set("MYSQL_PASSWORD", your_mysql_password) # 替换成你的mysql password
config.set("MASTER_QQ", your_qq_number) # 替换成你的qq号
config.set("COMMAND_PREFIX", "/")
config.set("CUSTOM_COMMANDS_PACKAGE", "plugins") # 载入自定义命令集
config.set("ONLY_CONNECT_NECESSARY_ROOM", True)
config.set("ONLY_HANDLE_NECESSARY_EVENT", True)

#datasource = JsonDataSource("推送配置.json")
datasource = MySQLDataSource()
bot = StarBot(datasource)
bot.run()
