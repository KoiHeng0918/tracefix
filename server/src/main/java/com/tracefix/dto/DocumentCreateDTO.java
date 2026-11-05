package com.tracefix.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

/**
 * 文档录入请求参数（P1 原始资料）。
 */
@Data
public class DocumentCreateDTO {
    /** 标题 简要描述错误*/
    @NotBlank(message = "标题不可以为空")
    private String title;

    /** 分类，如 spring、redis、errors */
    @NotBlank(message = "未填写分类")
    private String category;

    /** 来源（可选） */
    private String source;

    /** 正文 */
    @NotBlank(message = "正文不可为空")
    private String content;

}
