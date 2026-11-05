package com.tracefix.client;

import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.util.List;

/**
 * P0/P1 的 Mock AI 客户端。
 * 它不调用真实模型，只根据报错里的关键词返回固定结构，用于先跑通整条链路。
 * 真正实现放在 Python FastAPI 服务里，Java 通过 HTTP 调用。
 */
@Service
@ConditionalOnProperty(name = "ai.mock", havingValue = "true", matchIfMissing = true)
public class MockAiClient implements AiClient {

    @Override
    public AiDiagnosisResult diagnose(String inputTrace, String inputContext) {
        String text = inputTrace == null ? "" : inputTrace;

        if (text.contains("Access denied")) {
            return build(
                    "数据库密码或权限错误",
                    "java.sql.SQLException",
                    "Access denied for user '{user}'@'{host}' (using password: YES)",
                    "ERR-MYSQL-0002",
                    "检查 application.yml 的 username/password，确认 MySQL 用户权限",
                    new BigDecimal("0.82")
            );
        }

        if (text.contains("Connection refused")) {
            return build(
                    "数据库端口不可达，常见于 SSH 隧道未启动",
                    "java.net.ConnectException",
                    "Connection refused: no further information",
                    "ERR-MYSQL-0001",
                    "检查 SSH 隧道、MySQL 是否启动、端口是否正确",
                    new BigDecimal("0.78")
            );
        }

        if (text.contains("Invalid bound statement")) {
            return build(
                    "Mapper XML 的 namespace 或 id 与接口方法不匹配",
                    "org.apache.ibatis.binding.BindingException",
                    "Invalid bound statement (not found): {mapperMethod}",
                    "ERR-MYBATIS-0001",
                    "对齐 XML namespace 和方法 id，检查 mapper-locations 与 target/classes",
                    new BigDecimal("0.80")
            );
        }

        // 没有命中关键词时，不硬答，返回 NEED_INFO
        AiDiagnosisResult result = new AiDiagnosisResult();
        result.setTitle("信息不足，暂时无法给出可靠根因");
        result.setExtractedException("UNKNOWN");
        result.setExtractedMessage(firstLine(text));
        result.setConfidence(new BigDecimal("0.30"));
        result.setMissingInfo(List.of(
                "完整堆栈（含 Caused by）",
                "JDK / Spring Boot / 依赖版本",
                "相关配置或代码片段",
                "报错前做了什么改动"
        ));
        return result;
    }

    /** 构造一个命中的 Mock 诊断结果。 */
    private AiDiagnosisResult build(String cause, String exception, String message,
                                    String caseId, String fix, BigDecimal confidence) {
        AiDiagnosisResult result = new AiDiagnosisResult();
        result.setTitle(cause);
        result.setExtractedException(exception);
        result.setExtractedMessage(message);
        result.setConfidence(confidence);
        result.setRootCause(cause);
        result.setFixSteps(fix);
        result.setVerification("按修复步骤操作后重新调用接口，确认不再出现原报错");
        result.setMatchedCaseIds(List.of(caseId));
        return result;
    }

    /** 取报错第一行，避免把整段堆栈塞进消息字段。 */
    private String firstLine(String text) {
        int index = text.indexOf('\n');
        return index < 0 ? text : text.substring(0, index);
    }
}
