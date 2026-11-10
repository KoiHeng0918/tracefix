# TraceFix — Java 报错诊断与案例库

TraceFix 是一个面向 Java 开发者的报错诊断系统：粘贴真实报错后，系统解析堆栈、从结构化案例库中检索相似问题，生成带证据的诊断（原因、排查、修复、验证），并由人工确认修复是否有效。确认有效的案例回流到案例库，形成可复用的数据资产。

> 当前阶段：Java ↔ Python 诊断链路已打通；Python 已接入 DeepSeek 结构化生成、Qwen Embedding、FAISS 向量检索和 LangGraph 编排；离线评测已建立 `dev/test/holdout` 三组数据。

## 解决什么问题

Java 报错排查通常有三个痛点：

1. 堆栈很长，新手不知道哪一行才是自己的代码。
2. 通用大模型的回答看起来合理，但缺少证据，无法确认是否适用于当前版本和框架。
3. 问题解决后经验留在聊天记录里，同类报错下次还要重新查。

TraceFix 把“报错—原因—修复—验证”整理成结构化案例，让诊断有证据、可确认、可复用。

## 核心流程

```text
提交报错
  → 解析异常类型 / 消息 / 指纹
  → 关键词检索 baseline + 向量检索
  → 候选案例
  → LangGraph 编排
  → DeepSeek 生成结构化诊断：原因 / 修复 / 验证 / 引用
  → citations 白名单校验
  → 人工确认：原因对不对、修好没有
  → 修好：生成案例草稿；审核后进入正式案例库
```

## 功能状态

| 模块 | 状态 | 说明 |
|---|---|---|
| 文档录入 | 已实现 | `POST /doc/upload`，P1 原始资料 |
| 案例库 | 已实现 | 导入、列表、详情、审核、工单回流 |
| 诊断记录 | 已实现 | 创建、列表、详情、人工确认 |
| Java → Python 通信 | 已实现 | `HttpAiClient` 调 FastAPI `/ai/diagnose` |
| 堆栈解析 | 已实现 | 异常类型、归一化消息、指纹 |
| Python 案例读取 | 已实现 | 从 MySQL 读取 `ACTIVE` 案例 |
| 关键词检索 | 已实现 | 异常类型匹配 + 消息关键词打分，作为 baseline |
| Embedding | 已实现 | 通义 `qwen3.7-text-embedding-flash`，1024 维 |
| FAISS 向量检索 | 已实现 | `IndexFlatIP` + L2 归一化，保存 `faiss.index` 和 `case_ids.json` |
| 诊断生成 | 已实现 | DeepSeek 输出结构化 JSON；包含字段完整性和引用校验 |
| LangGraph 编排 | 已实现 | retrieve → assess → generate → validate；证据不足走 ask/abstain |
| 黄金评测集 | 已建立 | 20 条：`dev 10 / test 5 / holdout 5` |
| Mock AI | 已实现 | `ai.mock=true` 时使用，便于离线调试 |
| 前端页面 | 最小页面 | 提交报错、查看诊断、人工确认 |
| RRF 混合检索 | 规划中 | 融合关键词和向量的排名 |
| Redis / RabbitMQ | 规划中 | 缓存、限流、异步导入和重建索引 |

## 评测结果

当前 20 条评测数据覆盖 7 个 `ACTIVE` 案例，使用 `Recall@5` 作为检索指标：

| split | cases | keyword Recall@5 | vector Recall@5 |
|---|---:|---:|---:|
| dev | 10 | 0.50 | 1.00 |
| test | 5 | 0.00 | 1.00 |
| holdout | 5 | 0.20 | 1.00 |

`Recall@5` 的含义：正确案例是否出现在检索结果前 5 条中。

评测解读：

- 关键词检索按空格分词，对中文自然语言和英文 `message_pattern` 的跨语言匹配能力弱，所以分数低。
- 向量检索通过 Embedding 把中文问题和英文案例映射到同一语义空间，因此对自然语言描述更稳定。
- 当前每组只有 5～10 条数据，`1.00` 只能说明当前样本上的效果，不能证明所有 Java 报错场景都有效。
- `dev` 用于调参，`test` 用于方案比较，`holdout` 最后验收；不要根据 `test` 或 `holdout` 的逐条结果反复调参。

## 技术架构

```text
浏览器（单页 HTML）
   │ HTTP
Java 主服务（Spring Boot + MyBatis-Plus）
   │  ├─ 案例 / 诊断记录 / 人工确认（MySQL）
   │  └─ HttpAiClient ──────────────┐
   │                                │ HTTP
   │                                ▼
   │                    Python AI 服务（FastAPI）
   │                      ├─ 堆栈解析 / 指纹
   │                      ├─ MySQL ACTIVE 案例读取
   │                      ├─ 关键词检索（baseline）
   │                      ├─ VectorRetriever + FAISS
   │                      └─ LangGraph + DeepSeek
   │
MySQL（事实来源）
FAISS index（可重建的派生索引）
Redis / RabbitMQ（规划中）
```

Java 负责业务状态和数据库写入，Python 负责解析、检索和模型调用。MySQL 是事实来源，FAISS 只作为可重建的派生索引。

## 技术栈

- Java 主服务：Spring Boot 4.1.2、MyBatis-Plus 3.5.18.1
- 数据：MySQL
- Python AI 服务：FastAPI、PyMySQL
- 编排：LangGraph
- 大模型：DeepSeek `deepseek-chat`
- Embedding：通义 `qwen3.7-text-embedding-flash`，1024 维
- 向量索引：FAISS `IndexFlatIP`（L2 归一化后等价余弦相似度）
- 前端：单文件 HTML + JS，同源部署
- 规划中：RRF、Redis、RabbitMQ

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
| GET | `/case/detail` | 已实现 | 案例详情 |
| POST | `/case/review` | 已实现 | 审核案例状态 |
| POST | `/case/promote` | 已实现 | 已解决工单生成案例草稿 |
| POST | `/diagnosis/analyze` | 已实现 | 提交报错并诊断；由 `ai.mock` 切换 Mock/Python |
| GET | `/diagnosis/ticket/list` | 已实现 | 查询诊断记录 |
| GET | `/diagnosis/ticket/detail` | 已实现 | 诊断记录详情 |
| POST | `/diagnosis/confirm` | 已实现 | 人工确认根因/修复效果 |

Python 服务额外提供：

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/ai/health` | Python 服务健康检查 |
| POST | `/ai/diagnose` | 解析、向量检索、LangGraph 编排并返回结构化诊断 |

## 快速开始

### 1. 准备 MySQL

1. 创建 `tracefix` 数据库。
2. 执行 `server/sql/schema.sql`。
3. 准备少量 `qa_error_case` 数据，状态为 `ACTIVE` 才会参与检索。

### 2. 安装 Python 依赖

```bash
cd ai
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 3. 配置环境变量

创建 `ai/.env`（不要提交到 Git）：

```text
MYSQL_HOST=127.0.0.1
MYSQL_PORT=13306
MYSQL_USER=你的用户名
MYSQL_PASSWORD=你的密码
MYSQL_DATABASE=tracefix
```

Embedding 和 DeepSeek 的密钥放在本机环境变量或 `.env` 中：

```text
DASHSCOPE_API_KEY=你的通义密钥
DEEPSEEK_API_KEY=你的 DeepSeek 密钥
```

不要把真实密钥写进 README、代码或 Git。

### 4. 构建 FAISS 索引

在 `ai` 目录执行：

```bash
.venv\Scripts\python.exe scripts\build_faiss_index.py
```

会生成：

```text
ai/retrieval/index/faiss.index
ai/retrieval/index/case_ids.json
```

`case_ids.json` 的下标必须和 FAISS 内部 ID 一致；重建索引时要同时重建这两个文件。

### 5. 启动 Python 服务

```bash
.venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000
```

### 6. 配置并启动 Java

复制：

```text
server/src/main/resources/application-example.yml
```

为：

```text
server/src/main/resources/application.yml
```

填入本地数据库配置，并确认：

```yaml
ai:
  base-url: http://127.0.0.1:8000
  mock: false
```

启动 `TraceFixApplication` 后访问：

```text
http://localhost:8080/
```

或检查：

```text
GET /api/health
GET http://127.0.0.1:8000/ai/health
```

开发环境数据库通过 SSH 隧道访问，真实密码不进入仓库。

### 7. 运行评测

在项目根目录执行：

```powershell
ai\.venv\Scripts\python.exe eval\run_eval.py --split dev
ai\.venv\Scripts\python.exe eval\run_eval.py --split test
ai\.venv\Scripts\python.exe eval\run_eval.py --split holdout
```

`holdout` 只用于最终验收，不要反复根据它调参。

## Mock AI 与真实 Python 的切换

```text
ai.mock=true  → MockAiClient
ai.mock=false → HttpAiClient → Python /ai/diagnose
```

`MockAiClient` 用于离线调试和跑通 Java 业务流程；`HttpAiClient` 用于真实检索链路。

当前 Python 的 `generate` 节点已经调用 DeepSeek，不再使用模板版。`validate_citations` 会过滤模型返回的 `citations`，只保留候选案例中真实存在的 `case_no`。

## 项目结构

```text
tracefix/
├── data/                    知识库原始资料和报错候选清单
├── docs/
│   ├── PRD.md               产品需求说明书
│   └── FEATURE_MATRIX.md    功能矩阵
├── ai/                      Python AI 服务
│   ├── main.py              FastAPI 入口
│   ├── parsers/             堆栈解析 / 指纹
│   ├── retrieval/           MySQL 案例读取、关键词检索、向量检索
│   │   ├── case_repository.py
│   │   ├── case_retriever.py
│   │   ├── vector_retriever.py
│   │   ├── embedding_client.py
│   │   └── index/           faiss.index / case_ids.json
│   ├── graph/               LangGraph 诊断编排
│   ├── scripts/             建索引、查询验证等开发脚本（不参与运行时）
│   └── tests/               Python 单元测试
├── eval/                    评测脚本与黄金集
│   ├── README.md            评测说明
│   ├── run_eval.py          评测入口
│   └── golden/cases.jsonl   20 条评测数据
├── server/
│   ├── sql/
│   │   ├── schema.sql       三张核心表
│   │   └── reset_v2.sql     本地重建库脚本
│   └── src/main/
│       ├── java/com/tracefix/
│       │   ├── client/      Mock AI / HTTP AI 客户端
│       │   ├── common/      统一返回、异常处理
│       │   ├── config/      MyBatis-Plus、RabbitMQ 配置
│       │   ├── controller/  health / case / diagnosis
│       │   ├── dto/         请求参数
│       │   ├── entity/      实体
│       │   ├── mapper/      Mapper
│       │   └── service/     业务层
│       └── resources/static/index.html  最小前端页
└── README.md
```

## 当前限制

- `ACTIVE` 案例只有 7 条，评测集只有 20 条，样本规模仍然小。
- 向量检索在这批数据上 `Recall@5=1.00`，不能直接外推到所有 Java 报错。
- 还没有做关键词与向量的 RRF 融合。
- Redis / RabbitMQ 还没有接入。
- 没有多用户、登录、权限系统和正式部署。
- FAISS 索引是派生数据，案例变化后需要重新构建。

## Roadmap

### P0：跑通业务闭环

- Java 骨架、MySQL 连通
- 案例表、诊断记录表
- 案例导入 / 查询 / 审核
- 诊断记录 + Mock AI
- 人工确认、案例回流

### P1：真实诊断链路

- Python FastAPI 服务
- 堆栈解析、指纹
- MySQL ACTIVE 案例读取
- 关键词检索 baseline
- LangGraph 诊断编排
- DeepSeek 结构化诊断
- 引用白名单校验

### P2：把效果做成可证明的

- 补充更多真实案例和评测数据
- 关键词 + 向量 RRF 融合
- Recall@5、MRR、Top1 准确率、引用正确率
- CI 分层回归
- 部署和演示

## 设计取舍

**为什么只做报错诊断，不做通用问答？**

通用 Java 问答容易被通用大模型替代；报错诊断有具体输入、可验证结果、可沉淀案例，更适合做成一个有数据资产的项目。

**为什么保留关键词检索？**

关键词检索是稳定、可解释、成本低的 baseline，也能在向量服务不可用时作为降级方案。向量检索负责语义泛化，后续可以用 RRF 融合两者排名。

**为什么检索是证据层，不是产品本身？**

诊断需要引用历史案例，不能只靠模型记忆；但检索只是“找证据”。指纹精确命中时可以直接返回案例，没有证据时必须明确说信息不足，而不是硬答。

## 开发记录

- Maven 中央仓库不可用 → 配置阿里云镜像。
- 数据库公网连接超时 → 使用 SSH 隧道访问。
- MyBatis-Plus 3.5.9+ 分页插件拆分 → 手动引入 `mybatis-plus-jsqlparser`。
- Java `RestClient` 与 Uvicorn 协议不匹配 → 使用 `SimpleClientHttpRequestFactory` 强制 HTTP/1.1。
- 关键词检索中文跨语言匹配差 → 接入 Qwen Embedding + FAISS。
- FAISS 只返回内部 ID → 保存 `case_ids.json`，用内部 ID 映射回 `case_no`。
- `dev/test/holdout` 三组评测已完成；holdout 只用于最终验收。
