# starbot-mysql-plugins

#### 介绍
starbot自定义命令包，包含如下功能

1. 递归加载plugins下的所有文件，报错则打印日志并跳过（需要配置MASTER_QQ）
2. 拉群自动通过（需要配置MASTER_QQ）
3. 好友申请自动通过（需要配置MASTER_QQ）
4. mysql数据源下的机器人的动态订阅功能和当前内存数据源到mysql的转储能力

当前版本 v1.0.3

#### 更新日志

2025年1月17日：

1. mysql数据源将text替换为longtext,原因是text不足以容纳base64字符串长度
2. 完善了setmessage命令的功能，现在他能正确识别图片和at元素并替换成相应占位符了

2025年1月19日：
1. 设置版本号以方便进行版本更新
2. 统一使用命令交互进行设置立绘，并同步了setlogo的相关帮助

2025年1月21日：
1. 更新版本v1.0.1
2. 优化了setmessage的帮助信息，增加了等待超时时间(60s -> 600s)
3. 修正了transdatasource的帮助信息，数据源转换功能不局限于json数据源，可以是任意不为mysql的数据源
4. 增强了list功能，现在能展示对应订阅信息的具体订阅内容，如动态，开播和下播

2025年2月1日：
1. 更新版本v1.0.2
2. 新增quit指令，bot主人私聊和群聊可用，作用为退出群聊并清除订阅

2025年2月15日：
1. 更新版本v1.0.3
2. 增强命令可用性，命令“设置推送信息”增加触发“设置推送消息”，命令“退出群聊”增加触发“退群”
3. 命令交互场景增加了取消功能，发送取消即可取消操作
4. 修正部分日志打印

#### 软件架构
通过plugins目录下的__init__.py使用require导入内部所有插件包

#### 安装教程

将目录置于starbot的启动文件位置，添加config.set("CUSTOM_COMMANDS_PACKAGE", "plugins")即可

功能依赖MASTER_QQ配置项，需要添加config.set("MASTER_QQ", qq号)，例如config.set("MASTER_QQ", 123456)

部分功能需要starbot启用mysql数据源而并非使用json数据源，需要配置对应config.set("MYSQL_HOST", "mysqladdr") config.set("MYSQL_USERNAME", "username") config.set("MYSQL_PASSWORD", "password"),并且通过datasource = MySQLDataSource()启用mysql数据源 _[而不要使用datasource = JsonDataSource("推送配置.json")]_ 

数据源转储功能仅当非mysql数据源生效，仍需要配置对应config.set("MYSQL_HOST", "mysqladdr") config.set("MYSQL_USERNAME", "username") 以写入mysql数据库

根目录__init__.py递归加载全部不为_开头的文件夹及内部.py文件，只需要放置相应插件即可被导入

#### 使用说明

可以新增插件，放入plugins文件夹中并重启starbot，即可被自动导入

mysql默认数据库为starbot，内部表结构自行执行starbot.sql生成

以下命令自行增加config配置的命令前缀

帮助： 订阅帮助


主人命令示例：
![5cc31543a624c7440342b9aa2b9fb6f9](https://github.com/user-attachments/assets/58dacea6-f7b1-45ef-aaeb-0e204a9716c3)


群聊命令示例：
![79137602d6f3ecfc1df14a7f02c9abda_720](https://github.com/user-attachments/assets/bc9d34e0-8925-4a40-b20f-55fc36b2349a)


私聊命令示例：
![23f96861c0b397cb7955b5d2d3257b31_720](https://github.com/user-attachments/assets/b3f618f5-cba2-48bf-bcdf-2c6413376220)


加好友自动同意并发送指引：
![5d0be45ff8ab8f7e6230551a7453cd58](https://github.com/user-attachments/assets/40a4eb6d-5d37-46e7-a7bb-385dbf4fae91)


#### 引用

starbot项目地址 https://github.com/Starlwr/StarBot

命令参考ddbot https://github.com/cnxysoft/DDBOT-WSa/

增加插件重载功能的魔改版starbot https://github.com/HanamiSeishin/StarBot


#### 其他说明

作者作为曾经ddbot的使用者编写该starbot插件，目的是增强starbot功能，因此该仓库下的所有插件均可在starbot原仓库下使用

该插件的部署需要一定代码基础和运维技巧的支撑，若没有能力，请使用官方文档推荐的json数据源进行部署

插件仅在linux平台进行了测试，理论无平台相关性，但不确保不出问题

插件相关问题可以加入starbot官方群聊【推送姬の通知群（799915082）】，请注意提问技巧，部署相关问题请靠自己能力解决
