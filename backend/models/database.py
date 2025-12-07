"""数据库模型和操作"""
import json
import os
from typing import Dict, List, Optional
from datetime import datetime
import chromadb
from chromadb.config import Settings as ChromaSettings
from backend.config import settings
from backend.models.schemas import UserProgress, ProgressUpdate


class LearningProgressDB:
    """用户学习进度数据库"""
    
    def __init__(self):
        """初始化数据库"""
        self.client = chromadb.PersistentClient(
            path=settings.learning_progress_db_path,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name="user_learning_progress",
            metadata={"description": "用户学习进度存储"}
        )
    
    def get_user_progress(self, user_id: str) -> UserProgress:
        """获取用户学习进度"""
        results = self.collection.get(
            ids=[user_id],
            include=["metadatas", "documents"]
        )
        
        if not results["ids"]:
            # 新用户，返回默认进度
            return UserProgress(
                user_id=user_id,
                current_topic=None,
                mastery_level={},
                weak_points=[],
                mastered_topics=[],
                last_updated=datetime.now()
            )
        
        metadata = results["metadatas"][0]
        documents = results["documents"][0] if results["documents"] else "{}"
        
        # 解析存储的数据
        progress_data = json.loads(documents)
        
        return UserProgress(
            user_id=user_id,
            current_topic=metadata.get("current_topic"),
            mastery_level=progress_data.get("mastery_level", {}),
            weak_points=progress_data.get("weak_points", []),
            mastered_topics=progress_data.get("mastered_topics", []),
            last_updated=datetime.fromisoformat(metadata.get("last_updated", datetime.now().isoformat()))
        )
    
    def update_user_progress(self, user_id: str, update: ProgressUpdate):
        """更新用户学习进度"""
        progress = self.get_user_progress(user_id)
        
        # 更新掌握程度
        current_level = progress.mastery_level.get(update.topic, 0.0)
        if update.is_correct:
            # 答对了，提高掌握程度
            new_level = min(100.0, current_level + (100 - current_level) * 0.1)
            progress.mastery_level[update.topic] = new_level
            
            # 如果掌握程度超过 80，加入已掌握列表
            if new_level >= 80 and update.topic not in progress.mastered_topics:
                progress.mastered_topics.append(update.topic)
        else:
            # 答错了，降低掌握程度并记录错题
            new_level = max(0.0, current_level - 10.0)
            progress.mastery_level[update.topic] = new_level
            
            # 记录错题
            if update.question:
                error_record = f"{update.topic}: {update.question} | 正确答案: {update.answer}"
                if error_record not in progress.weak_points:
                    progress.weak_points.append(error_record)
        
        # 保存到数据库
        self._save_progress(progress)
    
    def set_current_topic(self, user_id: str, topic: str):
        """设置当前学习主题"""
        progress = self.get_user_progress(user_id)
        progress.current_topic = topic
        self._save_progress(progress)
    
    def _save_progress(self, progress: UserProgress):
        """保存进度到数据库"""
        progress.last_updated = datetime.now()
        
        # 准备存储数据
        progress_data = {
            "mastery_level": progress.mastery_level,
            "weak_points": progress.weak_points,
            "mastered_topics": progress.mastered_topics
        }
        
        self.collection.upsert(
            ids=[progress.user_id],
            documents=[json.dumps(progress_data, ensure_ascii=False)],
            metadatas=[{
                "current_topic": progress.current_topic or "",
                "last_updated": progress.last_updated.isoformat()
            }]
        )
    
    def get_all_topics(self, user_id: str) -> List[str]:
        """获取用户学习过的所有主题"""
        progress = self.get_user_progress(user_id)
        return list(progress.mastery_level.keys())


# 全局数据库实例
learning_progress_db = LearningProgressDB()

