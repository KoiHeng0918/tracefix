# TraceFix Finish Version 功能矩阵

> 目标：覆盖 P0–P2，不包含 P3 多用户。
> 当前：框架可运行，AI 为 Mock，RAG/LangGraph/Redis/MQ 为骨架。

## P0

| 功能 | 接口 | 状态 | 说明 |
|---|---|---|---|
| 健康检查 | `GET /api/health` | 已实现 | — |
| 案例导入 | `POST /case/import` | 已实现 | 单条导入 |
| 案例列表 | `GET /case/list` | 已实现 | 无分页 |
| 案例详情 | `GET /case/detail` | 已实现 | — |
| 诊断提交 | `POST /diagnosis/analyze` | 已实现 | Mock AI |
| 诊断列表 | `GET /diagnosis/ticket/list` | 已实现 | — |
| 诊断详情 | `GET /diagnosis/ticket/detail` | 已实现 | — |
| 人工确认 | `POST /diagnosis/confirm` | 已实现 | 状态流转 |
| 案例草稿回流 | `POST /case/promote` | 已实现 | RESOLVED → DRAFT |
| 案例审核 | `POST /case/review` | 已实现 | 改状态 |
| 最小前端 | `/` | 已实现 | 单页 HTML |

## P1

| 功能 | 位置 | 状态 | 说明 |
|---|---|---|---|
| 堆栈解析 | `ai/parsers/stack_parser.py` | 骨架 | 异常/帧/归一化/指纹 |
| 案例检索 | `ai/retrieval/case_retriever.py` | 骨架 | FAISS TODO |
| RAG | `ai/main.py` + `CaseRetriever` | 骨架 | 未接真实检索 |
| LangChain | `ai/requirements.txt` | 未接入 | 预留依赖 |
| LangGraph | `ai/graph/diagnosis_graph.py` | 骨架 | 条件分支已画 |
| URL 导入 | `POST /case/import/url` | 未实现 | 后续加 |
| 批量导入 | `POST /case/import/batch` | 未实现 | 后续加 |
| 知识库导入/导出 | `/case/library/*` | 未实现 | 后续加 |

## P2

| 功能 | 位置 | 状态 | 说明 |
|---|---|---|---|
| Redis 缓存 | `CacheService` | 骨架 | 未接业务 |
| 限流 | 未实现 | 未实现 | 后续加 |
| RabbitMQ 队列 | `RabbitMqConfig` | 骨架 | 队列声明 |
| 异步导入/索引 | 未实现 | 未实现 | 后续加 |
| 失败重试 | 未实现 | 未实现 | 后续加 |
| 评测脚本 | `eval/run_eval.py` | 骨架 | 黄金集为空 |
| CI | 未实现 | 未实现 | 后续加 |

## P3（不包含）

- 用户表、登录、注册
- 角色权限、数据隔离
- 多租户
- 高并发压测

这些等单用户闭环和评测稳定后再做。
