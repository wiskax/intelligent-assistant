# 📚 智能知识库助手 (RAG 系统)

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-teal.svg)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3+-green.svg)](https://github.com/langchain-ai/langchain)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 一个基于 **RAG（检索增强生成）** 技术的智能知识库助手，支持用户上传文档、自动向量化存储、语义检索和智能问答。系统采用 **混合检索（BM25 + 向量检索）** 技术，提供更精准的答案。

---

## ✨ 核心特性

- 📄 **文档上传**：支持 TXT、PDF、MD 格式，自动提取文本内容
- 🧠 **智能切分**：自动将长文档切分为语义完整的文本块
- 🔍 **混合检索**：结合 BM25 关键词检索 + 向量语义检索，精准匹配
- 💬 **RAG 问答**：基于检索结果生成有依据的、准确的回答
- 📎 **来源追溯**：回答附参考来源，可验证答案可信度
- 👤 **多用户隔离**：每个用户的文档和对话完全隔离
- 🔐 **JWT 认证**：安全的用户注册/登录系统
- 🌊 **流式前端**：打字机效果，实时展示回答生成过程
- 🐳 **一键部署**：支持 Docker Compose 快速启动

---

## 🛠️ 技术栈

| 类别 | 技术 |
|------|------|
| **Web 框架** | FastAPI, Uvicorn |
| **数据库** | PostgreSQL + SQLAlchemy (异步) |
| **向量数据库** | ChromaDB |
| **AI 框架** | LangChain, LangChain-Community |
| **LLM 接口** | 智谱AI (ChatGLM) / 兼容 OpenAI API |
| **检索算法** | BM25 + 向量语义检索 (混合检索) |
| **认证** | JWT (python-jose) |
| **前端** | HTML + CSS + JavaScript (原生) |
| **部署** | Docker, Docker Compose |

---

## 📊 系统架构图
┌─────────────────────────────────────────────────────────────────┐
│ 用户浏览器 │
│ (templates/index.html) │
└─────────────────────────┬───────────────────────────────────────┘
│ WebSocket / HTTP
┌─────────────────────────▼───────────────────────────────────────┐
│ FastAPI 后端 │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐ │
│ │ Auth API │ │ Documents │ │ Chat API │ │
│ │ 注册/登录/JWT │ │ 上传/列表 │ │ RAG 智能问答 │ │
│ └──────────────┘ └──────────────┘ └──────────────────────┘ │
└─────────────────────────┬───────────────────────────────────────┘
│
┌─────────────────────────▼───────────────────────────────────────┐
│ 业务服务层 │
│ ┌──────────────────┐ ┌──────────────────────────────────┐ │
│ │ Auth Service │ │ Document Service │ │
│ │ 密码加密/JWT │ │ 文档记录/状态管理 │ │
│ └──────────────────┘ └──────────────────────────────────┘ │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ Vector Service (向量服务) │ │
│ │ 文档加载 → 切分 → 向量化 → 存储 → 检索 │ │
│ └──────────────────────────────────────────────────────────┘ │
└─────────────────────────┬───────────────────────────────────────┘
│
┌─────────────────────────▼───────────────────────────────────────┐
│ 数据存储层 │
│ ┌─────────────┐ ┌─────────────┐ ┌──────────────────────┐ │
│ │ PostgreSQL │ │ ChromaDB │ │ Uploads │ │
│ │ 用户/文档 │ │ 向量索引 │ │ 原始文件 │ │
│ └─────────────┘ └─────────────┘ └──────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
---

## 🚀 快速开始

### 前置要求

- Python 3.11+
- Docker (用于 PostgreSQL)
- 智谱AI API Key

### 1️⃣ 克隆项目

```bash
git clone https://github.com/wiskax/intelligent-assistant.git
cd intelligent-assistant

---创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

---安装依赖
pip install -r requirements.txt

---配置环境变量
创建.env文件：
# 数据库
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/intelligent_assistant

# JWT
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# LLM (智谱AI)
ZHIPU_API_KEY=your_zhipu_api_key_here

---启动postgreSQL(Docker)
docker run -d \
  --name postgres-dev \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=intelligent_assistant \
  -p 5432:5432 \
  --restart always \
  postgres:15

  ---启动服务
  uvicorn app.main:app --reload --port 8000

  ---访问系统
  打开浏览器访问 http://localhost:8000

  📖 使用指南
注册与登录
打开 http://localhost:8000

输入用户名和密码，点击"注册"

注册成功后，切换到登录页面登录

上传文档
登录后，在左侧点击"点击上传文档"

选择 TXT、PDF 或 MD 文件

系统自动切分并向量化存储

智能问答
在底部输入框输入问题

系统检索相关文档片段

基于检索结果生成回答

点击"参考来源"查看引用的文档片段

📡 API 文档
启动服务后，访问 http://localhost:8000/docs 查看 Swagger API 文档。

接口	方法	说明
/api/v1/auth/register	POST	用户注册
/api/v1/auth/login	POST	用户登录
/api/v1/documents/upload	POST	上传文档（需认证）
/api/v1/documents/	GET	获取文档列表（需认证）
/api/v1/chat/ask	POST	RAG 问答（需认证）
/api/v1/system/status	GET	系统状态（需认证）

项目结构
intelligent_assistant/
├── app/
│   ├── api/                    # API 路由
│   │   ├── auth.py            # 认证接口
│   │   ├── chat.py            # 问答接口
│   │   ├── documents.py       # 文档接口
│   │   └── system.py          # 系统接口
│   ├── core/                   # 核心模块
│   │   ├── database.py        # 数据库连接
│   │   ├── loader.py          # 数据加载器
│   │   └── retriever.py       # 混合检索器
│   ├── models/                 # 数据模型
│   │   ├── user.py            # 用户模型
│   │   └── document.py        # 文档模型
│   ├── schemas/                # Pydantic 模型
│   │   ├── user.py            # 用户 Schemas
│   │   └── document.py        # 文档 Schemas
│   ├── services/               # 业务逻辑
│   │   ├── auth_service.py    # 认证服务
│   │   ├── document_service.py # 文档服务
│   │   └── vector_service.py  # 向量服务
│   ├── config.py              # 配置管理
│   ├── dependencies.py        # 依赖注入
│   └── main.py                # 应用入口
├── templates/
│   └── index.html             # 前端页面
├── chroma_db/                  # 向量数据库
├── uploads/                    # 上传文件存储
├── .env                       # 环境变量
├── .gitignore                 # Git 忽略配置
├── requirements.txt           # Python 依赖
├── cleanup.py                 # 数据清理工具
└── README.md                  # 项目文档

🧹 数据清理
python cleanup.py
菜单选项：

1 - 清空上传文件

2 - 清空向量数据库

3 - 清空数据库记录

4 - 清空所有数据

0 - 退出

🐳 Docker 部署
构建镜像
docker build -t intelligent-assistant .

启动服务
docker-compose up -d
⚙️ 配置说明
环境变量	说明	默认值
DATABASE_URL	PostgreSQL 连接字符串	postgresql+asyncpg://...
SECRET_KEY	JWT 密钥	随机字符串
ALGORITHM	JWT 算法	HS256
ACCESS_TOKEN_EXPIRE_MINUTES	Token 过期时间	30
ZHIPU_API_KEY	智谱AI API Key	必填
CHROMA_PERSIST_DIR	向量数据库路径	./chroma_db

🔧 常见问题
Q: 上传文档后提示"文档处理失败"？
A: 检查文件编码是否为 UTF-8，或文件内容是否为空。

Q: 问答时提示"未找到相关信息"？
A: 确保已上传文档，且文档内容与问题相关。

Q: 重启服务后数据丢失？
A: 检查 chroma_db 目录是否存在，并确保路径配置正确。

📄 License
MIT License

🙏 致谢
FastAPI

LangChain

ChromaDB

智谱AI

如果这个项目对你有帮助，欢迎 Star ⭐！

本人邮箱：1054422081@qq.com