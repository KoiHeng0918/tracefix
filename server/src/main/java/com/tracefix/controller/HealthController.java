package com.tracefix.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 健康检查接口。
 * 用于确认 Java 主服务已经启动。
 */
@RestController
public class HealthController {

    @GetMapping("/api/health")
    public String health() {
        return "ok";
    }
}
