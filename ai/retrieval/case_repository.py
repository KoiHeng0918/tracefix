import os
from pathlib import Path

import pymysql
from dotenv import load_dotenv

# 当前文件在 ai/retrieval/ 下
# __file__ 表示当前文件,.resolve() 把它变成绝对路径：
# parents[1] 上级的上级，就是/retrieval的上级 ai 目录
BASE_DIR = Path(__file__).resolve().parents[1]

# 读取 ai/.env 这个文件。
load_dotenv(BASE_DIR / ".env")


# 简历MySQL连接
def get_connection():
    return pymysql.connect(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        port=int(os.getenv("MYSQL_PORT", "13306")),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE", "tracefix"),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )


def list_active_cases() -> list[dict]:
    """读取所有 ACTIVE 案例，返回字典列表。"""
    connection = get_connection()
    try:
        #类似Java的 try with resource
        with connection.cursor() as cursor:

            # execute执行SQL语句，但是不取返回值
            cursor.execute(
                """
                SELECT
                    case_no,
                    title,
                    category,
                    exception_type,
                    message_pattern,
                    tech_stack,
                    root_cause,
                    fix_steps,
                    verification
                FROM qa_error_case
                WHERE status = 'ACTIVE'
                ORDER BY id
                """
            )

            # fetchall将游标运行后的返回值取出，结果为list
            return list(cursor.fetchall())
    finally:
        connection.close()