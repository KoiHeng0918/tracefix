package com.tracefix.controller;

import com.tracefix.common.Result;
import com.tracefix.dto.ErrorCaseCreateDTO;
import com.tracefix.service.ErrorCaseService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/case")
public class ErrorCaseController {

    @Autowired
    private ErrorCaseService errorCaseService;

    @PostMapping("/import")
    public Result importCase(@Validated @RequestBody ErrorCaseCreateDTO dto) {
        return Result.success(errorCaseService.importCase(dto));
    }

    @GetMapping("/list")
    public Result listCases() {
        return Result.success(errorCaseService.listCases());
    }
}
