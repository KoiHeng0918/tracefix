# TraceFix — Java 报错诊断与案例库

把一条真实 Java 报错，变成一张有证据、可人工确认、可沉淀复用的诊断记录。

> 项目原名 DevQA，v2 起改名 TraceFix；GitHub 仓库和本地目录可后续改为 `tracefix/`。

**当前定位**：只做报错诊断，不做通用 Java 问答、不自动改代码、不自动关闭问题。
**当前阶段**：Java 主服务骨架和文档录入已完成；诊断、案例库、评测尚未实现。项目方向已从 v1 的“通用问答 + RAG”收敛到“报错诊断 + 人工确认 + 案例回流”。

## 技术栈

- Java 主服务：Spring Boot 4.1.2、MyBatis-Plus 3.5.18.1
- 数据：MySQL（业务数据）、Redis（缓存/限流）、RabbitMQ（批量导入/索引重建等异步任务）
- Python AI 子服务：FastAPI、FAISS、DeepSeek、通义 text-embedding-v3
- 前端：单文件 HTML + JS，放 Java 的 static 目录同源部署
- 评测：Python 脚本 + 黄金集 + CI（规划中）

LangGraph 暂不使用。当前诊断链路用普通 Service 就能讲清，先不引入多节点编排。

## 核心闭环（目标）

```
提交报错
  → 解析异常类型 / 消息 / 堆栈帧 / 指纹
  → 从案例库找相似案例（精确匹配 + 语义检索）
  → AI 输出结构化诊断：原因 / 排查 / 修复 / 验证 / 引用
  → 人工确认：原因对不对、修好没有
  → 修好：沉淀为新案例；没修好：转人工 / 记为负例
```

目前只完成了最左侧的 Java 骨架和文档录入，诊断链路尚未实现。

## 项目进度

- [x] 2026-11-01：调通 DeepSeek API（curl 返回正常）
- [x] 2026-11-01：初始化仓库，创建知识库目录结构（data/01-11）
- [x] 2026-11-01：Java 主服务骨架，MySQL/Redis/RabbitMQ 连通，health 接口验证通过
- [x] 2026-11-02：文档录入接口（DTO 校验 → Service 落库 PENDING），第一条文档真实写入
- [x] 2026-11-02：方向收敛为“报错诊断 + 人工确认 + 案例回流”，重写 PRD 与协作指南
- [x] 2026-11-02：项目改名 TraceFix，Java 包名改为 `com.tracefix`，Maven artifact 改为 `tracefix-server`
- [x] 2026-11-02：清理 v1 的 `qa_question_log` 表定义、实体和 Mapper；`qa_document` 保留为 P1 原始资料
- [x] 2026-11-02：`schema.sql` 已包含 v2 三张表：`qa_document`、`qa_error_case`、`qa_diagnosis_ticket`
- [ ] 下一步：备份旧库，执行 `server/sql/reset_v2.sql` + `server/sql/schema.sql`，重建 `tracefix` 库
- [ ] 下一步：为 `qa_error_case`、`qa_diagnosis_ticket` 写实体和 Mapper
- [ ] 下一步：整理 20 条真实报错案例 + 20 条黄金评测用例
- [ ] 下一步：Python 服务 MVP（解析 + 指纹 + 检索 + 结构化诊断 + abstain）
- [ ] 下一步：诊断记录状态流转 + 人工确认 + 最小页面
- [ ] 后续：60 条黄金集、CI 评测、部署上线

## 目录结构

```
tracefix/
├── data/                    知识库原始资料（11-errors 是诊断主线的重点）
├── docs/
│   └── PRD.md               产品需求说明书 v2.0
├── server/
│   ├── sql/
│   │   ├── schema.sql       v2 三张表：qa_document / qa_error_case / qa_diagnosis_ticket
│   │   ├── reset_v2.sql     重建 tracefix 库（会删除旧库，需手动执行）
│   │   └── migration_v2_cleanup.sql  只删 qa_question_log 的可选脚本
│   └── src/main/java/com/tracefix/
│       ├── common/          统一返回结构
│       ├── config/          MyBatis-Plus 配置
│       ├── controller/      health + 文档录入
│       ├── dto/             请求参数
│       ├── entity/          实体
│       ├── mapper/          Mapper
│       └── service/         业务层
└── README.md
```

> 本地目录当前仍叫 `devqa/`，GitHub 仓库名也可以先不改；代码包名已经是 `com.tracefix`。

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
└── 11-errors/          经典报错与排查（诊断主线的核心素材）
```

> 当前 P0 只做 `11-errors` 相关的结构化案例；其他目录是后续资料，不是第一优先级。

## 配置说明

含真实密码的 `application.yml` 不入库（见 `.gitignore`）；新环境复制 `application-example.yml` 为 `application.yml` 后填入自己的连接信息。数据库开发通过 SSH 隧道访问，3306/6379 不对公网暴露。

## 数据库说明

- `qa_document`：P1 原始资料表，当前保留；`/doc/upload` 仍可用。
- `qa_question_log`：v1 问答日志，已从代码和 `schema.sql` 删除；实际库如需清理，先备份，再执行 `server/sql/migration_v2_cleanup.sql`。
- `qa_error_case` / `qa_diagnosis_ticket`：v2 目标表，建表语句已写入 `schema.sql`；实际数据库尚未重建，对应实体和接口还没写。
- 重建数据库：先备份旧库，再执行 `server/sql/reset_v2.sql` 创建 `tracefix` 库，最后执行 `server/sql/schema.sql`。

## 踩坑记录

1. **Maven 依赖下载卡死**：默认中央仓库在当前网络下不可用 → 配置 `~/.m2/settings.xml` 使用阿里云镜像解决。
2. **数据库公网连不上（10060 超时）**：数据库只监听内部回环地址 → 改用 SSH 隧道（本地 13306/16379 转发到服务器内部），同时避免端口暴露公网。
3. **PaginationInnerInterceptor 找不到类**：MyBatis-Plus 3.5.9 起将依赖 JSqlParser 的分页插件拆分为独立模块，starter 默认不引入 → 手动添加 `mybatis-plus-jsqlparser` 依赖。
4. **命令行 Maven 用错 JDK**：系统默认 JDK8，命令行需指定 JDK17 的 `JAVA_HOME`；IDEA 的红线以 `mvn compile` 结果为准。

## 下一步

1. 备份旧库，执行 `server/sql/reset_v2.sql` + `server/sql/schema.sql`，创建 `tracefix` 库。
2. 为 `qa_error_case`、`qa_diagnosis_ticket` 写实体和 Mapper。
3. 整理 20 条真实报错案例，先跑通案例入库和查询。
4. 写 Python 诊断 MVP，先用固定 JSON 跑通 Java ↔ Python 链路，再接真实检索和模型。
5. 做人工确认和最小页面，跑通一条完整闭环；再补黄金集和 CI。
