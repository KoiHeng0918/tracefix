-- TraceFix v2 数据库重建脚本
--
-- 警告：本脚本会删除旧库 devqa 和同名 tracefix 库，属于不可逆操作。
-- 执行前必须先备份。示例：
--   mysqldump -h 127.0.0.1 -P 13306 -u <user> -p devqa > devqa_v1_backup.sql
--
-- 执行顺序：
--   1. 备份旧库
--   2. 执行本脚本
--   3. 再执行 schema.sql 建表
--
-- 本脚本不会自动执行，需要你确认后手动运行。

DROP DATABASE IF EXISTS devqa;
DROP DATABASE IF EXISTS tracefix;

CREATE DATABASE tracefix
    DEFAULT CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE tracefix;
