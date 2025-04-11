import asyncio
import aiomysql
import argparse
import sys

from loguru import logger

async def execute_sql(db_config, starbot_sql):
    """执行SQL文件"""
    # 连接到目标数据库
    conn = await aiomysql.connect(
        host=db_config["host"],
        port=db_config["port"],
        user=db_config["user"],
        password=db_config["password"],
        db=db_config["db"]
    )
    try:
        # 分割SQL语句（简单分号分割，实际需要更复杂的解析）
        statements = [stmt.strip() for stmt in starbot_sql.split(';') if stmt.strip()]

        async with conn.cursor() as cursor:
            for stmt in statements:
                if stmt.upper().startswith("DELIMITER"):
                    continue  # 跳过DELIMITER指令
                try:
                    await cursor.execute(stmt)
                    logger.debug(f"Executed: {stmt[:50]}...")  # 显示前50个字符
                except aiomysql.Error as e:
                    logger.error(f"Error executing statement: {e}\nStatement: {stmt}")
                    raise
            await conn.commit()
    except Exception as e:
        logger.error(f"Error executing SQL file: {e}")
    finally:
        conn.close()


async def get_count(db_config, sql) -> int:
    conn = await aiomysql.connect(
        host=db_config["host"],
        port=db_config["port"],
        user=db_config["user"],
        password=db_config["password"],
        db=db_config["db"]
    )
    try:
        async with conn.cursor() as cursor:
            # 执行 COUNT(*) 查询
            await cursor.execute(sql)
            logger.debug(f"Executed: {sql[:50]}...")  # 显示前50个字符
            # 直接获取结果（COUNT(*) 返回单行单列）
            result = await cursor.fetchone()
            total = result[0]  # 结果是一个元组，如 (100,)
            return total
    except Exception as e:
        logger.error(f"Error executing SQL file: {e}")
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
    old_qq = args.oldqq
    new_qq = args.newqq
    count_sql = f"SELECT COUNT(*) AS total FROM bot WHERE bot = {old_qq};"
    insert_sql = f"UPDATE bot SET bot = {new_qq} WHERE bot = {old_qq};"
    count = await get_count(db_config, count_sql)
    logger.info(f"原qq号{old_qq}转换为新qq号{new_qq}，共{count}条数据，正在写入数据库...")
    await execute_sql(db_config, insert_sql)
    logger.success(f"^_^数据库初始化已完成，已完成mysql数据源的qq号迁移({old_qq} -> {new_qq})，共{count}条数据")
    exit()


if __name__ == "__main__":
    logger_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<level>{message}</level>"
    )
    logger.remove()
    logger.add(sys.stderr, format=logger_format, level="DEBUG")
    # 创建参数解析器
    parser = argparse.ArgumentParser(description="starbot_mysql_plugin数据库迁移工具")
    parser.add_argument("--oldqq", type=int, help="bot旧qq号", required=True)
    parser.add_argument("--newqq", type=int, help="bot新qq号", required=True)
    parser.add_argument("--host", type=str, help="mysql host[默认127.0.0.1]", default="127.0.0.1")
    parser.add_argument("--user", type=str, help="mysql username[默认root]", default="root")
    parser.add_argument("--password", type=str, help="mysql password[默认123456]", default="123456")
    parser.add_argument("--port", type=int, help="mysql port[默认3306]", default=3306)
    parser.add_argument("--database", type=str, help="mysql db[默认starbot]", default="starbot")

    # 解析参数并运行
    args = parser.parse_args()
    asyncio.run(main(args))
