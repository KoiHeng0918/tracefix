# DevQA — Java 开发者问答与报错诊断 Agent

面向 Java 开发者的知识问答 + 报错诊断 Agent：问 Java 知识、贴报错日志，得到带引用来源的回答与排查建议。

**架构**：Java 主服务（Spring Boot 3）+ Python AI 引擎（FastAPI + LangChain/LangGraph），同步 HTTP + 异步 RabbitMQ 双通道。

## 技术栈

Spring Boot 3 · MyBatis-Plus · MySQL · Redis · RabbitMQ · FastAPI · LangChain/LangGraph · FAISS · DeepSeek · 通义 embedding

## 项目进度

- [x] 2026-11-01：调通 DeepSeek API（curl 返回正常）
- [x] 2026-11-01：初始化仓库，创建知识库目录结构（data/01-11）
- [ ] D2：Java 主服务骨架（Spring Boot 3 + MyBatis-Plus + MySQL + Redis + RabbitMQ 连通）
- [ ] D3：Python 服务四件套跑通（FastAPI + DeepSeek + 通义 embedding + FAISS）
- [ ] D4：文档入库管道（解析 → 分块 → 向量化 → FAISS 索引 + MySQL 文档表）
- [ ] D5：LangGraph Agent（检索 + 生成 + 报错诊断节点）
- [ ] D6：Java ↔ Python 联动（HTTP 同步问答 + RabbitMQ 异步入库/日志）
- [ ] D7：Docker Compose 部署 5 服务 + Nginx + HTTPS + 前端页

## 知识库目录

```
data/
├── 01-spring/          Spring / SpringBoot 笔记
├── 02-ssm-mybatis/     MyBatis / SSM 整合
├── 03-microservices/   Spring Cloud / Nacos
├── 04-redis/           Redis 数据结构 / 缓存 / 分布式锁
├── 05-rabbitmq/        交换机模型 / 可靠投递 / 死信
├── 06-mysql/           索引 / 事务 / 锁 / 优化
├── 07-jvm/             内存 / GC / 类加载
├── 08-concurrency/     JUC / 线程池 / AQS
├── 09-network/         TCP / HTTP
├── 10-interview/       高频面试题
└── 11-errors/          经典报错与排查（诊断 Agent 专用）
```

## 踩坑记录

（每解决一个重复出现的报错，记到这里：现象 → 原因 → 解决）
