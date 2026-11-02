# TraceFix — Java 报错诊断与案例库

TraceFix 是一个面向 Java 开发者的报错诊断系统：粘贴真实报错后，系统解析堆栈、从结构化案例库中检索相似问题，生成带证据的诊断（原因、排查、修复、验证），并由人工确认修复是否有效。确认有效的案例回流到案例库，形成可复用的数据资产。

> 当前阶段：P0 的 Java 骨架、数据库模型、案例导入/查询接口已完成；诊断链路、Python AI 服务和评测体系正在开发。

## 解决什么问题

Java 报错排查通常有三个痛点：

1. 堆栈很长，新手不知道哪一行才是自己的代码。
2. 通用大模型的回答看起来合理，但缺少证据，无法确认是否适用于当前版本和框架。
3. 问题解决后经验留在聊天记录里，同类报错下次还要重新查。

TraceFix 把“报错—原因—修复—验证”整理成结构化案例，让诊断有证据、可确认、可复用。

## 核心流程

```text
提交报错
  → 解析异常类型 / 消息 / 堆栈帧 / 指纹
  → 从案例库检索相似案例（精确匹配 + 语义检索）
  → 生成结构化诊断：原因 / 排查 / 修复 / 验证 / 引用
  → 人工确认：原因对不对、修好没有
  → 修好：沉淀为新案例；没修好：转人工 / 记为负例
```

## 功能状态

| 模块 | 状态 | 说明 |
|---|---|---|
| 文档录入 | 已实现 | `POST /doc/upload`，P1 原始资料 |
| 案例库 | 已实现 | 结构化报错案例，支持导入和查询 |
| 诊断记录 | 数据模型已建 | 记录输入、AI 诊断、人工确认和状态流转 |
| 报错诊断 | 开发中 | 解析、检索、结构化输出、引用校验 |
| 黄金评测集 | 规划中 | 60 条真实场景，dev/test/holdout 拆分 |
| 前端页面 | 规划中 | 单页 HTML，提交报错 + 查看诊断 + 确认结果 |
| LangGraph 编排 | P1 规划 | 诊断状态图、条件分支、重试和人工中断 |

## 技术架构

```text
浏览器（单页 HTML）
   │ HTTP
Java 主服务（Spring Boot + MyBatis-Plus）
   │  ├─ 案例/诊断记录/人工确认（MySQL）
   │  ├─ 输入校验、缓存、限流（Redis）
   │  └─ HTTP 调用 Python AI 服务
   │
Python AI 服务（FastAPI）
   ├─ 堆栈解析 / 指纹
   ├─ 混合检索（FAISS + 全文 + 元数据）
   ├─ 结构化诊断生成
   └─ 引用校验 / 置信度判断
   │
MySQL（事实来源） ── FAISS（派生索引，可重建）
   │
RabbitMQ（批量导入、索引重建、评测任务）
```

Java 负责工程化与业务状态，Python 负责解析、检索和模型调用；MySQL 是事实来源，FAISS 索引可随时重建。

## 技术栈

- Java 主服务：Spring Boot 4.1.2、MyBatis-Plus 3.5.18.1
- 数据：MySQL、Redis、RabbitMQ
- Python AI 服务：FastAPI、FAISS、DeepSeek、通义 text-embedding-v3
- 诊断编排：LangGraph（P1，用于条件分支、重试和人工中断）
- 前端：单文件 HTML + JS，同源部署
- 评测：Python 脚本 + 黄金集 + CI（规划中）

## 数据模型

三张核心表：

| 表 | 作用 |
|---|---|
| `qa_document` | 原始资料/长文档，P1 使用 |
| `qa_error_case` | 结构化报错案例：异常类型、根因、修复步骤、验证方式、来源 |
| `qa_diagnosis_ticket` | 每次诊断的记录：输入、AI 诊断、置信度、人工确认、处理状态 |

案例库与诊断记录通过 `matched_case_ids` 和 `source_ticket_id` 逻辑关联，不建物理外键，避免高写入日志表被外键约束拖慢。

## API

| 方法 | 路径 | 状态 | 说明 |
|---|---|---|---|
| GET | `/api/health` | 已实现 | 健康检查 |
| POST | `/doc/upload` | 已实现 | 文档录入（P1） |
| POST | `/case/import` | 已实现 | 导入一条案例 |
| GET | `/case/list` | 已实现 | 查询案例列表 |
| POST | `/diagnosis/analyze` | 规划中 | 提交报错并诊断 |
| POST | `/diagnosis/confirm` | 规划中 | 人工确认根因/修复效果 |

## 快速开始

环境要求：JDK 17、Maven、MySQL 8。

1. 创建 `tracefix` 数据库，执行 `server/sql/schema.sql`。
2. 复制 `server/src/main/resources/application-example.yml` 为 `application.yml`，填入本地数据库/Redis/RabbitMQ 配置。
3. 启动 `TraceFixApplication`。
4. 访问 `GET /api/health`，返回 `ok` 即启动成功。

开发环境数据库通过 SSH 隧道访问，真实密码不进入仓库。

## 项目结构

```text
tracefix/
├── data/                    知识库原始资料
├── docs/
│   └── PRD.md               产品需求说明书
├── server/
│   ├── sql/
│   │   ├── schema.sql       三张核心表
│   │   └── reset_v2.sql     本地重建库脚本
│   └── src/main/java/com/tracefix/
│       ├── common/          统一返回结构
│       ├── config/          MyBatis-Plus 配置
│       ├── controller/      健康检查、文档、案例接口
│       ├── dto/             请求参数
│       ├── entity/          实体
│       ├── mapper/          Mapper
│       └── service/         业务层
└── README.md
```

## Roadmap

### P0：先跑通案例库和诊断数据模型

- Java 骨架、MySQL/Redis/RabbitMQ 连通
- 案例表、诊断记录表
- 案例导入/查询接口
- 5–20 条真实报错案例
- 诊断记录创建 + Mock AI 诊断

### P1：接入真实诊断链路

- Python FastAPI 服务
- 堆栈解析、指纹、混合检索
- DeepSeek 结构化诊断 + 引用校验
- LangGraph 诊断编排：
  - 证据充分性判断
  - 信息不足时追问
  - 引用校验失败时重试/降级
  - 人工中断和升级
- 诊断记录状态流转 + 人工确认
- 最小前端页面

### P2：把效果做成可证明的

- 60 条黄金评测集，dev/test/holdout 拆分
- 检索指标：Recall@5、MRR
- 诊断指标：根因准确率、引用正确率、答案忠实度、abstain 准确率
- CI 分层回归
- 部署上线

## 设计取舍

**为什么只做报错诊断，不做通用问答？**
通用 Java 问答容易被通用大模型替代；报错诊断有具体输入、可验证结果、可沉淀案例，更适合做成一个有数据资产的项目。

**为什么检索是证据层，不是产品本身？**
诊断需要引用历史案例，不能只靠模型记忆；但检索只是“找证据”。指纹精确命中时可以直接返回案例，没有证据时必须明确说信息不足，而不是硬答。

## 开发记录

- Maven 中央仓库不可用 → 配置阿里云镜像。
- 数据库公网连接超时 → 使用 SSH 隧道访问。
- MyBatis-Plus 3.5.9+ 分页插件拆分 → 手动引入 `mybatis-plus-jsqlparser`。
- 命令行 Maven 需指定 JDK 17 的 `JAVA_HOME`。
