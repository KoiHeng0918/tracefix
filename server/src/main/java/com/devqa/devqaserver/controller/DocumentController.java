package com.devqa.devqaserver.controller;

import com.devqa.devqaserver.common.Result;
import com.devqa.devqaserver.dto.DocumentCreateDTO;
import com.devqa.devqaserver.service.DocumentService;
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
