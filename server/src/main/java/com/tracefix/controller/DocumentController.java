package com.tracefix.controller;

import com.tracefix.common.Result;
import com.tracefix.dto.DocumentCreateDTO;
import com.tracefix.service.DocumentService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/doc")
public class DocumentController {
    @Autowired
    private DocumentService documentService;

    @PostMapping("/upload")
    public Result uploadDocument(@Validated @RequestBody DocumentCreateDTO documentCreateDTO) {

        return Result.success(documentService.createDocument(documentCreateDTO));
    }

}
