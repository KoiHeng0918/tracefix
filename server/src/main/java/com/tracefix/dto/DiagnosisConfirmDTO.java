package com.tracefix.dto;

import jakarta.validation.constraints.NotNull;
import lombok.Data;

/**
 * 人工确认请求参数。
 * 用于确认 AI 根因是否正确、修复是否有效。
 */
@Data
public class DiagnosisConfirmDTO {
    /** 诊断记录 ID ，由诊断结果或者手写输入*/
    @NotNull(message = "ticketId 不可以为空")
    private Long ticketId;

    /** 根因是否正确，由所按的按键决定 */
    private Boolean rootCauseCorrect;

    /** 修复是否有效 */
    private Boolean fixEffective;

    /** 人工确认或修正后的根因（可选；AI 正确时可留空） */
    private String confirmedRootCause;

    /** 解决说明 */
    private String resolutionNote;

}
