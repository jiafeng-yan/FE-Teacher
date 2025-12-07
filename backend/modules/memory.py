"""记忆管理模块"""
from typing import List, Dict, Optional
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseMessage
from backend.models.database import learning_progress_db
from backend.models.schemas import UserProgress


class MemoryManager:
    """记忆管理器"""
    
    def __init__(self):
        """初始化记忆管理器"""
        # 存储每个用户的对话记忆
        self.conversation_memories: Dict[str, ConversationBufferMemory] = {}
    
    def get_conversation_memory(self, user_id: str, conversation_id: Optional[str] = None) -> ConversationBufferMemory:
        """
        获取用户的对话记忆（短期记忆）
        
        Args:
            user_id: 用户ID
            conversation_id: 对话ID（可选）
            
        Returns:
            对话记忆对象
        """
        memory_key = f"{user_id}_{conversation_id or 'default'}"
        
        if memory_key not in self.conversation_memories:
            self.conversation_memories[memory_key] = ConversationBufferMemory(
                return_messages=True,
                memory_key="chat_history"
            )
        
        return self.conversation_memories[memory_key]
    
    def get_user_progress(self, user_id: str) -> UserProgress:
        """
        获取用户学习进度（长期记忆）
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户学习进度
        """
        return learning_progress_db.get_user_progress(user_id)
    
    def update_progress(self, user_id: str, topic: str, score: float, is_correct: bool, 
                       question: Optional[str] = None, answer: Optional[str] = None):
        """
        更新用户学习进度
        
        Args:
            user_id: 用户ID
            topic: 知识点
            score: 得分
            is_correct: 是否正确
            question: 问题内容
            answer: 用户答案
        """
        from backend.models.schemas import ProgressUpdate
        
        update = ProgressUpdate(
            topic=topic,
            score=score,
            is_correct=is_correct,
            question=question,
            answer=answer
        )
        
        learning_progress_db.update_user_progress(user_id, update)
    
    def set_current_topic(self, user_id: str, topic: str):
        """
        设置当前学习主题
        
        Args:
            user_id: 用户ID
            topic: 主题
        """
        learning_progress_db.set_current_topic(user_id, topic)
    
    def get_learning_context(self, user_id: str) -> str:
        """
        获取学习上下文信息（用于提示词）
        
        Args:
            user_id: 用户ID
            
        Returns:
            上下文信息字符串
        """
        progress = self.get_user_progress(user_id)
        
        context = f"用户学习进度信息：\n"
        context += f"- 当前学习主题: {progress.current_topic or '未设置'}\n"
        
        if progress.mastery_level:
            context += f"- 已学习知识点: {', '.join(progress.mastery_level.keys())}\n"
            context += f"- 掌握程度: {', '.join([f'{k}({v:.1f}%)' for k, v in list(progress.mastery_level.items())[:5]])}\n"
        
        if progress.mastered_topics:
            context += f"- 已掌握知识点: {', '.join(progress.mastered_topics[:5])}\n"
        
        if progress.weak_points:
            context += f"- 需要加强的知识点: {len(progress.weak_points)} 个错题记录\n"
        
        return context


# 全局记忆管理器实例
memory_manager = MemoryManager()

