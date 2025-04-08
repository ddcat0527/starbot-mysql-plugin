# starbot-mysql-plugins

#### 数据库初始化工具使用帮助
执行命令
```shell
python mysql_init.py --help
```
得到如下帮助文档
```shell
usage: mysql_init.py [-h] --qq QQ [--host HOST] [--user USER] [--password PASSWORD] [--port PORT] [--database DATABASE] [--onlystruct]

starbot_mysql_plugin数据库初始化工具

options:
  -h, --help           show this help message and exit
  --qq QQ              qq号[必填]
  --host HOST          mysql host[默认127.0.0.1]
  --user USER          mysql username[默认root]
  --password PASSWORD  mysql password[默认123456]
  --port PORT          mysql port[默认3306]
  --database DATABASE  mysql db[默认starbot]
  --onlystruct         mysql仅初始化结构
```

mysql数据库需要用户自行部署完成


#### 全新启动帮助

**以下操作预设qq号为123456789，mysql数据源密码为root123456**

如果你是starbot新用户，没有已有订阅信息，搭载本插件会遇到一个已知问题场景：空mysql订阅信息下，starbot将无法启动

此时可以通过如下命令初始化mysql：

```shell
python mysql_init.py --qq 123456789 --password root123456
```

该操作将以密码为root123456的root用户连接本地mysql服务器，创建名为starbot的数据库，并在该数据库内写入starbot所需的所有表结构并内置一条无用数据以供starbot启动，启动后可以通过插件命令进行操作，请务必确保订阅信息大于一条

~~订阅信息为starbot开发者姬姬的uid和推送姬の通知群（799915082），仅用于规避starbot启动问题，不产生任何推送~~

具体main.py文件请参考代码仓内的main.py文件


#### 数据源迁移帮助

**以下操作预设qq号为123456789，mysql数据源密码为root123456**

如果你是其他数据源用户（通常为json数据源）想要使用本插件并切换到mysql数据源
请使用如下命令初始化mysql：

```shell
python mysql_init.py --qq 123456789 --password root123456 --onlystruct
```

该操作将以密码为root123456的root用户连接本地mysql服务器，创建名为starbot的数据库，并在该数据库内写入starbot所需的所有表结构但不内置数据

然后将该仓库plugins目录拷贝到已有main.py文件，在main.py内添加以下配置项

```shell
config.set("MASTER_QQ", 123456789) # 设置starbot超级权限用户，没有设置过则需要设置
config.set("CUSTOM_COMMANDS_PACKAGE", "plugins") # 加载自定义插件包
config.set("MYSQL_HOST", "127.0.0.1") # mysql链接信息的mysql地址
config.set("MYSQL_USERNAME", "root") # mysql链接信息的mysql用户名
config.set("MYSQL_PASSWORD", "root123456") # mysql链接信息的mysql密码
```

然后继续使用原有数据源启动，启动完毕后，使用starbot超级权限用户对bot使用命令“数据源转储”，注意自行增加配置的命令前缀
bot接收到该命令，会将内存中的所有订阅信息，根据配置项的链接信息，写入mysql数据库

该命令执行需要一段时间，根据原数据源的数量、网络通信速度以及设备运行速度有关，请耐心等待，完成后会回复“数据源转储成功”

该操作完成后，停止starbot运行，然后修改main.py数据源启动：

```shell
...
from starbot.core.datasource import JsonDataSource
...
config.set("MASTER_QQ", 123456789) # 设置starbot超级权限用户，没有设置过则需要设置
config.set("CUSTOM_COMMANDS_PACKAGE", "plugins") # 加载自定义插件包
config.set("MYSQL_HOST", "127.0.0.1") # mysql链接信息的mysql地址
config.set("MYSQL_USERNAME", "root") # mysql链接信息的mysql用户名
config.set("MYSQL_PASSWORD", "root123456") # mysql链接信息的mysql密码
...
datasource = JsonDataSource("推送配置.json")
bot = StarBot(datasource)
```

修改为

```shell
...
from starbot.core.datasource import JsonDataSource, MySQLDataSource
...
config.set("MASTER_QQ", 123456789) # 设置starbot超级权限用户，没有设置过则需要设置
config.set("CUSTOM_COMMANDS_PACKAGE", "plugins") # 加载自定义插件包
config.set("MYSQL_HOST", "127.0.0.1") # mysql链接信息的mysql地址
config.set("MYSQL_USERNAME", "root") # mysql链接信息的mysql用户名
config.set("MYSQL_PASSWORD", "root123456") # mysql链接信息的mysql密码
...
#datasource = JsonDataSource("推送配置.json")
datasource = MySQLDataSource()
bot = StarBot(datasource)
```

正常启动starbot即可


#### 使用插件

预设命令前缀为“/”

发送“/help”或“/帮助”则返回插件帮助，插件帮助已覆盖bot原始帮助，通过添加“-d”或“--default”来呼出原始命令帮助

如果需要增加图片版权信息，请fork代码仓或者本地自行修改代码，原始版权信息请务必保留

普通绘图函数：mysql_utils.py -> draw_pic
logo绘图函数：mysql_utils.py -> draw_image_pic
帮助绘图函数：mysql_utils.py -> default_help （默认帮助，取自starbot.commands.builtin.help，可以根据需要自行修改）