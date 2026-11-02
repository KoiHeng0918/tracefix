package com.tracefix.service;

import com.tracefix.dto.ErrorCaseCreateDTO;
import com.tracefix.entity.QaErrorCase;

import java.util.List;

public interface ErrorCaseService {
    Long importCase(ErrorCaseCreateDTO dto);

    List<QaErrorCase> listCases();
}
