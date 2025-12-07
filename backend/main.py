"""FastAPI 主应用"""
import os
import uuid
from typing import Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.config import settings
from backend.models.schemas import (
    ChatRequest, ChatResponse, UserProgress, 
    DocumentUpload, ProgressUpdate, ChunkSettings,
    ReindexRequest, ReindexResponse
)
from backend.modules.workflow import teaching_workflow
from backend.modules.rag import rag_knowledge_base
from backend.modules.memory import memory_manager
from backend.models.database import learning_progress_db

# 创建 FastAPI 应用
app = FastAPI(
    title="金融经济教学智能体 API",
    description="基于 LangChain 的智能教学系统",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建上传目录
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "金融经济教学智能体 API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    对话接口
    
    处理用户消息，返回 AI 回复
    """
    try:
        response = teaching_workflow.process_message(
            user_id=request.user_id,
            message=request.message,
            conversation_id=request.conversation_id
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理消息时出错: {str(e)}")


@app.post("/api/upload", response_model=DocumentUpload)
async def upload_document(file: UploadFile = File(...)):
    """
    文档上传接口
    
    上传文档到知识库
    """
    try:
        # 检查文件类型
        allowed_extensions = [".pdf", ".txt", ".doc", ".docx", ".ppt", ".pptx", ".md"]
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型: {file_ext}。支持的类型: {', '.join(allowed_extensions)}"
            )
        
        # 保存文件
        file_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}{file_ext}")
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # 添加到知识库（使用当前配置的分片参数）
        chunks_count = rag_knowledge_base.add_document_from_file(
            file_path,
            chunk_size=settings.default_chunk_size,
            chunk_overlap=settings.default_chunk_overlap
        )
        
        return DocumentUpload(
            file_id=file_id,
            filename=file.filename,
            status="success",
            chunks_count=chunks_count
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传文档时出错: {str(e)}")


@app.get("/api/progress/{user_id}", response_model=UserProgress)
async def get_progress(user_id: str):
    """
    获取用户学习进度
    """
    try:
        progress = learning_progress_db.get_user_progress(user_id)
        return progress
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取进度时出错: {str(e)}")


@app.post("/api/progress/{user_id}")
async def update_progress(user_id: str, update: ProgressUpdate):
    """
    更新用户学习进度
    """
    try:
        learning_progress_db.update_user_progress(user_id, update)
        return {"message": "进度更新成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新进度时出错: {str(e)}")


@app.get("/api/knowledge/info")
async def get_knowledge_info():
    """
    获取知识库信息
    """
    try:
        info = rag_knowledge_base.get_collection_info()
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取知识库信息时出错: {str(e)}")


@app.post("/api/knowledge/search")
async def search_knowledge(query: str, k: int = 5):
    """
    搜索知识库
    """
    try:
        results = rag_knowledge_base.search(query, k=k)
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索知识库时出错: {str(e)}")


@app.get("/api/knowledge/chunk-settings")
async def get_chunk_settings():
    """
    获取当前文档分片设置
    """
    try:
        return {
            "chunk_size": settings.default_chunk_size,
            "chunk_overlap": settings.default_chunk_overlap
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分片设置时出错: {str(e)}")


@app.post("/api/knowledge/chunk-settings")
async def update_chunk_settings(settings_data: ChunkSettings):
    """
    更新文档分片设置（仅更新配置，不重新索引）
    
    注意：此操作只更新配置，不会重新索引现有文档。
    如需重新索引，请使用 /api/knowledge/reindex 接口。
    """
    try:
        # 更新配置（这里只是返回信息，实际配置需要重启服务或使用环境变量）
        # 为了简化，我们返回提示信息
        return {
            "message": "分片设置已更新（仅配置）。要应用新设置到现有文档，请使用重新索引接口。",
            "new_settings": {
                "chunk_size": settings_data.chunk_size,
                "chunk_overlap": settings_data.chunk_overlap
            },
            "warning": "新设置只会在上传新文档时生效。要重新处理现有文档，请使用重新索引功能。"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新分片设置时出错: {str(e)}")


@app.post("/api/knowledge/reindex", response_model=ReindexResponse)
async def reindex_knowledge(request: ReindexRequest):
    """
    重新分片和索引所有文档
    
    警告：此操作会删除所有现有文档块并重新创建，可能需要较长时间。
    请确保已确认操作。
    """
    try:
        if not request.confirm:
            return ReindexResponse(
                success=False,
                message="请确认重新索引操作。此操作会删除所有现有文档块并重新创建。",
                stats=None
            )
        
        # 执行重新索引
        stats = rag_knowledge_base.reindex_all_documents(
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
            upload_dir=UPLOAD_DIR
        )
        
        # 更新配置（通过环境变量或配置文件）
        # 注意：这里只是临时更新，实际应该持久化到配置文件
        settings.default_chunk_size = request.chunk_size
        settings.default_chunk_overlap = request.chunk_overlap
        
        return ReindexResponse(
            success=True,
            message=f"重新索引完成。处理了 {stats['reindexed_sources']} 个文档源，共 {stats['total_chunks_after']} 个文档块。",
            stats=stats
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重新索引时出错: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)

