package com.tracefix.service;

import com.tracefix.common.PageResult;
import com.tracefix.dto.DiagnosisAnalyzeDTO;
import com.tracefix.dto.DiagnosisConfirmDTO;
import com.tracefix.entity.QaDiagnosisTicket;

import java.util.Map;

/**
 * 诊断业务接口。
 * 实现类负责“建工单 → 调 AI → 保存结果 → 人工确认”。
 */
public interface DiagnosisService {
    /** 提交报错并诊断，返回 ticketId 和诊断结果。 */
    Map<String, Object> analyze(DiagnosisAnalyzeDTO dto);

    /** 分页查询诊断记录，可按状态筛选。 */
    PageResult<QaDiagnosisTicket> listTickets(int pageNum, int pageSize, String status);

    /** 按 ID 查询诊断记录。 */
    QaDiagnosisTicket getTicket(Long id);

    /** 人工确认根因/修复结果。 */
    QaDiagnosisTicket confirm(DiagnosisConfirmDTO dto);
}
