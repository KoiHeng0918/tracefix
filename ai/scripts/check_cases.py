import os
from pathlib import Path

import pymysql
from dotenv import load_dotenv

# 从 ai/.env 读取数据库配置
BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")


def get_connection():
    """建立 MySQL 连接。"""
    return pymysql.connect(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        port=int(os.getenv("MYSQL_PORT", "13306")),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE", "tracefix"),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )


def main():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # 只读取正式参与检索的 ACTIVE 案例
            cursor.execute(
                """
                SELECT case_no, title, exception_type, message_pattern
                FROM qa_error_case
                WHERE status = 'ACTIVE'
                ORDER BY id
                """
            )
            rows = cursor.fetchall()

        print(f"ACTIVE cases: {len(rows)}")
        for row in rows:
            print("-" * 80)
            print(f"case_no: {row['case_no']}")
            print(f"title: {row['title']}")
            print(f"exception_type: {row['exception_type']}")
            print(f"message_pattern: {row['message_pattern']}")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
