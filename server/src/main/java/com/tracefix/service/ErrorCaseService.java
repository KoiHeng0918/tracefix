package com.tracefix.service;

import com.tracefix.dto.CasePromoteDTO;
import com.tracefix.dto.CaseReviewDTO;
import com.tracefix.dto.ErrorCaseCreateDTO;
import com.tracefix.entity.QaErrorCase;

import java.util.List;

/**
 * 案例库业务接口。
 * 案例只存“已验证的解决方案”，不是每条报错都直接入库。
 */
public interface ErrorCaseService {
    /** 手动导入一条案例。 */
    Long importCase(ErrorCaseCreateDTO dto);

    /** 查询案例列表。 */
    List<QaErrorCase> listCases();

    /** 按 ID 查询案例。 */
    QaErrorCase getCase(Long id);

    /** 审核案例状态。 */
    QaErrorCase review(CaseReviewDTO dto);

    /** 已解决工单生成案例草稿。 */
    Long promote(CasePromoteDTO dto);
}
