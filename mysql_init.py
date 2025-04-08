import asyncio
import aiomysql
import argparse

starbot_sql = """
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS `bot`;
CREATE TABLE `bot`  (
  `id` bigint(0) NOT NULL AUTO_INCREMENT,
  `bot` bigint(0) NULL DEFAULT NULL,
  `uid` bigint(0) NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 12 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;
DROP TABLE IF EXISTS `dynamic_update`;
CREATE TABLE `dynamic_update`  (
  `id` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `uid` bigint(0) NOT NULL COMMENT 'B站id',
  `enabled` tinyint(1) NULL DEFAULT NULL,
  `message` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;
DROP TABLE IF EXISTS `live_off`;
CREATE TABLE `live_off`  (
  `id` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `uid` bigint(0) NOT NULL COMMENT 'B站id',
  `enabled` tinyint(1) NULL DEFAULT NULL,
  `message` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;
DROP TABLE IF EXISTS `live_on`;
CREATE TABLE `live_on`  (
  `id` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `uid` bigint(0) NOT NULL COMMENT 'B站id',
  `enabled` tinyint(1) NULL DEFAULT NULL,
  `message` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;
DROP TABLE IF EXISTS `live_report`;
CREATE TABLE `live_report`  (
  `id` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `uid` bigint(0) NOT NULL COMMENT 'b站id',
  `enabled` tinyint(1) NULL DEFAULT NULL,
  `logo` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `logo_base64` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `time` tinyint(1) NULL DEFAULT NULL,
  `fans_change` tinyint(1) NULL DEFAULT NULL,
  `fans_medal_change` tinyint(1) NULL DEFAULT NULL,
  `guard_change` tinyint(1) NULL DEFAULT NULL,
  `danmu` tinyint(1) NULL DEFAULT NULL,
  `box` tinyint(1) NULL DEFAULT NULL,
  `gift` tinyint(1) NULL DEFAULT NULL,
  `sc` tinyint(1) NULL DEFAULT NULL,
  `guard` tinyint(1) NULL DEFAULT NULL,
  `danmu_ranking` int(0) NULL DEFAULT NULL,
  `box_ranking` int(0) NULL DEFAULT NULL,
  `box_profit_ranking` int(0) NULL DEFAULT NULL,
  `gift_ranking` int(0) NULL DEFAULT NULL,
  `sc_ranking` int(0) NULL DEFAULT NULL,
  `guard_list` tinyint(1) NULL DEFAULT NULL,
  `box_profit_diagram` tinyint(1) NULL DEFAULT NULL,
  `danmu_diagram` tinyint(1) NULL DEFAULT NULL,
  `box_diagram` tinyint(1) NULL DEFAULT NULL,
  `gift_diagram` tinyint(1) NULL DEFAULT NULL,
  `sc_diagram` tinyint(1) NULL DEFAULT NULL,
  `guard_diagram` tinyint(1) NULL DEFAULT NULL,
  `danmu_cloud` tinyint(1) NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;
DROP TABLE IF EXISTS `targets`;
CREATE TABLE `targets`  (
  `id` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `uid` bigint(0) NOT NULL COMMENT 'B站id',
  `num` bigint(0) NULL DEFAULT NULL COMMENT '需要推送的推送目标 QQ 号或群号',
  `type` int(10) UNSIGNED ZEROFILL NULL DEFAULT NULL COMMENT '推送类型，0 为私聊推送，1 为群聊推送',
  `uname` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `room_id` bigint(0) NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;
SET FOREIGN_KEY_CHECKS = 1;
"""

async def create_database(db_config):
    """创建数据库"""
    conn = await aiomysql.connect(
        host=db_config["host"],
        port=db_config["port"],
        user=db_config["user"],
        password=db_config["password"]
    )

    async with conn.cursor() as cursor:
        try:
            await cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS {db_config['db']} "
                f"DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            print(f"Database {db_config['db']} created")
        except aiomysql.Error as e:
            print(f"Error creating database: {e}")
        finally:
            conn.close()


async def execute_sql(db_config, starbot_sql):
    """执行SQL文件"""
    try:
        # 连接到目标数据库
        conn = await aiomysql.connect(
            host=db_config["host"],
            port=db_config["port"],
            user=db_config["user"],
            password=db_config["password"],
            db=db_config["db"]
        )

        # 分割SQL语句（简单分号分割，实际需要更复杂的解析）
        statements = [stmt.strip() for stmt in starbot_sql.split(';') if stmt.strip()]

        async with conn.cursor() as cursor:
            for stmt in statements:
                if stmt.upper().startswith("DELIMITER"):
                    continue  # 跳过DELIMITER指令
                try:
                    await cursor.execute(stmt)
                    print(f"Executed: {stmt[:50]}...")  # 显示前50个字符
                except aiomysql.Error as e:
                    print(f"Error executing statement: {e}\nStatement: {stmt}")
                    raise
            await conn.commit()
    except Exception as e:
        print(f"Error executing SQL file: {e}")
    finally:
        conn.close()



async def main(args):
    db_config = {
        "host": f"{args.host}",
        "port": args.port,
        "user": f"{args.user}",
        "password": f"{args.password}",
        "db": f"{args.database}",
        "autocommit": True
    }
    insert_sql = f"""
    INSERT INTO `bot` VALUES (1, {args.qq}, 180864557);
    INSERT INTO `dynamic_update` VALUES ('00000000-0000-0000-0000-000000000000', 180864557, 0, '冷月丶残星丶发送了动态');
    INSERT INTO `live_off` VALUES ('00000000-0000-0000-0000-000000000000', 180864557, 0, '冷月丶残星丶直播结束了');
    INSERT INTO `live_on` VALUES ('00000000-0000-0000-0000-000000000000', 180864557, 0, '冷月丶残星丶正在直播');
    INSERT INTO `live_report` VALUES ('00000000-0000-0000-0000-000000000000', 180864557, 0, '', '', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);
    INSERT INTO `targets` VALUES ('00000000-0000-0000-0000-000000000000', 180864557, 799915082, 0000000001, '冷月丶残星丶', 7260744);
    """
    if not args.onlystruct and args.qq == 0:
        print("需要QQ号，请添加--qq参数指定qq号，例如--qq 123456789")
        exit()
    await create_database(db_config)
    await execute_sql(db_config, starbot_sql)
    if not args.onlystruct:
        await execute_sql(db_config, insert_sql)
    exit()


if __name__ == "__main__":
    # 创建参数解析器
    parser = argparse.ArgumentParser(description="starbot_mysql_plugin数据库初始化工具")
    parser.add_argument("--qq", type=int, help="qq号，未添加--onlystruct参数时必填", default=0)
    parser.add_argument("--host", type=str, help="mysql host[默认127.0.0.1]", default="127.0.0.1")
    parser.add_argument("--user", type=str, help="mysql username[默认root]", default="root")
    parser.add_argument("--password", type=str, help="mysql password[默认123456]", default="123456")
    parser.add_argument("--port", type=int, help="mysql port[默认3306]", default=3306)
    parser.add_argument("--database", type=str, help="mysql db[默认starbot]", default="starbot")
    parser.add_argument("--onlystruct", action="store_true", help="mysql仅初始化结构", default=False)

    # 解析参数并运行
    args = parser.parse_args()
    asyncio.run(main(args))
