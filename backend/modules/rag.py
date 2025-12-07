"""RAG 知识库模块"""
import os
import json
from typing import List, Optional, Dict
from pathlib import Path
import chromadb
from chromadb.config import Settings as ChromaSettings
# from langchain_community.vectorstores import Chroma
from langchain_chroma import Chroma
from backend.config import settings
from backend.utils.embeddings import embedding_manager
from backend.utils.document_loader import DocumentLoader


class RAGKnowledgeBase:
    """RAG 知识库"""
    
    def __init__(self):
        """初始化知识库"""
        # 创建 ChromaDB 客户端
        self.client = chromadb.PersistentClient(
            path=settings.chroma_db_path,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(
            name=settings.chroma_collection_name,
            metadata={"description": "金融经济知识库"}
        )
        
        # 创建 LangChain Chroma 向量存储
        self.vectorstore = Chroma(
            client=self.client,
            collection_name=settings.chroma_collection_name,
            embedding_function=embedding_manager.embeddings
        )
    
    def add_documents(self, texts: List[str], metadatas: Optional[List[dict]] = None):
        """
        添加文档到知识库
        
        Args:
            texts: 文档文本列表
            metadatas: 元数据列表（可选）
        """
        if metadatas is None:
            metadatas = [{}] * len(texts)
        
        self.vectorstore.add_texts(texts=texts, metadatas=metadatas)
    
    def add_document_from_file(self, file_path: str, chunk_size: Optional[int] = None, chunk_overlap: Optional[int] = None):
        """
        从文件添加文档到知识库
        
        Args:
            file_path: 文件路径
            chunk_size: 文档分块大小（可选，使用默认值）
            chunk_overlap: 分块重叠大小（可选，使用默认值）
            
        Returns:
            添加的文档块数量
        """
        # 创建文档加载器（使用指定的分片参数）
        loader = DocumentLoader(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        
        # 加载并分块文档
        chunks = loader.load_document(file_path)
        
        # 准备元数据
        filename = os.path.basename(file_path)
        metadatas = [{"source": filename, "chunk_index": i, "file_path": file_path} for i in range(len(chunks))]
        
        # 添加到向量存储
        self.add_documents(chunks, metadatas)
        
        return len(chunks)
    
    def search(self, query: str, k: int = 5, user_progress: Optional[dict] = None) -> List[str]:
        """
        在知识库中搜索相关内容
        
        Args:
            query: 查询文本
            k: 返回结果数量
            user_progress: 用户学习进度（用于个性化检索）
            
        Returns:
            相关文档片段列表
        """
        # 如果有用户进度，可以调整检索策略
        # 例如：如果用户是初学者，优先检索基础内容
        
        # 执行相似度搜索
        results = self.vectorstore.similarity_search(query, k=k)
        
        # 提取文本内容
        texts = [doc.page_content for doc in results]
        
        return texts
    
    def search_with_scores(self, query: str, k: int = 5) -> List[tuple]:
        """
        搜索并返回相似度分数
        
        Args:
            query: 查询文本
            k: 返回结果数量
            
        Returns:
            (文档内容, 相似度分数) 元组列表
        """
        results = self.vectorstore.similarity_search_with_score(query, k=k)
        return [(doc.page_content, score) for doc, score in results]
    
    def get_collection_info(self) -> dict:
        """获取知识库信息"""
        count = self.collection.count()
        return {
            "collection_name": settings.chroma_collection_name,
            "document_count": count
        }
    
    def get_all_documents(self) -> List[Dict]:
        """
        获取知识库中所有文档的元数据
        
        Returns:
            文档元数据列表
        """
        results = self.collection.get(include=["metadatas", "documents"])
        
        documents = []
        for i, metadata in enumerate(results["metadatas"]):
            documents.append({
                "id": results["ids"][i],
                "metadata": metadata,
                "content": results["documents"][i] if results["documents"] else ""
            })
        
        return documents
    
    def get_unique_sources(self) -> List[str]:
        """
        获取知识库中所有唯一的文档来源
        
        Returns:
            文档来源列表
        """
        results = self.collection.get(include=["metadatas"])
        sources = set()
        
        for metadata in results["metadatas"]:
            if "source" in metadata:
                sources.add(metadata["source"])
        
        return list(sources)
    
    def delete_by_source(self, source: str):
        """
        根据来源删除文档
        
        Args:
            source: 文档来源（文件名）
        """
        results = self.collection.get(include=["metadatas"])
        ids_to_delete = []
        
        for i, metadata in enumerate(results["metadatas"]):
            if metadata.get("source") == source:
                ids_to_delete.append(results["ids"][i])
        
        if ids_to_delete:
            self.collection.delete(ids=ids_to_delete)
        
        return len(ids_to_delete)
    
    def _check_and_fix_embedding_dimension(self) -> bool:
        """
        检查当前嵌入模型的维度是否与集合的维度匹配
        如果不匹配，删除旧集合并创建新集合
        
        Returns:
            True 如果维度匹配或已修复，False 如果出错
        """
        try:
            # 获取当前嵌入模型的维度
            current_dim = embedding_manager.get_embedding_dimension()
            print(f"当前嵌入模型维度: {current_dim}")
            
            # 检查集合中是否有数据
            collection_count = self.collection.count()
            
            if collection_count > 0:
                # 如果集合中有数据，尝试添加一个测试文档来检查维度
                # ChromaDB 在添加时会自动检查维度，如果维度不匹配会抛出异常
                test_text = "dimension_test"
                test_embedding = embedding_manager.embed_query(test_text)
                
                try:
                    # 尝试添加测试项
                    self.collection.add(
                        ids=["__dimension_test__"],
                        embeddings=[test_embedding],
                        documents=[test_text],
                        metadatas=[{"test": True}]
                    )
                    # 如果成功，删除测试项
                    self.collection.delete(ids=["__dimension_test__"])
                    print("嵌入维度匹配，无需重建集合")
                    return True
                except Exception as e:
                    error_msg = str(e).lower()
                    # 检查是否是维度不匹配错误
                    if "dimension" in error_msg or "expecting" in error_msg:
                        print(f"检测到嵌入维度不匹配: {error_msg}")
                        print("正在删除旧集合并创建新集合...")
                        
                        # 删除旧集合
                        try:
                            self.client.delete_collection(name=settings.chroma_collection_name)
                        except Exception as delete_error:
                            print(f"删除旧集合时出错: {delete_error}")
                        
                        # 创建新集合
                        self.collection = self.client.get_or_create_collection(
                            name=settings.chroma_collection_name,
                            metadata={"description": "金融经济知识库"}
                        )
                        
                        # 重新创建 LangChain Chroma 向量存储
                        self.vectorstore = Chroma(
                            client=self.client,
                            collection_name=settings.chroma_collection_name,
                            embedding_function=embedding_manager.embeddings
                        )
                        
                        print(f"已创建新集合，维度: {current_dim}")
                        return True
                    else:
                        # 其他错误，记录并返回False
                        print(f"检查维度时发生其他错误: {e}")
                        return False
            else:
                # 集合为空，可以安全地重新创建以确保维度正确
                print(f"集合为空，重新创建集合以确保维度正确（维度: {current_dim}）")
                try:
                    self.client.delete_collection(name=settings.chroma_collection_name)
                except Exception:
                    pass  # 如果集合不存在，忽略错误
                
                # 创建新集合
                self.collection = self.client.get_or_create_collection(
                    name=settings.chroma_collection_name,
                    metadata={"description": "金融经济知识库"}
                )
                
                # 重新创建 LangChain Chroma 向量存储
                self.vectorstore = Chroma(
                    client=self.client,
                    collection_name=settings.chroma_collection_name,
                    embedding_function=embedding_manager.embeddings
                )
                
                return True
                
        except Exception as e:
            print(f"检查嵌入维度时出错: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def reindex_all_documents(self, chunk_size: int, chunk_overlap: int, upload_dir: str = "uploads") -> Dict:
        """
        重新分片和索引所有文档
        
        Args:
            chunk_size: 新的文档分块大小
            chunk_overlap: 新的分块重叠大小
            upload_dir: 上传文件目录
            
        Returns:
            重新索引结果统计
        """
        # 在检查维度之前，先保存所有文档的元数据（以防维度不匹配导致集合被删除）
        try:
            all_docs = self.get_all_documents()
        except Exception as e:
            print(f"获取文档列表时出错: {e}")
            all_docs = []
        
        # 检查并修复嵌入维度不匹配问题
        # 注意：如果维度不匹配，集合会被删除并重建，所以需要重新获取文档列表
        dimension_fixed = self._check_and_fix_embedding_dimension()
        
        # 如果维度被修复（集合被重建），文档列表会为空，使用之前保存的元数据
        if dimension_fixed:
            # 重新获取文档列表（如果集合被重建，这会返回空列表）
            try:
                current_docs = self.get_all_documents()
                # 如果当前文档列表为空但之前有文档，使用之前保存的元数据
                if len(current_docs) == 0 and len(all_docs) > 0:
                    print("集合已重建，使用之前保存的文档元数据")
                    # all_docs 已经包含了之前的元数据，继续使用
                elif len(current_docs) > 0:
                    # 如果集合没有被重建，使用当前的文档列表
                    all_docs = current_docs
            except Exception as e:
                print(f"重新获取文档列表时出错: {e}")
                # 如果出错，继续使用之前保存的 all_docs
        else:
            raise ValueError("无法检查或修复嵌入维度，请检查嵌入模型配置")
        
        # 按来源分组
        sources_map = {}
        for doc in all_docs:
            source = doc["metadata"].get("source")
            file_path = doc["metadata"].get("file_path")
            if source:
                if source not in sources_map:
                    sources_map[source] = {
                        "file_path": file_path,
                        "chunks": []
                    }
                sources_map[source]["chunks"].append(doc)
        
        # 统计信息
        stats = {
            "total_sources": len(sources_map),
            "reindexed_sources": 0,
            "failed_sources": [],
            "total_chunks_before": len(all_docs),
            "total_chunks_after": 0
        }
        
        # 创建新的文档加载器
        loader = DocumentLoader(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        
        # 对每个来源的文档进行重新索引
        for source, info in sources_map.items():
            try:
                # 删除旧的文档块
                deleted_count = self.delete_by_source(source)
                
                # 如果文件路径存在，重新加载和分片
                file_path = info["file_path"]
                if file_path and os.path.exists(file_path):
                    chunks = loader.load_document(file_path)
                    
                    # 准备新的元数据
                    metadatas = [{"source": source, "chunk_index": i, "file_path": file_path} for i in range(len(chunks))]
                    
                    # 添加到向量存储
                    self.add_documents(chunks, metadatas)
                    
                    stats["reindexed_sources"] += 1
                    stats["total_chunks_after"] += len(chunks)
                else:
                    # 如果文件不存在，尝试从 upload_dir 查找
                    possible_path = os.path.join(upload_dir, source)
                    if os.path.exists(possible_path):
                        chunks = loader.load_document(possible_path)
                        metadatas = [{"source": source, "chunk_index": i, "file_path": possible_path} for i in range(len(chunks))]
                        self.add_documents(chunks, metadatas)
                        stats["reindexed_sources"] += 1
                        stats["total_chunks_after"] += len(chunks)
                    else:
                        stats["failed_sources"].append(source)
                        print(f"警告: 无法找到文件 {source}，跳过重新索引")
            except Exception as e:
                stats["failed_sources"].append(source)
                print(f"重新索引 {source} 时出错: {e}")
        
        return stats


# 全局知识库实例
rag_knowledge_base = RAGKnowledgeBase()

