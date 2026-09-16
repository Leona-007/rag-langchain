# Campus RAG System

一个基于 FastAPI、LangChain 和 Qdrant 的校园知识库问答服务。系统支持用户认证、会话管理、Markdown/TXT 文档上传、向量检索、来源引用和 SSE 流式回答。

## 功能特性

- 邮箱注册、登录、JWT Access Token/Refresh Token 刷新
- 用户会话创建、查询、删除和历史消息查看
- Markdown/TXT 文档上传与本地保存
- 文档自动切分、中文向量化并写入 Qdrant
- 基于相似度检索的 RAG 问答
- 非流式 JSON 问答和 SSE 流式问答
- 返回回答引用的章节、小节、内容摘要和相似度
- 管理员删除知识库文档
- FastAPI 自动生成 Swagger/OpenAPI 文档

## 技术栈

| 层次 | 技术 |
| --- | --- |
| Web API | FastAPI、Uvicorn、SSE-Starlette |
| RAG 编排 | LangChain、LangChain Text Splitters |
| Embedding | HuggingFace `BAAI/bge-base-zh-v1.5`，CPU 推理 |
| LLM | DeepSeek、OpenAI 兼容接口或 Ollama，三选一 |
| 关系数据库 | PostgreSQL + SQLAlchemy Async + asyncpg |
| 向量数据库 | Qdrant |
| 认证 | JWT + bcrypt |
| Python | 3.10 或更高版本 |

## 系统架构

```text
客户端
	|
	v
FastAPI (/root)
	|-- 认证与权限 ------ PostgreSQL
	|-- 会话与消息 ------ PostgreSQL
	|-- 文档上传 -------- 本地 data/ + PostgreSQL 元数据
	|                      |
	|                      v
	|                 文本加载 -> Markdown 分段 -> 文本切分
	|                                      |
	|                                      v
	|                         HuggingFace Embedding -> Qdrant
	|
	`-- 问答 -> Qdrant 相似度检索 -> LLM -> 回答与来源
```

### 文档处理流程

1. 接收 `.md` 或 `.txt` 文件，文件大小限制为 10 MB。
2. 文件保存到 `data/`，文件名使用 UUID 前缀避免冲突。
3. 使用 Markdown 标题提取 `chapter` 和 `section` 元数据。
4. 使用递归文本切分器生成文本块。
5. 使用 `BAAI/bge-base-zh-v1.5` 生成 768 维向量并写入 Qdrant。
6. 在 PostgreSQL 中保存文档、文本块和 Qdrant point ID。

## 环境准备

需要提前安装并启动：

- Python 3.10+
- PostgreSQL 需要创建的数据库，例如 `campus_rag`
- Qdrant，默认监听 `localhost:6333`
- 一个可用的 LLM 提供商：DeepSeek、OpenAI 兼容 API 或 Ollama

推荐使用 [uv](https://docs.astral.sh/uv/) 管理虚拟环境和依赖。

### 安装依赖

```powershell
uv sync
```

首次使用 HuggingFace Embeddings 时会下载模型 `BAAI/bge-base-zh-v1.5`。模型默认运行在 CPU，首次启动或首次上传文档可能需要较长时间。

## 配置环境变量

在项目根目录创建 `.env`。下面是一个使用 DeepSeek 的最小示例：

```dotenv
APP_NAME=Campus RAG System
DEBUG=false

DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_postgres_password
DB_NAME=campus_rag

QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=campus_knowledge
QDRANT_VECTOR_SIZE=768

JWT_SECRET_KEY=replace-with-a-long-random-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=your-deepseek-api-key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat

CHUNK_SIZE=500
CHUNK_OVERLAP=50
RETRIEVER_TOP_K=3
SHOW_SOURCE=true
DATA_DIR=data
```

LLM 提供商可选值：

- `deepseek`：使用 `DEEPSEEK_*` 配置。
- `openai`：使用 `OPENAI_API_KEY`、`OPENAI_BASE_URL` 和 `OPENAI_MODEL`。
- 其他值：当前实现会回退到 Ollama，使用 `OLLAMA_BASE_URL` 和 `OLLAMA_MODEL`。

不要把 `.env`、API Key 或生产 JWT 密钥提交到版本库。项目配置中存在开发环境默认值，部署前应通过环境变量全部覆盖，并立即轮换任何曾经暴露过的密钥。

## 初始化与启动

应用启动时会自动创建 SQLAlchemy 模型对应的 PostgreSQL 表。首次部署可以额外运行初始化脚本创建管理员账号：

```powershell
uv run python scripts/init_admain.py
```

当前脚本内置的是开发环境管理员账号和密码，生产环境请先修改脚本或改用更安全的管理员创建流程，避免使用默认凭据。

启动开发服务器：

```powershell
uv run uvicorn src.main:app --reload
```

服务启动后：

- API 根地址：`http://localhost:8000/`
- Swagger UI：`http://localhost:8000/docs`
- ReDoc：`http://localhost:8000/redoc`

所有业务接口都带有 `/root` 前缀，例如注册接口为 `POST /root/register`。

## API 概览

除注册和登录外，接口需要携带：

```http
Authorization: Bearer <access_token>
```

### 认证

| 方法 | 路径 | 说明 | 是否认证 |
| --- | --- | --- | --- |
| `POST` | `/root/register` | 注册用户 | 否 |
| `POST` | `/root/login` | 登录并获取 Access/Refresh Token | 否 |
| `POST` | `/root/refresh` | 刷新 Access Token | 否 |
| `GET` | `/root/me` | 获取当前用户信息 | 是 |

注册和登录请求体：

```json
{
	"email": "student@example.com",
	"password": "at-least-8-characters"
}
```

登录响应包含：

```json
{
	"access_token": "<jwt>",
	"refresh_token": "<jwt>",
	"token_type": "bearer"
}
```

### 会话与问答

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `POST` | `/root/sessions` | 创建会话 |
| `GET` | `/root/sessions` | 获取当前用户的会话列表 |
| `GET` | `/root/sessions/{session_id}` | 获取会话消息详情 |
| `DELETE` | `/root/sessions/{session_id}` | 删除会话 |
| `POST` | `/root/sessions/chat` | 非流式问答 |
| `POST` | `/root/stream` | SSE 流式问答 |

问答请求体：

```json
{
	"session_id": "session-uuid",
	"question": "宿舍几点关门？"
}
```

非流式响应示例：

```json
{
	"answer": "宿舍晚上 23:00 关门。",
	"sources": [
		{
			"content": "宿舍楼门禁时间为……",
			"chapter": "住宿管理",
			"section": "门禁时间",
			"score": 0.9123
		}
	]
}
```

流式接口通过 SSE 推送三类事件：

- `token`：回答文本片段。
- `source`：检索到的来源列表。
- `done`：本次生成结束。

### 文档管理

| 方法 | 路径 | 说明 | 权限 |
| --- | --- | --- | --- |
| `POST` | `/root/upload` | 上传 `.md` 或 `.txt` 文档 | 登录用户 |
| `GET` | `/root/` | 获取文档列表 | 登录用户 |
| `DELETE` | `/root/{document_id}` | 删除文档及其向量 | 管理员 |

上传示例：

```powershell
curl.exe -X POST http://localhost:8000/root/upload `
	-H "Authorization: Bearer <access_token>" `
	-F "file=@data/simple_university_doc.md"
```

文档状态通常经历 `indexing -> ready`；处理失败时为 `error`。删除操作会同时清理 Qdrant 向量、本地文件和 PostgreSQL 记录。

## 项目结构

```text
.
├── data/                  # 上传文档存储目录与示例文档
├── scripts/               # 数据库和管理员初始化脚本
├── src/
│   ├── api/               # FastAPI 路由：认证、聊天、文档
│   ├── db/                # SQLAlchemy Base、模型、异步会话
│   ├── rag/               # 加载、切分、Embedding、向量库、检索、生成
│   ├── schemas/           # Pydantic 请求和响应模型
│   ├── services/          # 认证外的业务服务逻辑
│   ├── utils/             # JWT 和密码哈希
│   ├── config.py          # pydantic-settings 配置
│   └── main.py            # FastAPI 应用入口
├── mcp_server.py          # MCP 服务预留入口
└── pyproject.toml         # 项目元数据和依赖
```

## 开发建议

- 修改数据库连接、Qdrant 地址或 LLM 配置时，优先通过 `.env` 覆盖默认值。
- 调整向量模型时，需要同步确认 `QDRANT_VECTOR_SIZE`，并重建对应 collection。
- 更新切分策略或 Embedding 模型后，已有文档不会自动重建索引，建议清理旧 collection 后重新上传。
- 生产环境建议使用数据库迁移工具管理表结构，而不是仅依赖启动时的 `create_all`。
- 当前聊天和文档索引包含同步的向量库调用，生产部署时应评估后台任务、超时和并发限制。

## 已知注意事项

- 目前没有内置测试套件和数据库迁移目录，部署前应补充接口、权限和 RAG 链路测试。
- CORS 当前只配置了 `localhost:8000` 和 `localhost:3000`，且允许的方法配置为 `GET`；如果前端跨域调用注册、上传或聊天接口，需要按实际域名和方法调整 `src/main.py`。
- 文档接口的路径较短且与认证、聊天路由同处 `/root` 下，接入前端时请以 Swagger/OpenAPI 为准。
- `mcp_server.py` 当前为空文件，MCP 能力尚未实现。

## License

当前仓库未声明开源许可证。
