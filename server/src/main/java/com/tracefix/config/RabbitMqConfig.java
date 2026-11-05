package com.tracefix.config;

import org.springframework.amqp.core.Queue;
import org.springframework.amqp.core.QueueBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * P2 异步任务队列骨架：
 * - 批量导入案例
 * - 重建索引
 * - 评测任务
 * 诊断主链路仍然走同步 HTTP，不把实时请求塞进 MQ。
 */
@Configuration
public class RabbitMqConfig {

    public static final String CASE_IMPORT_QUEUE = "tracefix.case.import";
    public static final String INDEX_REBUILD_QUEUE = "tracefix.index.rebuild";
    public static final String EVAL_JOB_QUEUE = "tracefix.eval.job";

    @Bean
    public Queue caseImportQueue() {
        return QueueBuilder.durable(CASE_IMPORT_QUEUE).build();
    }

    @Bean
    public Queue indexRebuildQueue() {
        return QueueBuilder.durable(INDEX_REBUILD_QUEUE).build();
    }

    @Bean
    public Queue evalJobQueue() {
        return QueueBuilder.durable(EVAL_JOB_QUEUE).build();
    }
}
