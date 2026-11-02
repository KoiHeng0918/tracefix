package com.devqa.devqaserver.service.impl;

import com.devqa.devqaserver.dto.DocumentCreateDTO;
import com.devqa.devqaserver.entity.QaDocument;
import com.devqa.devqaserver.mapper.QaDocumentMapper;
import com.devqa.devqaserver.service.DocumentService;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;


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
// TODO 接入 RabbitMQ 后发送文档ID
        return doc.getId();

    }
}
