# starbot-mysql-plugins

#### 介绍
starbot自定义命令包，包含如下功能

1. 递归加载plugins下的所有文件，报错则打印日志并跳过，配合魔改版starbot可实现热更新插件（需要配置MASTER_QQ）
2. 拉群自动通过（需要配置MASTER_QQ）
3. 好友申请自动通过（需要配置MASTER_QQ）
4. mysql数据源下的机器人的动态订阅功能和当前内存数据源到mysql的转储能力

#### 更新日志

2025年1月17日：

1. mysql数据源将text替换为longtext,原因是text不足以容纳base64字符串长度
2. 完善了setmessage命令的功能，现在他能正确识别图片和at元素并替换成相应占位符了

#### 软件架构
通过plugins目录下的__init__.py使用require导入内部所有插件包

#### 安装教程

将目录置于starbot的启动文件位置，添加config.set("CUSTOM_COMMANDS_PACKAGE", "plugins")即可

部分功能依赖MASTER_QQ配置项，需要添加config.set("MASTER_QQ", qq号)，例如config.set("MASTER_QQ", 123456)

部分功能需要starbot启用mysql数据源而并非使用json数据源，需要配置对应config.set("MYSQL_HOST", "mysqladdr") config.set("MYSQL_USERNAME", "username") config.set("MYSQL_PASSWORD", "password"),并且通过datasource = MySQLDataSource()启用mysql数据源 _[而不要使用datasource = JsonDataSource("推送配置.json")]_ 

数据源转储功能仅当非mysql数据源生效，仍需要配置对应config.set("MYSQL_HOST", "mysqladdr") config.set("MYSQL_USERNAME", "username") 以写入mysql数据库

根目录__init__.py递归加载全部不为_开头的文件夹及内部.py文件，只需要放置相应插件即可被导入

#### 使用说明

可以新增插件，放入plugins，配置好__init__.py，即可自动加载

mysql默认数据库为starbot，内部表结构自行执行starbot.sql生成

以下命令自行增加config配置的前缀
帮助： 订阅帮助
主人命令示例：
![8c9023c182772defb345f6106e0952bd](https://github.com/user-attachments/assets/13b6b60c-3825-4d16-9b46-07798d497dd1)

群聊命令示例：
![da6d61b11213af40825242d800633566_720](https://github.com/user-attachments/assets/941ff9c0-3ced-4248-8356-24f4f0cb0a49)

私聊命令示例：
![d2494b048a0b7409f8ec5516748e006a_720](https://github.com/user-attachments/assets/53dd0334-0acc-4f5f-a728-e6d86aa07144)

加好友自动同意并发送指引：
![baf125ee1fb7c7ceb5a03e8d8dd6b087](https://github.com/user-attachments/assets/429d9850-382b-4f7c-8a51-8ffde0dbbe26)


#### 引用

starbot项目地址 https://github.com/Starlwr/StarBot

命令参考ddbot https://github.com/cnxysoft/DDBOT-WSa/

增加插件重载功能的魔改版starbot https://github.com/HanamiSeishin/StarBot
