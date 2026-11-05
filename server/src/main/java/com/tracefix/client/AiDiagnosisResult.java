package com.tracefix.client;

import lombok.Data;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

/**
 * AI 诊断结果对象。
 * 它只用于 Java 内部传递诊断结果，不是数据库实体。
 * 以后接真实 Python 服务时，可以继续复用它作为返回契约。
 */
@Data
public class AiDiagnosisResult {

    /** 对应 qa_diagnosis_ticket.fingerprint */
    private String fingerprint;

    /** 对应 qa_error_case.title */
    private String title;

    /** 对应 qa_diagnosis_ticket.extracted_exception */
    private String extractedException;

    /** 对应 qa_diagnosis_ticket.extracted_message */
    private String extractedMessage;

    /** 对应 qa_diagnosis_ticket.matched_case_ids */
    private List<String> matchedCaseIds = new ArrayList<>();

    /** 对应 qa_error_case.root_cause */
    private String rootCause;

    /** 对应 qa_error_case.fix_steps */
    private String fixSteps;

    /** 对应 qa_error_case.verification */
    private String verification;

    /** 对应 qa_diagnosis_ticket.confidence */
    private BigDecimal confidence = BigDecimal.ZERO;

    /** 没有数据库字段，用来决定 NEED_INFO 还是 DIAGNOSED */
    private List<String> missingInfo = new ArrayList<>();
}
