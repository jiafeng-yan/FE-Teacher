"""嵌入模型管理"""
from typing import List
from langchain_openai import OpenAIEmbeddings
# from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from backend.config import settings


class EmbeddingManager:
    """嵌入模型管理器"""
    
    def __init__(self):
        """初始化嵌入模型"""
        if settings.use_local_embedding:
            # encode_kwargs = {'normalize_embeddings': True}
            # 使用本地模型
            print('local_embedding_model', settings.local_embedding_model)
            self.embeddings = HuggingFaceEmbeddings(
                model_name=settings.local_embedding_model,
                model_kwargs={'device': settings.infer_device, 'trust_remote_code': True},
                # encode_kwargs=encode_kwargs
            )
        else:
            # 使用 OpenAI 模型
            if not settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY 未设置，无法使用 OpenAI 嵌入模型")
            self.embeddings = OpenAIEmbeddings(
                model=settings.openai_embedding_model,
                openai_api_key=settings.openai_api_key
            )
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """对文档列表进行嵌入"""
        return self.embeddings.embed_documents(texts)
    
    def embed_query(self, text: str) -> List[float]:
        """对查询文本进行嵌入"""
        return self.embeddings.embed_query(text)
    
    def get_embedding_dimension(self) -> int:
        """
        获取当前嵌入模型的维度
        
        Returns:
            嵌入维度
        """
        # 通过嵌入一个测试文本来获取维度
        test_text = "test"
        embedding = self.embed_query(test_text)
        return len(embedding)


# 全局嵌入模型实例
embedding_manager = EmbeddingManager()

