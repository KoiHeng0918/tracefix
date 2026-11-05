package com.tracefix.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;
import java.util.Date;

/**
 * 诊断记录表：一次诊断的输入、AI 结果、人工确认和状态。
 * 对应表：qa_diagnosis_ticket
 */
@Data
@TableName(value = "qa_diagnosis_ticket")
public class QaDiagnosisTicket {
    /** 主键 */
    @TableId(type = IdType.AUTO)
    private Long id;

    /** 工单号，如 D-20261102-0001，唯一 */
    private String ticketNo;

    /** 请求幂等键，防止重复提交生成多条记录 */
    private String requestId;

    /** 会话分组 ID；只用于分组，不是登录身份 */
    private String sessionId;

    /** 用户粘贴的报错原文 */
    private String inputTrace;

    /** 补充信息：版本、代码片段、配置等 */
    private String inputContext;

    /** 报错指纹 */
    private String fingerprint;

    /** 从报错中抽取的异常类型 */
    private String extractedException;

    /** 归一化后的异常消息 */
    private String extractedMessage;

    /** 命中的案例 ID，逗号分隔 */
    private String matchedCaseIds;

    /** AI 返回的完整结构化诊断 JSON */
    private String diagnosisJson;

    /** 置信度 0.00-1.00 */
    private BigDecimal confidence;

    /** 状态：SUBMITTED / DIAGNOSED / NEED_INFO / CONFIRMED / REJECTED / RESOLVED / ARCHIVED 等 */
    private String status;

    /** 人工确认或修正后的根因 */
    private String confirmedRootCause;

    /** 修复是否有效：1 是 / 0 否 / null 未确认 */
    private Boolean fixEffective;

    /** 解决说明 */
    private String resolutionNote;

    /** 转外部 Issue 的链接（可选） */
    private String escalatedIssueUrl;

    /** 诊断耗时（毫秒） */
    private Integer latencyMs;

    /** 使用的模型 */
    private String model;

    /** Prompt 版本 */
    private String promptVersion;

    /** 检索/索引版本 */
    private String retrievalVersion;

    /** 是否评测流量，避免污染真实统计 */
    private Boolean isEval;

    /** 创建时间 */
    private Date createTime;

    /** 更新时间 */
    private Date updateTime;

}
