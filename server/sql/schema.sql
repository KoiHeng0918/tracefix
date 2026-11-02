-- DevQA 业务表建表脚本
-- 在 devqa 库中执行

CREATE TABLE IF NOT EXISTS qa_document (
    id          BIGINT       NOT NULL AUTO_INCREMENT COMMENT '主键',
    title       VARCHAR(200) NOT NULL COMMENT '文档标题',
    category    VARCHAR(50)  NOT NULL COMMENT '分类：spring/redis/errors 等',
    source      VARCHAR(200) DEFAULT NULL COMMENT '来源',
    content     MEDIUMTEXT   NOT NULL COMMENT '文档原文',
    chunk_count INT          NOT NULL DEFAULT 0 COMMENT '切分后的块数',
    status      VARCHAR(20)  NOT NULL DEFAULT 'PENDING' COMMENT '向量化状态：PENDING/PROCESSING/DONE/FAILED',
    create_time DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (id),
    KEY idx_category_status (category, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='知识文档表';

CREATE TABLE IF NOT EXISTS qa_question_log (
    id             BIGINT     NOT NULL AUTO_INCREMENT COMMENT '主键',
    session_id     VARCHAR(64) NOT NULL COMMENT '会话ID',
    question       TEXT       NOT NULL COMMENT '用户问题',
    answer         MEDIUMTEXT COMMENT '模型回答',
    mode           VARCHAR(20) NOT NULL DEFAULT 'CHAT' COMMENT '模式：CHAT/DIAGNOSE',
    hit_knowledge  TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否命中知识库',
    doc_ids        VARCHAR(200) DEFAULT NULL COMMENT '命中的文档ID，逗号分隔',
    model          VARCHAR(50) DEFAULT NULL COMMENT '使用的模型',
    latency_ms     INT        DEFAULT NULL COMMENT '总耗时（毫秒）',
    create_time    DATETIME   NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    KEY idx_session (session_id),
    KEY idx_create_time (create_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='问答记录表';
