"""配置管理模块"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """应用配置"""
    
    # OpenAI 配置
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    openai_embedding_model: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    openai_base_url: Optional[str] = os.getenv("OPENAI_BASE_URL", None)  # 支持自定义 base_url
    
    # 意图识别模型配置（可独立配置）
    intent_model_api_key: Optional[str] = os.getenv("INTENT_MODEL_API_KEY", None)
    intent_model_name: str = os.getenv("INTENT_MODEL_NAME", "gpt-3.5-turbo")
    intent_model_base_url: Optional[str] = os.getenv("INTENT_MODEL_BASE_URL", None)
    
    # 本地嵌入模型配置
    infer_device: str = os.getenv("INFER_DEVICE", 'cuda')
    local_embedding_model: str = os.getenv("LOCAL_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    use_local_embedding: bool = os.getenv("USE_LOCAL_EMBEDDING", "true").lower() == "true"
    
    # Tavily 搜索配置
    tavily_api_key: Optional[str] = os.getenv("TAVILY_API_KEY", None)
    
    # ChromaDB 配置
    chroma_db_path: str = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    chroma_collection_name: str = os.getenv("CHROMA_COLLECTION_NAME", "financial_economics_knowledge")
    
    # 学习进度数据库配置
    learning_progress_db_path: str = os.getenv("LEARNING_PROGRESS_DB_PATH", "./learning_progress_db")
    
    # 文档分片配置（默认值，可通过 API 修改）
    default_chunk_size: int = int(os.getenv("DEFAULT_CHUNK_SIZE", "1000"))
    default_chunk_overlap: int = int(os.getenv("DEFAULT_CHUNK_OVERLAP", "200"))
    
    # 服务器配置
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    
    # 前端配置
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

