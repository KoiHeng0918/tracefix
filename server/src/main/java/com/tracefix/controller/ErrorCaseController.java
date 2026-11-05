package com.tracefix.controller;

import com.tracefix.common.Result;
import com.tracefix.dto.CasePromoteDTO;
import com.tracefix.dto.CaseReviewDTO;
import com.tracefix.dto.ErrorCaseCreateDTO;
import com.tracefix.service.ErrorCaseService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

/**
 * 案例库相关接口。
 * 案例是“已验证的报错解决方案”，不是每条报错都自动入库。
 */
@RestController
@RequestMapping("/case")
public class ErrorCaseController {

    @Autowired
    private ErrorCaseService errorCaseService;

    /** 手动导入一条案例，主要用于种子数据。 */
    @PostMapping("/import")
    public Result importCase(@Validated @RequestBody ErrorCaseCreateDTO dto) {
        return Result.success(errorCaseService.importCase(dto));
    }

    /** 查询案例列表。 */
    @GetMapping("/list")
    public Result listCases() {
        return Result.success(errorCaseService.listCases());
    }

    /** 查看案例详情。 */
    @GetMapping("/detail")
    public Result detail(@RequestParam Long id) {
        return Result.success(errorCaseService.getCase(id));
    }

    /** 审核案例状态：DRAFT / REVIEW / ACTIVE / DEPRECATED。 */
    @PostMapping("/review")
    public Result review(@Validated @RequestBody CaseReviewDTO dto) {
        return Result.success(errorCaseService.review(dto));
    }

    /** 把一条 RESOLVED 的诊断记录生成案例草稿。 */
    @PostMapping("/promote")
    public Result promote(@Validated @RequestBody CasePromoteDTO dto) {
        return Result.success(errorCaseService.promote(dto));
    }
}
