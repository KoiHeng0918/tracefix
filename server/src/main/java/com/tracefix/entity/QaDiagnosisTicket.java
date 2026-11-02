package com.tracefix.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;
import java.util.Date;

@Data
@TableName(value = "qa_diagnosis_ticket")
public class QaDiagnosisTicket {
    @TableId(type = IdType.AUTO)
    private Long id;
    private String ticketNo;
    private String requestId;
    private String sessionId;
    private String inputTrace;
    private String inputContext;
    private String fingerprint;
    private String extractedException;
    private String extractedMessage;
    private String matchedCaseIds;
    private String diagnosisJson;
    private BigDecimal confidence;
    private String status;
    private String confirmationResult;
    private String confirmedRootCause;
    private Boolean fixEffective;
    private String resolutionNote;
    private String escalatedIssueUrl;
    private Integer latencyMs;
    private String model;
    private String promptVersion;
    private String retrievalVersion;
    private Boolean isEval;
    private Date createTime;
    private Date updateTime;

}
