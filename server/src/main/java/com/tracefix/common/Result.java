package com.tracefix.common;

import lombok.Data;

/**
 * 统一返回结构：{ code, message, data }。
 * code=0 表示成功，非 0 表示失败。
 */
@Data
public class Result<T> {
    /** 业务状态码 */
    private Integer code;

    /** 提示信息 */
    private String message;

    /** 返回数据 */
    private T data;

    public static <T> Result<T> success(T data) {
        Result<T> r = new Result<>();
        r.code = 0;
        r.message = "success";
        r.data = data;
        return r;
    }

    public static <T> Result<T> error(Integer code, String message) {
        Result<T> r = new Result<>();
        r.code = code;
        r.message = message;
        return r;
    }
}
