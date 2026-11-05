package com.tracefix.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

/**
 * 案例导入请求参数。
 * 对应实体：QaErrorCase
 */
@Data
public class ErrorCaseCreateDTO {
    /** 案例编号，如 ERR-SPRING-0001 */
    @NotBlank(message = "案例编号不可以为空")
    private String caseNo;

    /** 标题 */
    @NotBlank(message = "标题不可以为空")
    private String title;

    /** 分类：spring / mybatis / mysql 等 */
    @NotBlank(message = "分类不可以为空")
    private String category;

    /** 异常全类名 */
    @NotBlank(message = "异常类型不可以为空")
    private String exceptionType;

    /** 归一化后的异常消息骨架 */
    @NotBlank(message = "异常消息模式不可以为空")
    private String messagePattern;

    /** 技术栈/版本 */
    @NotBlank(message = "技术栈不可以为空")
    private String techStack;

    /** 适用版本范围（可选） */
    private String versionScope;

    /** 现象/堆栈摘要 */
    @NotBlank(message = "现象描述不可以为空")
    private String symptom;

    /** 根因 */
    @NotBlank(message = "根因不可以为空")
    private String rootCause;

    /** 修复步骤 */
    @NotBlank(message = "修复步骤不可以为空")
    private String fixSteps;

    /** 验证方式 */
    @NotBlank(message = "验证方式不可以为空")
    private String verification;

    /** 来源：自己项目 / 公开 issue / 官方文档 */
    @NotBlank(message = "来源不可以为空")
    private String source;

    /** 公开来源链接（可选） */
    private String sourceUrl;

    /** 许可证/使用说明（可选） */
    private String license;

    /** 报错指纹 */
    @NotBlank(message = "指纹不可以为空")
    private String fingerprint;

}
