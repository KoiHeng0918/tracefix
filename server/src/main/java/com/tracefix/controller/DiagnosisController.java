package com.tracefix.controller;

import com.tracefix.common.Result;
import com.tracefix.dto.DiagnosisAnalyzeDTO;
import com.tracefix.dto.DiagnosisConfirmDTO;
import com.tracefix.service.DiagnosisService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

/**
 * 诊断相关接口。
 * Controller 只负责接收参数、调用 Service、包装统一返回。
 */
@RestController
@RequestMapping("/diagnosis")
public class DiagnosisController {

    @Autowired
    private DiagnosisService diagnosisService;

    /** 贴报错，创建诊断记录并返回 AI 诊断结果。 */
    @PostMapping("/analyze")
    public Result analyze(@Validated @RequestBody DiagnosisAnalyzeDTO dto) {
        return Result.success(diagnosisService.analyze(dto));
    }

    /** 查询本地诊断记录列表。 */
    @GetMapping("/ticket/list")
    public Result listTickets() {
        return Result.success(diagnosisService.listTickets());
    }

    /** 按 ID 查看一条诊断记录。 */
    @GetMapping("/ticket/detail")
    public Result ticketDetail(@RequestParam Long id) {
        return Result.success(diagnosisService.getTicket(id));
    }

    /** 人工确认根因是否正确、修复是否有效。 */
    @PostMapping("/confirm")
    public Result confirm(@Validated @RequestBody DiagnosisConfirmDTO dto) {
        return Result.success(diagnosisService.confirm(dto));
    }
}
