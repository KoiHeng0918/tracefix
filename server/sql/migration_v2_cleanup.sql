-- TraceFix v2 清理脚本（可选）
-- 目的：删除 v1 的 qa_question_log。该表已被 qa_diagnosis_ticket 取代，
--       当前代码和 schema.sql 中不再使用。
--
-- 如果准备执行 reset_v2.sql 直接重建数据库，本脚本不需要再执行。
--
-- 注意：
-- 1. 本脚本不会自动执行，需要你确认后手动运行。
-- 2. 执行前先备份数据库；如仍需保留历史数据，先执行下面的备份语句。
-- 3. 只在开发库 devqa 中执行，不要在生产库直接跑。

-- 可选：备份旧表（需要时取消注释）
-- CREATE TABLE qa_question_log_backup AS SELECT * FROM qa_question_log;

-- 确认不再需要旧数据后，再执行：
DROP TABLE IF EXISTS qa_question_log;
