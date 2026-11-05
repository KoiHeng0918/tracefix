package com.tracefix.client;

/**
 * AI 诊断客户端接口。
 * 当前实现是 MockAiClient；以后可以替换成调用 Python /ai/diagnose 的实现。
 */
public interface AiClient {

    /**
     * 根据报错原文和补充信息返回结构化诊断。
     * 返回值不是数据库实体，而是 Java 和 AI 服务之间的内部结果对象。
     */
    AiDiagnosisResult diagnose(String inputTrace, String inputContext);
}
