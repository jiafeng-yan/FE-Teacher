"""Pydantic 数据模型"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ChatMessage(BaseModel):
    """聊天消息模型"""
    role: str = Field(..., description="消息角色: user, assistant, system")
    content: str = Field(..., description="消息内容")
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    """聊天请求模型"""
    user_id: str = Field(..., description="用户唯一标识")
    message: str = Field(..., description="用户消息")
    conversation_id: Optional[str] = Field(None, description="对话ID")


class ChatResponse(BaseModel):
    """聊天响应模型"""
    response: str = Field(..., description="AI 回复")
    intent: str = Field(..., description="识别的用户意图")
    sources: Optional[List[str]] = Field(None, description="知识来源")
    conversation_id: str = Field(..., description="对话ID")


class UserProgress(BaseModel):
    """用户学习进度模型"""
    user_id: str
    current_topic: Optional[str] = Field(None, description="当前学习章节")
    mastery_level: Dict[str, float] = Field(default_factory=dict, description="各知识点掌握程度 0-100")
    weak_points: List[str] = Field(default_factory=list, description="错题记录")
    mastered_topics: List[str] = Field(default_factory=list, description="已掌握知识点列表")
    last_updated: Optional[datetime] = None


class ProgressUpdate(BaseModel):
    """学习进度更新模型"""
    topic: str = Field(..., description="知识点")
    score: float = Field(..., description="得分 0-100")
    is_correct: bool = Field(..., description="是否正确")
    question: Optional[str] = Field(None, description="问题内容")
    answer: Optional[str] = Field(None, description="用户答案")


class DocumentUpload(BaseModel):
    """文档上传响应模型"""
    file_id: str = Field(..., description="文件ID")
    filename: str = Field(..., description="文件名")
    status: str = Field(..., description="处理状态")
    chunks_count: int = Field(..., description="文档分块数量")


class IntentResponse(BaseModel):
    """意图识别响应模型"""
    intent: str = Field(..., description="识别的意图: learn, review, chat, answer")
    confidence: float = Field(..., description="置信度 0-1")
    topic: Optional[str] = Field(None, description="相关主题")


class ChunkSettings(BaseModel):
    """文档分片设置模型"""
    chunk_size: int = Field(..., ge=100, le=5000, description="文档分块大小 (100-5000)")
    chunk_overlap: int = Field(..., ge=0, le=1000, description="分块重叠大小 (0-1000)")


class ReindexRequest(BaseModel):
    """重新索引请求模型"""
    chunk_size: int = Field(..., ge=100, le=5000, description="新的文档分块大小")
    chunk_overlap: int = Field(..., ge=0, le=1000, description="新的分块重叠大小")
    confirm: bool = Field(False, description="确认重新索引")


class ReindexResponse(BaseModel):
    """重新索引响应模型"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    stats: Optional[Dict[str, Any]] = Field(None, description="统计信息")

