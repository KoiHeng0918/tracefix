package com.tracefix.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

/**
 * 案例审核请求参数。
 * 用于修改案例状态，如 DRAFT → ACTIVE，或 ACTIVE → DEPRECATED。
 */
@Data
public class CaseReviewDTO {
    /** 案例 ID */
    @NotNull(message = "caseId 不可以为空")
    private Long caseId;

    /** 目标状态：DRAFT / REVIEW / ACTIVE / DEPRECATED */
    @NotBlank(message = "status 不可以为空")
    private String status;

    /** 审核备注（可选） */
    private String comment;

}
