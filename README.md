# starbot-mysql-plugins

#### 介绍
starbot自定义命令包，包含如下功能

1. 递归加载plugins下的所有文件，报错则打印日志并跳过，配合魔改版starbot可实现热更新插件（需要配置MASTER_QQ）
2. 拉群自动通过（需要配置MASTER_QQ）
3. 好友申请自动通过（需要配置MASTER_QQ）
4. mysql数据源下的机器人的动态订阅功能和当前内存数据源到mysql的转储能力

当前版本 v1.0.1

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
![9863cae698b9182e86aef0aab0f90be4](https://github.com/user-attachments/assets/9a326c3b-273d-4209-b3db-8a2a7b554b7f)


群聊命令示例：
![ad6ab2d42ad373e6b665de9fedf9b359_720](https://github.com/user-attachments/assets/3dd9b774-b3be-49b8-916b-bd482762078b)


私聊命令示例：
![5b9fecf0c7bb96fe39dc507182d2fbfb](https://github.com/user-attachments/assets/e2cf7b53-7e55-42bf-bf69-20c599bdd4cf)


加好友自动同意并发送指引：
![baf125ee1fb7c7ceb5a03e8d8dd6b087](https://github.com/user-attachments/assets/429d9850-382b-4f7c-8a51-8ffde0dbbe26)


#### 引用

starbot项目地址 https://github.com/Starlwr/StarBot

命令参考ddbot https://github.com/cnxysoft/DDBOT-WSa/

增加插件重载功能的魔改版starbot https://github.com/HanamiSeishin/StarBot


#### 其他说明

作者作为曾经ddbot的使用者编写该starbot插件，目的是增强starbot功能，因此该仓库下的所有插件均可在starbot原仓库下使用

该插件的部署需要一定代码基础和运维技巧的支撑，若没有能力，请使用官方文档推荐的json数据源进行部署

插件仅在linux平台进行了测试，理论无平台相关性，但不确保不出问题

插件相关问题可以加入starbot官方群聊【推送姬の通知群（799915082）】，请注意提问技巧，部署相关问题请靠自己能力解决
