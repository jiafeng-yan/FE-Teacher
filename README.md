# 金融经济教学智能体

基于 LangChain 构建的智能教学系统，采用 Agentic Workflow 架构，实现个性化教学和动态学习进度跟踪。

## 核心特性

- 🧠 **智能意图识别**：自动识别用户意图（学习、复习、闲聊）
- 📚 **RAG 知识库**：支持上传 PPT、TXT、Word 等文档，构建专业金融经济知识库
- 💾 **持久化记忆**：使用 ChromaDB 存储用户学习进度、错题本、知识点掌握情况
- 🔧 **工具集成**：联网搜索、绘图等扩展功能
- 🎯 **个性化教学**：根据学生进度动态调整教学内容，实现因材施教
- 💬 **苏格拉底式教学**：通过引导性提问帮助学生思考
- 🔄 **智能模型切换**：支持切换嵌入模型，自动处理维度不匹配问题

## 技术架构

### 后端架构

```
Agentic Workflow
├── Planner/Router (意图识别)
├── RAG (知识检索)
├── Memory (短期 + 长期记忆)
└── Tools (联网搜索、绘图等)
```

### 核心模块

1. **Planner/Router**：使用小模型识别用户意图
2. **RAG 知识库**：本地文本嵌入模型 + ChromaDB 向量存储
3. **Memory**：
   - 短期记忆：对话上下文（LLM 内置）
   - 长期记忆：用户学习进度数据库（ChromaDB）
4. **Tools**：Tavily 搜索、绘图工具等

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd dify-to-langchain

# 创建虚拟环境
python -m venv venv
# Linux
source venv/bin/activate
# Windows
venv\Scripts\activate
python -m pip install --upgrade pip

# 安装依赖
pip install torch==2.8.0 --index-url https://download.pytorch.org/whl/cu129
pip install -r requirements.txt

# 前端配置
cd frontend
npm install
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的 API 密钥和配置
```

**必需配置**：

- `OPENAI_API_KEY`: OpenAI API 密钥（或兼容的 API 密钥）

**可选配置**：

- `OPENAI_BASE_URL`: 自定义 API 基础 URL（用于兼容其他 OpenAI API 兼容服务）
- `OPENAI_MODEL`: 主对话模型名称（默认: gpt-4-turbo-preview）
- `INTENT_MODEL_API_KEY`: 意图识别模型 API 密钥（可选，默认使用 OPENAI_API_KEY）
- `INTENT_MODEL_NAME`: 意图识别模型名称（默认: gpt-3.5-turbo）
- `INTENT_MODEL_BASE_URL`: 意图识别模型 API 基础 URL（可选）
- `TAVILY_API_KEY`: Tavily 搜索 API 密钥（可选，用于联网搜索）
- `DEFAULT_CHUNK_SIZE`: 默认文档分块大小（默认: 1500）
- `DEFAULT_CHUNK_OVERLAP`: 默认分块重叠大小（默认: 300）

### 3. 启动后端服务

```bash
venv\Scripts\activate
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

```

### 4. 启动前端服务

```bash
cd frontend
npm run dev

```

### 5. 访问应用

- 前端界面：http://localhost:3000
- API 文档：http://localhost:8000/docs

## 项目结构

```
dify-to-langchain/
├── backend/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 主应用
│   ├── config.py               # 配置管理
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py          # Pydantic 数据模型
│   │   └── database.py         # 数据库模型
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── planner.py          # 意图识别模块
│   │   ├── rag.py              # RAG 知识库模块
│   │   ├── memory.py           # 记忆管理模块
│   │   ├── tools.py            # 工具模块
│   │   └── workflow.py         # 核心工作流
│   └── utils/
│       ├── __init__.py
│       ├── document_loader.py  # 文档加载器
│       └── embeddings.py      # 嵌入模型管理
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── ChatInterface.jsx
│   │   │   └── DocumentUpload.jsx
│   │   └── services/
│   │       └── api.js
│   ├── package.json
│   └── tailwind.config.js
├── requirements.txt
├── .env.example
└── README.md
```

## 使用说明

### 上传知识库文档

1. 在前端界面点击"上传文档"
2. 选择 PPT、TXT、Word 等格式文件
3. 系统自动进行文档解析和向量化存储

### 开始学习

1. 在对话界面输入问题或学习需求
2. 系统自动识别意图并调用相应模块
3. 根据你的学习进度提供个性化教学内容

### 查看学习进度

系统会自动记录：

- 当前学习章节
- 知识点掌握程度（0-100）
- 错题记录
- 已掌握知识点列表

## API 文档

启动服务后访问 http://localhost:8000/docs 查看完整的 API 文档。

主要接口：

- `POST /api/chat` - 对话接口
- `POST /api/upload` - 文档上传接口
- `GET /api/progress/{user_id}` - 获取学习进度
- `POST /api/progress/{user_id}` - 更新学习进度

## 文档导航

- [README.md](README.md) - 项目概述和快速开始
- [QUICKSTART.md](QUICKSTART.md) - 快速启动指南
- [ARCHITECTURE.md](ARCHITECTURE.md) - 系统架构文档
- [ARCHITECTURE_DIAGRAMS.md](ARCHITECTURE_DIAGRAMS.md) - 系统架构图示（包含详细流程图）
- [CONFIGURATION.md](CONFIGURATION.md) - 配置说明文档
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - 项目总结

## 配置说明

详细的配置说明请参考 [CONFIGURATION.md](CONFIGURATION.md)。

详细的架构图示请参考 [ARCHITECTURE_DIAGRAMS.md](ARCHITECTURE_DIAGRAMS.md)。

### 主要配置项

- **OPENAI_API_KEY**: OpenAI API 密钥（必需）
- **OPENAI_BASE_URL**: 自定义 API 基础 URL（可选，用于兼容其他服务）
- **INTENT*MODEL*\***: 意图识别模型独立配置（可选）
- **DEFAULT_CHUNK_SIZE**: 文档分块大小（默认: 1000）
- **DEFAULT_CHUNK_OVERLAP**: 分块重叠大小（默认: 200）

### 文档分片设置

文档分片参数可以通过前端界面动态调整：

1. 访问"设置"标签页
2. 修改分块大小和重叠大小
3. 保存设置（仅更新配置）
4. 重新索引所有文档（应用新设置到现有文档）

### 嵌入模型切换

系统支持切换不同的嵌入模型（本地模型或 OpenAI 模型）：

- **自动维度检测**：切换模型后，系统会自动检测嵌入维度是否匹配
- **自动修复**：如果维度不匹配，系统会在重新索引时自动删除旧集合并创建新集合
- **无缝切换**：无需手动清理数据，系统会自动处理所有技术细节

**支持的嵌入模型**：

- 本地模型：`sentence-transformers/all-MiniLM-L6-v2` (384 维)
- 本地模型：`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (384 维)
- OpenAI 模型：`text-embedding-3-small` (1536 维)
- OpenAI 模型：`text-embedding-3-large` (3072 维)

**切换步骤**：

1. 修改 `.env` 文件中的 `LOCAL_EMBEDDING_MODEL` 或 `USE_LOCAL_EMBEDDING`
2. 重启后端服务
3. 在前端界面执行"重新索引所有文档"
4. 系统会自动检测并修复维度不匹配问题

## 开发指南

### 添加新的工具

在 `backend/modules/tools.py` 中添加新的工具函数，并在 `workflow.py` 中集成。

### 自定义提示词

在 `backend/modules/workflow.py` 中修改教学提示词模板。

### 调整分段策略

可以通过以下方式调整文档分段策略：

1. 修改环境变量 `DEFAULT_CHUNK_SIZE` 和 `DEFAULT_CHUNK_OVERLAP`
2. 通过前端界面动态调整（推荐）
3. 在 `backend/utils/document_loader.py` 中修改默认值

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
