package com.tracefix.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

/**
 * 诊断分析请求参数。
 * 用户只需要提供报错原文和可选的补充信息。
 */
@Data
public class DiagnosisAnalyzeDTO {
    /** 用户粘贴的报错原文/堆栈，对应 qa_diagnosis_ticket.input_trace */
    @NotBlank(message = "报错内容不可以为空")
    private String inputTrace;

    /** 补充信息：JDK/框架版本、代码片段、配置等，对应 input_context */
    private String inputContext;

    /** 会话分组 ID，可选；不是登录身份 */
    private String sessionId;

    /** 请求幂等键，可选；防止重复提交 */
    private String requestId;

}
