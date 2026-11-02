package com.tracefix.service.impl;

import com.tracefix.dto.ErrorCaseCreateDTO;
import com.tracefix.entity.QaErrorCase;
import com.tracefix.mapper.QaErrorCaseMapper;
import com.tracefix.service.ErrorCaseService;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class ErrorCaseServiceImpl implements ErrorCaseService {

    @Autowired
    private QaErrorCaseMapper qaErrorCaseMapper;

    @Override
    public Long importCase(ErrorCaseCreateDTO dto) {
        QaErrorCase errorCase = new QaErrorCase();
        BeanUtils.copyProperties(dto, errorCase);
        errorCase.setStatus("ACTIVE");
        errorCase.setQualityScore(3);
        errorCase.setHitCount(0);
        qaErrorCaseMapper.insert(errorCase);
        return errorCase.getId();
    }

    @Override
    public List<QaErrorCase> listCases() {
        return qaErrorCaseMapper.selectList(null);
    }
}
