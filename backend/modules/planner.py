"""意图识别模块（Planner/Router）"""
from typing import Dict
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from backend.config import settings
from backend.models.schemas import IntentResponse


class IntentPlanner:
    """意图识别器"""
    
    def __init__(self):
        """初始化意图识别器"""
        # 优先使用意图识别模型的独立配置，如果没有则使用 OpenAI 配置
        api_key = settings.intent_model_api_key or settings.openai_api_key
        model_name = settings.intent_model_name
        base_url = settings.intent_model_base_url or settings.openai_base_url
        
        if not api_key:
            raise ValueError("意图识别模型 API Key 未设置，请设置 INTENT_MODEL_API_KEY 或 OPENAI_API_KEY")
        
        # 构建 LLM 参数
        llm_kwargs = {
            "model": model_name,
            "temperature": 0.3,
            "openai_api_key": api_key
        }
        
        # 如果配置了 base_url，添加到参数中
        if base_url:
            llm_kwargs["base_url"] = base_url
        
        # 使用配置的模型进行意图识别
        self.llm = ChatOpenAI(**llm_kwargs)
        
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", """你是一个意图识别助手。根据用户的输入，判断用户的意图。

可能的意图类型：
1. learn - 用户想学习新知识（如："什么是GDP？"、"给我讲讲货币政策"）
2. review - 用户想复习已学内容（如："帮我复习一下"、"我之前学的什么？"）
3. answer - 用户正在回答问题（如："答案是A"、"我认为是..."）
4. chat - 闲聊或其他（如："你好"、"今天天气怎么样？"、"最近国际经济形势怎么样？"）

请只返回JSON格式：
{{
    "intent": "learn|review|answer|chat",
    "confidence": 0.0-1.0,
    "topic": "相关主题（如果有）"
}}"""),
            ("human", "{user_input}")
        ])
    
    def identify_intent(self, user_input: str, user_progress: Dict = None) -> IntentResponse:
        """
        识别用户意图
        
        Args:
            user_input: 用户输入
            user_progress: 用户学习进度（可选）
            
        Returns:
            意图识别结果
        """
        # 如果有用户进度信息，添加到提示中
        context = f"用户输入: {user_input}"
        if user_progress:
            context += f"\n当前学习主题: {user_progress.get('current_topic', '无')}"
        
        chain = self.prompt_template | self.llm
        
        try:
            response = chain.invoke({"user_input": context})
            content = response.content.strip()
            
            # 解析 JSON 响应
            import json
            # 尝试提取 JSON
            if "{" in content and "}" in content:
                json_start = content.find("{")
                json_end = content.rfind("}") + 1
                json_str = content[json_start:json_end]
                result = json.loads(json_str)
            else:
                # 如果无法解析，使用默认值
                result = {"intent": "chat", "confidence": 0.5, "topic": None}
            
            return IntentResponse(
                intent=result.get("intent", "chat"),
                confidence=float(result.get("confidence", 0.5)),
                topic=result.get("topic")
            )
        except Exception as e:
            # 错误处理：返回默认意图
            print(f"意图识别错误: {e}")
            return IntentResponse(
                intent="chat",
                confidence=0.5,
                topic=None
            )


# 全局意图识别器实例
intent_planner = IntentPlanner()

