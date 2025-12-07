"""文档加载和处理"""
import os
from typing import List
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredPowerPointLoader
)


class DocumentLoader:
    """文档加载器"""
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        """
        初始化文档加载器
        
        Args:
            chunk_size: 文档分块大小（如果为 None，使用配置中的默认值）
            chunk_overlap: 分块重叠大小（如果为 None，使用配置中的默认值）
        """
        from backend.config import settings
        
        self.chunk_size = chunk_size or settings.default_chunk_size
        self.chunk_overlap = chunk_overlap or settings.default_chunk_overlap
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", "。", "！", "？", "；", " ", ""]
        )
    
    def update_splitter(self, chunk_size: int, chunk_overlap: int):
        """
        更新分片器配置
        
        Args:
            chunk_size: 新的文档分块大小
            chunk_overlap: 新的分块重叠大小
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", "。", "！", "？", "；", " ", ""]
        )
    
    def load_document(self, file_path: str) -> List[str]:
        """
        加载文档并分块
        
        Args:
            file_path: 文件路径
            
        Returns:
            文档块列表
        """
        file_ext = Path(file_path).suffix.lower()
        
        # 根据文件类型选择加载器
        if file_ext == ".pdf":
            loader = PyPDFLoader(file_path)
        elif file_ext in [".txt", ".md"]:
            loader = TextLoader(file_path, encoding="utf-8")
        elif file_ext in [".doc", ".docx"]:
            loader = UnstructuredWordDocumentLoader(file_path)
        elif file_ext in [".ppt", ".pptx"]:
            loader = UnstructuredPowerPointLoader(file_path)
        else:
            raise ValueError(f"不支持的文件类型: {file_ext}")
        
        # 加载文档
        documents = loader.load()
        
        # 合并所有页面内容
        full_text = "\n\n".join([doc.page_content for doc in documents])
        
        # 分块
        chunks = self.text_splitter.split_text(full_text)
        
        return chunks
    
    def load_text(self, text: str) -> List[str]:
        """
        直接加载文本并分块
        
        Args:
            text: 文本内容
            
        Returns:
            文档块列表
        """
        return self.text_splitter.split_text(text)


# 全局文档加载器实例
document_loader = DocumentLoader()

