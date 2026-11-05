package com.tracefix.common;

import lombok.Getter;

/**
 * 业务异常。
 * Service 里发现业务规则不满足时抛出，由 GlobalExceptionHandler 统一转成 Result。
 */
@Getter
public class BizException extends RuntimeException {
    /** 业务状态码，默认 400 */
    private final int code;

    public BizException(String message) {
        this(400, message);
    }

    public BizException(int code, String message) {
        super(message);
        this.code = code;
    }
}
