package com.tracefix.dto;

import jakarta.validation.constraints.NotNull;
import lombok.Data;

/**
 * 工单回流案例请求参数。
 * 把一条已解决的诊断记录生成案例草稿。
 */
@Data
public class CasePromoteDTO {
    /** 已解决的诊断记录 ID */
    @NotNull(message = "ticketId 不可以为空")
    private Long ticketId;

}
