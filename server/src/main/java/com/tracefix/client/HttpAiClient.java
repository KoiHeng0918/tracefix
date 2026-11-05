package com.tracefix.client;

import com.tracefix.common.BizException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.http.MediaType;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;
import tools.jackson.databind.ObjectMapper;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * 调用 Python FastAPI 的 AI 客户端。
 * 当 ai.mock=false 时启用，替换 MockAiClient。
 */
@Service
@ConditionalOnProperty(name = "ai.mock", havingValue = "false")
public class HttpAiClient implements AiClient {

    private final RestClient restClient;
    @Autowired
    private ObjectMapper objectMapper;


    // 构造一个restClient，使用builder

    //重点.requestFactory(new SimpleClientHttpRequestFactory())
    public HttpAiClient(@Value("${ai.base-url:http://127.0.0.1:8000}") String baseUrl) {
        this.restClient = RestClient.builder()
                .baseUrl(baseUrl)
                .requestFactory(new SimpleClientHttpRequestFactory())
                .build();
    }

    @Override
    public AiDiagnosisResult diagnose(String inputTrace, String inputContext) {
        Map<String, Object> request = new LinkedHashMap<>();
        request.put("trace", inputTrace);
        request.put("context", inputContext);
        try {
            String json = objectMapper.writeValueAsString(request);
            String response = restClient.post()
                    .uri("/ai/diagnose")
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(json)
                    .retrieve()
                    .body(String.class);
            return objectMapper.readValue(response, AiDiagnosisResult.class);
        } catch (Exception e) {
            throw new BizException(502, "调用 AI 服务失败：" + e.getMessage());
        }
    }


}
