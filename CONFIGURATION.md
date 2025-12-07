# 配置说明文档

本文档详细说明所有可配置的环境变量和系统设置。

## 环境变量配置

### OpenAI 配置

#### OPENAI_API_KEY

- **类型**: 字符串
- **必需**: 是
- **说明**: OpenAI API 密钥，用于调用大语言模型
- **示例**: `sk-...`

#### OPENAI_MODEL

- **类型**: 字符串
- **默认值**: `gpt-4-turbo-preview`
- **说明**: 主对话模型名称
- **示例**: `gpt-4-turbo-preview`, `gpt-3.5-turbo`

#### OPENAI_BASE_URL

- **类型**: 字符串
- **默认值**: `None` (使用 OpenAI 官方 API)
- **说明**: 自定义 API 基础 URL，用于兼容其他 OpenAI API 兼容服务（如本地部署的模型服务）
- **示例**: `http://localhost:1234/v1`, `https://api.example.com/v1`

#### OPENAI_EMBEDDING_MODEL

- **类型**: 字符串
- **默认值**: `text-embedding-3-small`
- **说明**: 文本嵌入模型名称（仅在 `USE_LOCAL_EMBEDDING=false` 时使用）
- **示例**: `text-embedding-3-small`, `text-embedding-3-large`

### 意图识别模型配置（独立配置）

#### INTENT_MODEL_API_KEY

- **类型**: 字符串
- **默认值**: `None` (使用 OPENAI_API_KEY)
- **说明**: 意图识别模型的独立 API 密钥，允许使用不同的 API 服务
- **示例**: `sk-...`

#### INTENT_MODEL_NAME

- **类型**: 字符串
- **默认值**: `gpt-3.5-turbo`
- **说明**: 意图识别模型名称
- **示例**: `gpt-3.5-turbo`, `gpt-4`, `qwen-turbo`

#### INTENT_MODEL_BASE_URL

- **类型**: 字符串
- **默认值**: `None` (使用 OPENAI_BASE_URL 或 OpenAI 官方 API)
- **说明**: 意图识别模型的 API 基础 URL
- **示例**: `http://localhost:8000/v1`

**使用场景**: 当你想要使用不同的模型服务进行意图识别时，可以独立配置这些参数。例如：

- 主对话使用 OpenAI GPT-4
- 意图识别使用本地部署的 Qwen 模型

### 本地嵌入模型配置

#### USE_LOCAL_EMBEDDING

- **类型**: 布尔值
- **默认值**: `true`
- **说明**: 是否使用本地嵌入模型（推荐，免费且无需 API 调用）
- **可选值**: `true`, `false`

#### LOCAL_EMBEDDING_MODEL

- **类型**: 字符串
- **默认值**: `sentence-transformers/all-MiniLM-L6-v2`
- **说明**: 本地嵌入模型名称（仅在 `USE_LOCAL_EMBEDDING=true` 时使用）
- **示例**: `sentence-transformers/all-MiniLM-L6-v2`, `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`

### 文档分片配置

#### DEFAULT_CHUNK_SIZE

- **类型**: 整数
- **默认值**: `1000`
- **范围**: 100-5000
- **说明**: 默认文档分块大小（字符数）
- **影响**:
  - 较小的值：更精确的匹配，但可能丢失上下文
  - 较大的值：包含更多上下文，但检索可能不够精确

#### DEFAULT_CHUNK_OVERLAP

- **类型**: 整数
- **默认值**: `200`
- **范围**: 0-1000
- **说明**: 默认分块重叠大小（字符数）
- **影响**: 重叠有助于保持上下文连续性，但会增加存储空间

**注意**: 这些默认值可以通过前端界面动态修改，修改后需要重新索引现有文档才能生效。

### 嵌入模型切换

#### 切换嵌入模型

当你需要切换嵌入模型时（例如从 384 维模型切换到 768 维模型），系统会自动处理维度不匹配问题：

1. **修改配置**：在 `.env` 文件中修改 `LOCAL_EMBEDDING_MODEL` 或 `USE_LOCAL_EMBEDDING`
2. **重启服务**：重启后端服务以加载新模型
3. **重新索引**：在前端界面执行"重新索引所有文档"
4. **自动修复**：系统会自动检测维度不匹配，删除旧集合并创建新集合

**常见嵌入模型维度**：

- `sentence-transformers/all-MiniLM-L6-v2`: 384 维
- `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`: 384 维
- `text-embedding-3-small`: 1536 维
- `text-embedding-3-large`: 3072 维

**重要提示**：

- 切换模型后必须重新索引所有文档
- 系统会自动处理维度不匹配，无需手动清理数据
- 重新索引会删除所有现有文档块并重新创建，可能需要较长时间

### 数据库配置

#### CHROMA_DB_PATH

- **类型**: 字符串
- **默认值**: `./chroma_db`
- **说明**: ChromaDB 知识库存储路径

#### CHROMA_COLLECTION_NAME

- **类型**: 字符串
- **默认值**: `financial_economics_knowledge`
- **说明**: ChromaDB 集合名称

#### LEARNING_PROGRESS_DB_PATH

- **类型**: 字符串
- **默认值**: `./learning_progress_db`
- **说明**: 用户学习进度数据库存储路径

### 工具配置

#### TAVILY_API_KEY

- **类型**: 字符串
- **默认值**: `None`
- **说明**: Tavily 搜索 API 密钥（用于联网搜索功能）
- **获取**: https://tavily.com/

### 服务器配置

#### API_HOST

- **类型**: 字符串
- **默认值**: `0.0.0.0`
- **说明**: API 服务器监听地址

#### API_PORT

- **类型**: 整数
- **默认值**: `8000`
- **说明**: API 服务器端口

#### FRONTEND_URL

- **类型**: 字符串
- **默认值**: `http://localhost:3000`
- **说明**: 前端应用 URL（用于 CORS 配置）

## 配置示例

### 示例 1: 使用 OpenAI 官方 API

```env
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4-turbo-preview
```

### 示例 2: 使用本地部署的模型服务

```env
OPENAI_API_KEY=sk-any-key
OPENAI_MODEL=qwen-plus
OPENAI_BASE_URL=http://localhost:1234/v1
USE_LOCAL_EMBEDDING=true
```

### 示例 3: 意图识别使用独立模型

```env
# 主对话模型
OPENAI_API_KEY=sk-openai-key
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_BASE_URL=https://api.openai.com/v1

# 意图识别模型（使用本地服务）
INTENT_MODEL_API_KEY=sk-any-key
INTENT_MODEL_NAME=qwen-turbo
INTENT_MODEL_BASE_URL=http://localhost:8000/v1

USE_LOCAL_EMBEDDING=true
```

### 示例 4: 自定义文档分片参数

```env
DEFAULT_CHUNK_SIZE=1500
DEFAULT_CHUNK_OVERLAP=300
```

## 前端界面配置

文档分片参数也可以通过前端界面进行配置：

1. 访问前端应用
2. 点击"设置"标签页
3. 修改"文档分块大小"和"分块重叠大小"
4. 点击"保存设置"（仅更新配置）
5. 点击"重新索引所有文档"（应用新设置到现有文档）

**重要提示**:

- 修改分片参数后，新上传的文档会自动使用新参数
- 要重新处理现有文档，必须使用"重新索引"功能
- 重新索引会删除所有现有文档块并重新创建，可能需要较长时间

## 配置优先级

1. **环境变量** > 代码默认值
2. **意图识别模型配置** > OpenAI 通用配置
3. **前端设置** > 环境变量默认值（仅对新上传文档生效）

## 常见问题

### Q: 如何切换到本地部署的模型？

A: 设置 `OPENAI_BASE_URL` 为你的本地服务地址，例如：

```env
OPENAI_BASE_URL=http://localhost:1234/v1
```

### Q: 意图识别可以使用不同的模型服务吗？

A: 可以，通过设置 `INTENT_MODEL_API_KEY`、`INTENT_MODEL_NAME` 和 `INTENT_MODEL_BASE_URL` 独立配置。

### Q: 修改分片参数后需要重启服务吗？

A: 不需要重启服务。新参数会立即生效于新上传的文档。要重新处理现有文档，使用前端的"重新索引"功能。

### Q: 如何备份知识库数据？

A: 备份 `CHROMA_DB_PATH` 目录（默认 `./chroma_db`）即可。

### Q: 切换嵌入模型后出现维度不匹配错误怎么办？

A: 系统已经实现了自动维度检测和修复功能。当你切换模型后执行重新索引时，系统会：

1. 自动检测当前模型的嵌入维度
2. 如果维度不匹配，自动删除旧集合并创建新集合
3. 使用保存的文档元数据重新索引所有文档

如果仍然遇到问题，请检查：

- 是否正确重启了后端服务
- 新模型是否正确加载
- 查看后端日志中的维度检测信息
