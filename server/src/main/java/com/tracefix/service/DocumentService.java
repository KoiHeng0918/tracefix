package com.tracefix.service;

import com.tracefix.dto.DocumentCreateDTO;

/**
 * 原始资料业务接口（P1）。
 */
public interface DocumentService {
    /** 创建一条原始资料，返回主键。 */
    Long createDocument(DocumentCreateDTO dto);
}
