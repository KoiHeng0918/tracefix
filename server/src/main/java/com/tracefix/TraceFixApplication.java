package com.tracefix;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * TraceFix 启动类。
 * 扫描 com.tracefix 下的 Spring 组件，并扫描 mapper 包。
 */
@SpringBootApplication
@MapperScan("com.tracefix.mapper")
public class TraceFixApplication {

    public static void main(String[] args) {
        SpringApplication.run(TraceFixApplication.class, args);
    }

}
