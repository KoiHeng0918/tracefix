package com.tracefix.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class ErrorCaseCreateDTO {
    @NotBlank(message = "案例编号不可以为空")
    private String caseNo;
    @NotBlank(message = "标题不可以为空")
    private String title;
    @NotBlank(message = "分类不可以为空")
    private String category;
    @NotBlank(message = "异常类型不可以为空")
    private String exceptionType;
    @NotBlank(message = "异常消息模式不可以为空")
    private String messagePattern;
    @NotBlank(message = "技术栈不可以为空")
    private String techStack;
    private String versionScope;
    @NotBlank(message = "现象描述不可以为空")
    private String symptom;
    @NotBlank(message = "根因不可以为空")
    private String rootCause;
    @NotBlank(message = "修复步骤不可以为空")
    private String fixSteps;
    @NotBlank(message = "验证方式不可以为空")
    private String verification;
    @NotBlank(message = "来源不可以为空")
    private String source;
    private String sourceUrl;
    private String license;
    @NotBlank(message = "指纹不可以为空")
    private String fingerprint;

}
