package com.tracefix.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.util.Date;

/**
 * 报错案例表：结构化“报错 → 原因 → 修复 → 验证”。
 * 对应表：qa_error_case
 */
@Data
@TableName(value = "qa_error_case")
public class QaErrorCase {
    /** 主键 */
    @TableId(type = IdType.AUTO)
    private Long id;

    /** 案例编号，如 ERR-SPRING-0001，唯一 */
    private String caseNo;

    /** 标题 */
    private String title;

    /** 分类：spring / mybatis / mysql / redis / mq / jvm / concurrency / build / network */
    private String category;

    /** 异常全类名，如 java.lang.NullPointerException */
    private String exceptionType;

    /** 归一化后的异常消息骨架，用于匹配同类报错 */
    private String messagePattern;

    /** 技术栈，如 Spring Boot 3.x + MyBatis-Plus 3.5.x */
    private String techStack;

    /** 适用版本范围；未验证时写“未验证” */
    private String versionScope;

    /** 现象/堆栈摘要 */
    private String symptom;

    /** 具体根因 */
    private String rootCause;

    /** 有序修复步骤 */
    private String fixSteps;

    /** 如何确认修好 */
    private String verification;

    /** 来源：自己项目 / 公开 issue / 官方文档 */
    private String source;

    /** 公开来源链接 */
    private String sourceUrl;

    /** 公开来源许可证/使用说明 */
    private String license;

    /** 报错指纹，用于精确匹配和去重 */
    private String fingerprint;

    /** FAISS 中的向量 ID（后续接检索时使用） */
    private String embeddingId;

    /** 人工质量分 1-5 */
    private Integer qualityScore;

    /** 状态：DRAFT / REVIEW / ACTIVE / DEPRECATED */
    private String status;

    /** 从哪条诊断记录回流而来 */
    private Long sourceTicketId;

    /** 被检索命中次数 */
    private Integer hitCount;

    /** 创建时间 */
    private Date createTime;

    /** 更新时间 */
    private Date updateTime;

}
