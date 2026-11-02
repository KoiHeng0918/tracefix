package com.tracefix.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.util.Date;

@Data
@TableName(value = "qa_error_case")
public class QaErrorCase {
    @TableId(type = IdType.AUTO)
    private Long id;
    private String caseNo;
    private String title;
    private String category;
    private String exceptionType;
    private String messagePattern;
    private String techStack;
    private String versionScope;
    private String symptom;
    private String rootCause;
    private String fixSteps;
    private String verification;
    private String source;
    private String sourceUrl;
    private String license;
    private String fingerprint;
    private String embeddingId;
    private Integer qualityScore;
    private String status;
    private Long sourceTicketId;
    private Integer hitCount;
    private Date createTime;
    private Date updateTime;

}
