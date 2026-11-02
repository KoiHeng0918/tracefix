package com.devqa.devqaserver.service;

import com.devqa.devqaserver.dto.DocumentCreateDTO;



public interface DocumentService {
    public Long createDocument(DocumentCreateDTO dto);
}
