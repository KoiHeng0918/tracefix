# DevQA — Java 开发者问答与报错诊断 Agent

面向 Java 开发者的知识问答 + 报错诊断 Agent：问 Java 知识、贴报错日志，得到带引用来源的回答与排查建议。

**架构**：Java 主服务（Spring Boot 4.1.2）+ Python AI 引擎（FastAPI + LangChain/LangGraph），同步 HTTP + 异步 RabbitMQ 双通道。

## 技术栈

Spring Boot 4.1.2 · MyBatis-Plus 3.5.18 · MySQL · Redis · RabbitMQ · FastAPI · LangChain/LangGraph · FAISS · DeepSeek · 通义 embedding

## 项目进度

- [x] 2026-11-01：调通 DeepSeek API（curl 返回正常）
- [x] 2026-11-01：初始化仓库，创建知识库目录结构（data/01-11）
- [x] 2026-11-01：Java 主服务骨架，MySQL/Redis/RabbitMQ 连通，health 接口验证通过
- [x] 2026-11-02：文档录入接口（DTO 校验 → Service 落库 PENDING），第一条文档真实写入
- [ ] D3：Python 服务四件套跑通（FastAPI + DeepSeek + 通义 embedding + FAISS）
- [ ] D4：文档入库管道（解析 → 分块 → 向量化 → FAISS 索引 + MQ 异步链路）
- [ ] D5：LangGraph Agent（检索 + 生成 + 报错诊断节点）
- [ ] D6：Java ↔ Python 联动（HTTP 同步问答 + RabbitMQ 异步入库/日志）
- [ ] D7：部署上线 + Nginx + HTTPS + 前端聊天页

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

## 配置说明

含真实密码的 `application.yml` 不入库（见 .gitignore）；新环境复制 `application-example.yml` 为 `application.yml` 后填入自己的连接信息。数据库开发通过 SSH 隧道访问，3306/6379 不对公网暴露。

## 踩坑记录

1. **Maven 依赖下载卡死**：默认中央仓库在当前网络下不可用 → 配置 `~/.m2/settings.xml` 使用阿里云镜像解决。
2. **数据库公网连不上（10060 超时）**：数据库只监听内部回环地址 → 改用 SSH 隧道（本地 13306/16379 转发到服务器内部），同时避免端口暴露公网。
3. **PaginationInnerInterceptor 找不到类**：MyBatis-Plus 3.5.9 起将依赖 JSqlParser 的分页插件拆分为独立模块，starter 默认不引入 → 手动添加 `mybatis-plus-jsqlparser` 依赖。
