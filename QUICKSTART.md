# 快速启动指南

## 前置要求

- Python 3.8+
- Node.js 16+
- OpenAI API Key（可选，也可部署本地模型）
- Tavily API Key（可选，用于联网搜索）

## 安装步骤

### 1. 后端设置

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `env.example` 为 `.env` 并填入你的 API 密钥：

```bash
# Windows
copy env.example .env

# Linux/Mac
cp env.example .env
```

编辑 `.env` 文件，至少需要设置：

- `OPENAI_API_KEY`: 你的 OpenAI API 密钥

可选配置：

- `TAVILY_API_KEY`: Tavily 搜索 API 密钥（用于联网搜索功能）
- `USE_LOCAL_EMBEDDING`: 设置为 `true` 使用本地嵌入模型（无需 OpenAI 嵌入 API）

### 3. 启动后端

```bash
# Windows
start_backend.bat

# Linux/Mac
chmod +x start_backend.sh
./start_backend.sh

# 或直接运行
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

后端将在 http://localhost:8000 启动

### 4. 前端设置

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将在 http://localhost:3000 启动

## 使用说明

### 1. 上传知识库文档

1. 在前端界面点击"上传文档"标签
2. 选择 PDF、TXT、Word 或 PowerPoint 文件
3. 点击"上传文档"按钮
4. 等待文档处理完成

### 2. 开始学习

1. 在"对话学习"标签中输入问题，例如：

   - "什么是 GDP？"
   - "给我讲讲货币政策"
   - "解释一下通货膨胀"

2. 系统会自动：
   - 识别你的意图（学习、复习、答题、闲聊）
   - 从知识库检索相关内容
   - 根据你的学习进度提供个性化教学
   - 使用苏格拉底式提问引导你思考

### 3. 回答问题

当系统提问时，你可以直接回答。系统会：

- 自动判卷评分
- 更新你的学习进度
- 如果得分低于 60 分，触发"补习模式"

### 4. 查看学习进度

在"学习进度"标签中可以查看：

- 当前学习主题
- 各知识点掌握程度（0-100%）
- 已掌握知识点列表
- 需要加强的知识点（错题记录）

## 常见问题

### Q: 如何切换使用本地嵌入模型？

A: 在 `.env` 文件中设置 `USE_LOCAL_EMBEDDING=true`。首次使用时会自动下载模型。

**重要提示**：切换嵌入模型后，需要在前端界面执行"重新索引所有文档"操作。系统会自动检测并修复嵌入维度不匹配问题，无需手动清理数据。

### Q: 如何配置自定义的 API 服务？

A: 设置 `OPENAI_BASE_URL` 环境变量，例如：`OPENAI_BASE_URL=http://localhost:1234/v1`

### Q: 意图识别可以使用不同的模型吗？

A: 可以，通过设置 `INTENT_MODEL_API_KEY`、`INTENT_MODEL_NAME` 和 `INTENT_MODEL_BASE_URL` 独立配置意图识别模型。

### Q: 如何修改文档分片参数？

A: 有两种方式：

1. 修改环境变量 `DEFAULT_CHUNK_SIZE` 和 `DEFAULT_CHUNK_OVERLAP`
2. 通过前端"设置"标签页动态调整（推荐）

修改后需要执行"重新索引所有文档"才能应用到现有文档。

### Q: 切换嵌入模型后出现维度错误怎么办？

A: 系统已经实现了自动维度检测和修复功能。当你切换模型后执行重新索引时，系统会：

1. 自动检测当前模型的嵌入维度
2. 如果维度不匹配，自动删除旧集合并创建新集合
3. 使用保存的文档元数据重新索引所有文档

如果仍然遇到问题，请检查后端日志中的维度检测信息。

### Q: 知识库数据存储在哪里？

A: 默认存储在 `./chroma_db` 目录。学习进度存储在 `./learning_progress_db` 目录。

### Q: 如何重置用户学习进度？

A: 删除 `./learning_progress_db` 目录即可。

### Q: 支持哪些文档格式？

A: 支持 PDF (.pdf)、文本文件 (.txt, .md)、Word (.doc, .docx)、PowerPoint (.ppt, .pptx)

### Q: 如何修改教学风格？

A: 编辑 `backend/modules/workflow.py` 中的提示词模板。

## 开发建议

1. **调整分段策略**：编辑 `backend/utils/document_loader.py` 中的 `chunk_size` 和 `chunk_overlap` 参数

2. **添加新工具**：在 `backend/modules/tools.py` 中添加新工具函数

3. **自定义提示词**：修改 `backend/modules/workflow.py` 中各意图的处理函数中的提示词

4. **调整评分标准**：修改 `backend/modules/workflow.py` 中 `_handle_answer_intent` 方法的评分逻辑

## 故障排除

### 后端启动失败

- 检查 Python 版本（需要 3.8+）
- 检查是否安装了所有依赖：`pip install -r requirements.txt`
- 检查 `.env` 文件中的 API 密钥是否正确

### 前端无法连接后端

- 确认后端服务正在运行（http://localhost:8000）
- 检查 `frontend/vite.config.js` 中的代理配置
- 检查浏览器控制台的错误信息

### 文档上传失败

- 检查文件格式是否支持
- 检查文件大小（建议小于 50MB）
- 查看后端日志中的错误信息

### 重新索引时出现维度不匹配错误

- 系统会自动处理此问题，无需手动干预
- 如果自动修复失败，检查后端日志中的错误信息
- 确认新嵌入模型已正确加载
- 可以尝试手动删除 `./chroma_db` 目录后重新上传文档

### 意图识别不准确

- 可以调整 `backend/modules/planner.py` 中的提示词
- 可以尝试使用更精确的模型（如 gpt-4）
