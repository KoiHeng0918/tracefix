package com.tracefix.common;

import org.springframework.dao.DuplicateKeyException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

/**
 * 全局异常处理。
 * 把参数校验、业务异常、重复键和其他异常统一转成 Result，避免前端收到一堆 500 堆栈。
 */
@RestControllerAdvice
public class GlobalExceptionHandler {

    /** 处理 @Validated 参数校验失败。 */
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public Result<Void> handleValidation(MethodArgumentNotValidException e) {
        String message = e.getBindingResult().getFieldErrors().isEmpty()
                ? "参数校验失败"
                : e.getBindingResult().getFieldErrors().get(0).getDefaultMessage();
        return Result.error(400, message);
    }

    /** 处理业务异常，例如状态不允许、记录不存在。 */
    @ExceptionHandler(BizException.class)
    public Result<Void> handleBiz(BizException e) {
        return Result.error(e.getCode(), e.getMessage());
    }

    /** 处理唯一键冲突，例如 caseNo 重复。 */
    @ExceptionHandler(DuplicateKeyException.class)
    public Result<Void> handleDuplicate(DuplicateKeyException e) {
        return Result.error(409, "数据已存在，请检查案例编号或指纹");
    }

    /** 兜底异常。 */
    @ExceptionHandler(Exception.class)
    public Result<Void> handleOther(Exception e) {
        return Result.error(500, "服务内部错误：" + e.getMessage());
    }
}
