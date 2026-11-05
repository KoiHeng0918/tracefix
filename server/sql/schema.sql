-- TraceFix 业务表建表脚本（v2）
-- 在 tracefix 库中执行
--
-- 当前包含三张表：
--   qa_document          P1 原始资料库，非诊断主链路
--   qa_error_case        报错案例库，诊断的检索语料
--   qa_diagnosis_ticket  诊断记录/工单，承载诊断结果与人工确认
--
-- 旧库 devqa 的 qa_question_log 已被 qa_diagnosis_ticket 取代。
-- 重建数据库的步骤见 sql/reset_v2.sql。

CREATE TABLE IF NOT EXISTS qa_document (
    id          BIGINT       NOT NULL AUTO_INCREMENT COMMENT '主键',
    title       VARCHAR(200) NOT NULL COMMENT '文档标题',
    category    VARCHAR(50)  NOT NULL COMMENT '分类：spring/redis/errors 等',
    source      VARCHAR(200) DEFAULT NULL COMMENT '来源',
    content     MEDIUMTEXT   NOT NULL COMMENT '文档原文',
    chunk_count INT          NOT NULL DEFAULT 0 COMMENT '切分后的块数',
    status      VARCHAR(20)  NOT NULL DEFAULT 'PENDING' COMMENT '处理状态：PENDING/PROCESSING/DONE/FAILED',
    create_time DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (id),
    KEY idx_category_status (category, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='原始资料表（P1，非诊断主链路）';

CREATE TABLE IF NOT EXISTS qa_error_case (
    id             BIGINT       NOT NULL AUTO_INCREMENT COMMENT '主键',
    case_no        VARCHAR(32)  NOT NULL COMMENT '业务编号，如 ERR-SPRING-0001',
    title          VARCHAR(200) NOT NULL COMMENT '标题',
    category       VARCHAR(50)  NOT NULL COMMENT '分类：spring/mybatis/mysql/redis/mq/jvm/concurrency/build/network',
    exception_type VARCHAR(200) NOT NULL COMMENT '异常全限定名',
    message_pattern VARCHAR(500) NOT NULL COMMENT '归一化后的异常消息模式',
    tech_stack     VARCHAR(100) NOT NULL COMMENT '技术栈，如 Spring Boot 3.x + MyBatis-Plus 3.5.x',
    version_scope  VARCHAR(100) DEFAULT NULL COMMENT '适用版本范围；未验证时写“未验证”',
    symptom        TEXT         NOT NULL COMMENT '用户看到的现象/堆栈摘要',
    root_cause     TEXT         NOT NULL COMMENT '具体根因',
    fix_steps      MEDIUMTEXT   NOT NULL COMMENT '有序修复步骤',
    verification   TEXT         NOT NULL COMMENT '如何确认修好',
    source         VARCHAR(200) NOT NULL COMMENT '来源：自己项目/公开 issue/官方文档',
    source_url     VARCHAR(500) DEFAULT NULL COMMENT '公开来源链接',
    license        VARCHAR(50)  DEFAULT NULL COMMENT '公开来源许可证/使用说明',
    fingerprint    CHAR(64)     NOT NULL COMMENT '异常类+归一化消息+关键帧的哈希',
    embedding_id   VARCHAR(100) DEFAULT NULL COMMENT 'FAISS 中的向量 ID',
    quality_score  TINYINT      NOT NULL DEFAULT 3 COMMENT '人工质量分 1-5',
    status         VARCHAR(20)  NOT NULL DEFAULT 'DRAFT' COMMENT 'DRAFT/REVIEW/ACTIVE/DEPRECATED',
    source_ticket_id BIGINT     DEFAULT NULL COMMENT '从哪张诊断工单回流',
    hit_count      INT          NOT NULL DEFAULT 0 COMMENT '被检索命中次数',
    create_time    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_case_no (case_no),
    KEY idx_fingerprint (fingerprint),
    KEY idx_category_status (category, status),
    KEY idx_exception_type (exception_type),
    KEY idx_source_ticket (source_ticket_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='报错案例库';

CREATE TABLE IF NOT EXISTS qa_diagnosis_ticket (
    id                  BIGINT       NOT NULL AUTO_INCREMENT COMMENT '主键',
    ticket_no           VARCHAR(32)  NOT NULL COMMENT '工单号，如 D-20261102-0001',
    request_id          VARCHAR(64)  DEFAULT NULL COMMENT '请求幂等键',
    session_id          VARCHAR(64)  NOT NULL DEFAULT '' COMMENT '会话 ID',
    input_trace         MEDIUMTEXT   NOT NULL COMMENT '脱敏后的报错文本',
    input_context       MEDIUMTEXT   DEFAULT NULL COMMENT '代码/版本/配置等上下文',
    fingerprint         CHAR(64)     DEFAULT NULL COMMENT '报错指纹',
    extracted_exception VARCHAR(500) DEFAULT NULL COMMENT '抽取的异常全限定名',
    extracted_message   VARCHAR(1000) DEFAULT NULL COMMENT '归一化后的异常消息',
    matched_case_ids    VARCHAR(500) DEFAULT NULL COMMENT '命中的案例 ID，逗号分隔',
    diagnosis_json      MEDIUMTEXT   DEFAULT NULL COMMENT '结构化诊断 JSON',
    confidence          DECIMAL(3,2) DEFAULT NULL COMMENT '置信度 0.00-1.00',
    status              VARCHAR(20)  NOT NULL DEFAULT 'SUBMITTED' COMMENT 'SUBMITTED/DIAGNOSED/NEED_INFO/ABSTAINED/CONFIRMED/REJECTED/RESOLVED/ESCALATED/ARCHIVED/DIAGNOSIS_FAILED',
    confirmed_root_cause TEXT        DEFAULT NULL COMMENT '人工确认/修正后的根因',
    fix_effective       TINYINT(1)   DEFAULT NULL COMMENT '修复是否有效：1 是 / 0 否 / NULL 未确认',
    resolution_note     TEXT         DEFAULT NULL COMMENT '解决说明',
    escalated_issue_url VARCHAR(500) DEFAULT NULL COMMENT '外部 Issue 链接',
    latency_ms          INT          DEFAULT NULL COMMENT '诊断耗时（毫秒）',
    model               VARCHAR(50)  DEFAULT NULL COMMENT '使用的模型',
    prompt_version      VARCHAR(50)  DEFAULT NULL COMMENT 'Prompt 版本',
    retrieval_version   VARCHAR(50)  DEFAULT NULL COMMENT '检索/索引版本',
    is_eval             TINYINT(1)   NOT NULL DEFAULT 0 COMMENT '是否评测流量',
    create_time         DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time         DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_ticket_no (ticket_no),
    UNIQUE KEY uk_request_id (request_id),
    KEY idx_fingerprint (fingerprint),
    KEY idx_status_create (status, create_time),
    KEY idx_session (session_id),
    KEY idx_create_time (create_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='诊断记录/工单';
