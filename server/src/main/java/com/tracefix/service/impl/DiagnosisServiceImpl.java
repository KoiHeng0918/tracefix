package com.tracefix.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.tracefix.client.AiClient;
import com.tracefix.client.AiDiagnosisResult;
import com.tracefix.common.BizException;
import com.tracefix.dto.DiagnosisAnalyzeDTO;
import com.tracefix.dto.DiagnosisConfirmDTO;
import com.tracefix.entity.QaDiagnosisTicket;
import com.tracefix.mapper.QaDiagnosisTicketMapper;
import com.tracefix.service.DiagnosisService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import tools.jackson.databind.ObjectMapper;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * 诊断主流程：
 * 1. analyze：保存用户输入 → 调用 AI → 把 AI 结果写回诊断记录
 * 2. confirm：人工确认根因/修复是否有效
 * 3. promote（在 ErrorCaseServiceImpl）：已解决工单再回流成案例草稿
 *
 * 注意：analyze 只写 qa_diagnosis_ticket，不写 qa_error_case。
 */
@Service
public class DiagnosisServiceImpl implements DiagnosisService {

    @Autowired
    private QaDiagnosisTicketMapper qaDiagnosisTicketMapper;

    @Autowired
    private AiClient aiClient;

    @Autowired
    private ObjectMapper objectMapper;

    /**
     * 提交报错并诊断。
     * 先把用户输入落一条 SUBMITTED 工单，再调用 AI，最后把结果更新回同一条工单。
     */
    @Override
    public Map<String, Object> analyze(DiagnosisAnalyzeDTO dto) {
        // 1. 创建诊断记录：此时只有用户输入，还没有 AI 结果
        QaDiagnosisTicket ticket = new QaDiagnosisTicket();

        ticket.setTicketNo("D-"+System.currentTimeMillis());
        ticket.setInputContext(dto.getInputContext());
        ticket.setInputTrace(dto.getInputTrace());
        ticket.setRequestId(dto.getRequestId());
        ticket.setStatus("SUBMITTED");
        ticket.setSessionId(dto.getSessionId() == null ? "" : dto.getSessionId());
        ticket.setIsEval(false);
        qaDiagnosisTicketMapper.insert(ticket);

        // 2. 调用 AI
        AiDiagnosisResult result = aiClient.diagnose(dto.getInputTrace(), dto.getInputContext());

        // 3. 把 AI 结果拆到工单字段里

        //主要有清洗过的ExtractedException和归一化的ExtractedMessage
        ticket.setExtractedException(result.getExtractedException());
        ticket.setExtractedMessage(result.getExtractedMessage());

        //还有匹配到的案例集，类型List<String>的ids
        if (result.getMatchedCaseIds() != null) {
        //  String.join(分隔符, 集合) → 返回用分隔符把每个元素连起来的一个字符串
            ticket.setMatchedCaseIds(String.join(",", result.getMatchedCaseIds()));
        }

        ticket.setConfidence(result.getConfidence());

        ticket.setFingerprint(result.getFingerprint());

        // missingInfo 为空说明证据足够，可以给诊断；
        // 否则需要用户补充信息
        ticket.setStatus(result.getMissingInfo() == null || result.getMissingInfo().isEmpty()
                ? "DIAGNOSED" : "NEED_INFO");

        // 4. 完整 AI 结果另存一份 JSON，方便以后复盘和评测
        try {
            ticket.setDiagnosisJson(objectMapper.writeValueAsString(result));
        } catch (Exception e) {
            throw new BizException(500, "诊断结果序列化失败");
        }

        qaDiagnosisTicketMapper.updateById(ticket);

        // 5. 返回给前端的是 data，不是整条数据库记录
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("ticketId", ticket.getId());
        data.put("ticketNo", ticket.getTicketNo());
        data.put("status", ticket.getStatus());
        data.put("diagnosis", result);
        return data;
    }

    /** 查询诊断记录列表，按创建时间倒序。 */
    @Override
    public List<QaDiagnosisTicket> listTickets() {
        return qaDiagnosisTicketMapper.selectList(
                new LambdaQueryWrapper<QaDiagnosisTicket>()
                        .orderByDesc(QaDiagnosisTicket::getCreateTime)
        );
    }

    /** 按 ID 查询一条诊断记录，不存在就抛 404。 */
    @Override
    public QaDiagnosisTicket getTicket(Long id) {
        QaDiagnosisTicket ticket = qaDiagnosisTicketMapper.selectById(id);
        if (ticket == null) {
            throw new BizException(404, "诊断记录不存在");
        }
        return ticket;
    }

    /**
     * 人工确认。
     * 只有 DIAGNOSED 状态可以确认；确认后根据修复是否有效更新状态。
     */
    @Override
    public QaDiagnosisTicket confirm(DiagnosisConfirmDTO dto) {

        //1. 判断是否处于DIAGNOSED状态 ，analyze调用AI未确诊的不走下方流程等待信息补全或者证据不足直接结束
        //创建ticket对象
        QaDiagnosisTicket ticket = getTicket(dto.getTicketId());
        //判断是不是DIAGNOSED
        if (!"DIAGNOSED".equals(ticket.getStatus())) {
            throw new BizException("只有 DIAGNOSED 状态的记录可以确认");
        }
        // 根因不对但人工修正后修好了：允许，但必须写清真实根因
        if (Boolean.TRUE.equals(dto.getFixEffective())
                && Boolean.FALSE.equals(dto.getRootCauseCorrect())
                && (dto.getConfirmedRootCause() == null || dto.getConfirmedRootCause().isBlank())) {
            throw new BizException("原因不对但已修好时，必须填写真实根因");
        }

        //2. 真正走confirm时，把DTO层对应传入数据写入对应工单实体类
        // 人工可修正确认根原因，由前端传入
        // 解决方案也由人工修正，前端传入
        // 是否有效由按钮决定
        // 按钮 | rootCauseCorrect | fixEffective | 状态 |
        //| 原因正确，已修好 | true | true | RESOLVED |
        //| 原因正确，还没修好 | true | false | CONFIRMED |
        //| 原因不对 | false | false | REJECTED |
        //| 原因不对，但已修好 | false | true | RESOLVED（必须填 confirmedRootCause） |
        ticket.setConfirmedRootCause(dto.getConfirmedRootCause());
        ticket.setFixEffective(dto.getFixEffective());
        ticket.setResolutionNote(dto.getResolutionNote());


        //3.根据写回工单的信息决定工单状态
        // 修复有效 → RESOLVED；根因不对 → REJECTED；根因对但没修好 → CONFIRMED
        if (Boolean.TRUE.equals(dto.getFixEffective())) {
            ticket.setStatus("RESOLVED");
        } else if (Boolean.FALSE.equals(dto.getRootCauseCorrect())) {
            ticket.setStatus("REJECTED");
        } else {
            ticket.setStatus("CONFIRMED");
        }
        // 更新工单
        qaDiagnosisTicketMapper.updateById(ticket);
        return ticket;
    }
}
