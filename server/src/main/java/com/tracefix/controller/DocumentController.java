package com.tracefix.controller;

import com.tracefix.common.Result;
import com.tracefix.dto.DocumentCreateDTO;
import com.tracefix.service.DocumentService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

/**
 * 原始资料录入接口（P1）。
 * 不是当前诊断主线；诊断主线使用 /diagnosis 和 /case。
 */
@RestController
@RequestMapping("/doc")
public class DocumentController {

    @Autowired
    private DocumentService documentService;

    /** 录入一条原始资料，落库为 PENDING。 */
    @PostMapping("/upload")
    public Result uploadDocument(@Validated @RequestBody DocumentCreateDTO documentCreateDTO) {
        return Result.success(documentService.createDocument(documentCreateDTO));
    }

}
