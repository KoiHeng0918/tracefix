package com.tracefix.service.impl;

import com.tracefix.common.BizException;
import com.tracefix.dto.CasePromoteDTO;
import com.tracefix.dto.CaseReviewDTO;
import com.tracefix.dto.ErrorCaseCreateDTO;
import com.tracefix.entity.QaDiagnosisTicket;
import com.tracefix.entity.QaErrorCase;
import com.tracefix.mapper.QaDiagnosisTicketMapper;
import com.tracefix.mapper.QaErrorCaseMapper;
import com.tracefix.service.ErrorCaseService;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.ObjectMapper;

import java.util.List;

/**
 * 案例库业务实现。
 * 负责案例导入、查询、审核，以及“已解决工单 → 案例草稿”的回流。
 */
@Service
public class ErrorCaseServiceImpl implements ErrorCaseService {

    @Autowired
    private QaErrorCaseMapper qaErrorCaseMapper;

    @Autowired
    private QaDiagnosisTicketMapper qaDiagnosisTicketMapper;

    @Autowired
    private ObjectMapper objectMapper;

    /**
     * 手动导入一条案例。
     * 当前用于种子数据，导入后直接 ACTIVE。
     */
    @Override
    public Long importCase(ErrorCaseCreateDTO dto) {
        QaErrorCase errorCase = new QaErrorCase();
        BeanUtils.copyProperties(dto, errorCase);
        errorCase.setStatus("ACTIVE");
        errorCase.setQualityScore(3);
        errorCase.setHitCount(0);
        qaErrorCaseMapper.insert(errorCase);
        return errorCase.getId();
    }

    /** 查询全部案例。当前没有分页。 */
    @Override
    public List<QaErrorCase> listCases() {
        return qaErrorCaseMapper.selectList(null);
    }

    /** 按 ID 查询案例，不存在抛 404。 */
    @Override
    public QaErrorCase getCase(Long id) {
        QaErrorCase errorCase = qaErrorCaseMapper.selectById(id);
        if (errorCase == null) {
            throw new BizException(404, "案例不存在");
        }
        return errorCase;
    }

    /** 修改案例状态，例如 DRAFT → ACTIVE。 */
    @Override
    public QaErrorCase review(CaseReviewDTO dto) {
        QaErrorCase errorCase = getCase(dto.getCaseId());
        if (!List.of("DRAFT", "REVIEW", "ACTIVE", "DEPRECATED").contains(dto.getStatus())) {
            throw new BizException("不支持的案例状态：" + dto.getStatus());
        }
        errorCase.setStatus(dto.getStatus());
        qaErrorCaseMapper.updateById(errorCase);
        return errorCase;
    }

    /**
     * 数据飞轮：把已解决的诊断记录生成案例草稿。
     *
     * 注意：
     * - 只有 RESOLVED 状态可以回流
     * - 生成的是 DRAFT，不是直接 ACTIVE
     * - 标题/根因/修复来自诊断记录，缺失字段先写“待补充”
     */
    @Override
    public Long promote(CasePromoteDTO dto) {

        //1. 校验是不是正确调用接口
        QaDiagnosisTicket ticket = qaDiagnosisTicketMapper.selectById(dto.getTicketId());
        
        if (ticket == null) {
            throw new BizException(404, "诊断记录不存在");
        }
        if (!"RESOLVED".equals(ticket.getStatus())) {
            throw new BizException("只有 RESOLVED 状态的记录可以生成案例草稿");
        }

        //2. 填入案例库

        QaErrorCase errorCase = new QaErrorCase();
        errorCase.setCaseNo("ERR-" + System.currentTimeMillis());
        errorCase.setTitle(resolveTitle(ticket));
        errorCase.setExceptionType(defaultIfBlank(ticket.getExtractedException(), "UNKNOWN"));
        errorCase.setMessagePattern(defaultIfBlank(ticket.getExtractedMessage(), "待补充"));
        errorCase.setRootCause(defaultIfBlank(ticket.getConfirmedRootCause(), "待补充"));
        errorCase.setFixSteps(defaultIfBlank(ticket.getResolutionNote(), "待补充"));
        errorCase.setCategory("unknown");
        errorCase.setTechStack("待补充");
        errorCase.setSymptom(ticket.getInputTrace());
        errorCase.setVerification("待补充");
        errorCase.setSource("工单回流");
        errorCase.setFingerprint(defaultIfBlank(ticket.getFingerprint(), "tmp-ticket-" + ticket.getId()));
        errorCase.setStatus("DRAFT");
        errorCase.setQualityScore(3);
        errorCase.setHitCount(0);
        errorCase.setSourceTicketId(ticket.getId());
        qaErrorCaseMapper.insert(errorCase);

        // 工单已回流，标记为 ARCHIVED，避免重复生成
        ticket.setStatus("ARCHIVED");
        qaDiagnosisTicketMapper.updateById(ticket);
        return errorCase.getId();
    }

    /**
     * 生成案例标题。
     * 优先用人工确认后的根因 confirmedRootCause，其次用 AI 返回的 title，最后退回报错第一行。
     */
    private String resolveTitle(QaDiagnosisTicket ticket) {
        String confirmedRootCause = ticket.getConfirmedRootCause();
        if (confirmedRootCause != null && !confirmedRootCause.isBlank()) {
            return toTitle(confirmedRootCause);
        }

        String title = readDiagnosisTitle(ticket.getDiagnosisJson());
        if (title != null && !title.isBlank()) {
            return toTitle(title);
        }

        return toTitle(ticket.getInputTrace());
    }

    /** 从 diagnosis_json 里读取 AI 返回的 title。解析失败时返回 null，不影响回流。 */
    private String readDiagnosisTitle(String diagnosisJson) {
        if (diagnosisJson == null || diagnosisJson.isBlank()) {
            return null;
        }
        try {
            JsonNode root = objectMapper.readTree(diagnosisJson);
            JsonNode title = root.get("title");
            return title == null || title.isNull() ? null : title.asText();
        } catch (Exception e) {
            return null;
        }
    }

    /** 取文本第一行并截断到 120 个字符。 */
    private String toTitle(String text) {
        if (text == null || text.isBlank()) {
            return "待补充";
        }

        //  \R是匹配任意换行符，在\R前加\转义
        //  2即只分隔一刀分为两段，得到一个被分隔为两段的字符串组
        //  例如输入："第一行\n第二行\n第三行"
        //split("\\R",2) → ["第一行", "第二行\n第三行"]
        String line = text.split("\\R", 2)[0].trim();

        // 第一行为空默认标题
        if (line.isEmpty()) {
            return "待补充";
        }

        //截取后返回最大长120文本
        return line.length() > 120 ? line.substring(0, 120) : line;
    }

    /** 值为空时使用兜底文本。 */
    private String defaultIfBlank(String value, String fallback) {
        return value == null || value.isBlank() ? fallback : value;
    }
}
