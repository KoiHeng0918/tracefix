package com.tracefix.service.impl;

import com.tracefix.dto.DocumentCreateDTO;
import com.tracefix.entity.QaDocument;
import com.tracefix.mapper.QaDocumentMapper;
import com.tracefix.service.DocumentService;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

/**
 * 原始资料业务实现（P1）。
 * 当前只负责落库，不做向量化；后续可接 MQ 异步处理。
 */
@Service
public class DocumentServiceImpl implements DocumentService {

    @Autowired
    private QaDocumentMapper qaDocumentMapper;

    @Override
    public Long createDocument(DocumentCreateDTO dto) {
        QaDocument doc = new QaDocument();
        BeanUtils.copyProperties(dto, doc);
        doc.setStatus("PENDING");
        qaDocumentMapper.insert(doc);
        // P1：原始资料入库暂不接 MQ；诊断主链路不依赖文档上传。
        return doc.getId();
    }
}
