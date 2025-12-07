"""核心工作流模块"""
from typing import Dict, List, Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import initialize_agent, AgentType
from langchain.schema import AIMessage
from backend.config import settings
from backend.modules.planner import intent_planner
from backend.modules.rag import rag_knowledge_base
from backend.modules.memory import memory_manager
from backend.modules.tools import get_tools
from backend.models.schemas import ChatResponse, IntentResponse


class TeachingWorkflow:
    """教学智能体工作流"""
    
    def __init__(self):
        """初始化工作流"""
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY 未设置")
        
        # 构建主对话模型参数
        llm_kwargs = {
            "model": settings.openai_model,
            "temperature": 0.7,
            "openai_api_key": settings.openai_api_key
        }
        if settings.openai_base_url:
            llm_kwargs["base_url"] = settings.openai_base_url
        
        # 主对话模型
        self.llm = ChatOpenAI(**llm_kwargs)
        
        # 构建评分模型参数
        grading_kwargs = {
            "model": "gpt-3.5-turbo",
            "temperature": 0.3,
            "openai_api_key": settings.openai_api_key
        }
        if settings.openai_base_url:
            grading_kwargs["base_url"] = settings.openai_base_url
        
        # 评分模型（用于判卷）
        self.grading_llm = ChatOpenAI(**grading_kwargs)
        
        # 初始化 Agent（带工具）
        self.agent = initialize_agent(
            tools=get_tools(),
            llm=self.llm,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            verbose=True,
            memory=None  # 我们手动管理记忆
        )
    
    def process_message(self, user_id: str, message: str, conversation_id: Optional[str] = None) -> ChatResponse:
        """
        处理用户消息
        
        Args:
            user_id: 用户ID
            message: 用户消息
            conversation_id: 对话ID
            
        Returns:
            响应结果
        """
        # 1. 获取用户进度（长期记忆）
        user_progress = memory_manager.get_user_progress(user_id)
        progress_dict = {
            "current_topic": user_progress.current_topic,
            "mastery_level": user_progress.mastery_level,
            "mastered_topics": user_progress.mastered_topics
        }
        
        # 2. 意图识别
        intent_result = intent_planner.identify_intent(message, progress_dict)
        
        # 3. 根据意图处理
        if intent_result.intent == "learn":
            response = self._handle_learn_intent(user_id, message, intent_result, user_progress, conversation_id)
        elif intent_result.intent == "review":
            response = self._handle_review_intent(user_id, message, user_progress, conversation_id)
        elif intent_result.intent == "answer":
            response = self._handle_answer_intent(user_id, message, user_progress, conversation_id)
        else:  # chat
            response = self._handle_chat_intent(user_id, message, conversation_id)
        
        return response
    
    def _handle_learn_intent(self, user_id: str, message: str, intent: IntentResponse, 
                            user_progress, conversation_id: Optional[str]) -> ChatResponse:
        """处理学习意图"""
        # 1. 从知识库检索相关内容
        progress_dict = {
            "current_topic": user_progress.current_topic,
            "mastery_level": user_progress.mastery_level,
            "mastered_topics": user_progress.mastered_topics
        }
        knowledge = rag_knowledge_base.search(message, k=3, user_progress=progress_dict)
        
        # 2. 设置当前主题
        if intent.topic:
            memory_manager.set_current_topic(user_id, intent.topic)
        
        # 3. 构建教学提示词
        learning_context = memory_manager.get_learning_context(user_id)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一位苏格拉底式的金融经济导师。你的教学风格是：

1. **引导式提问**：不要直接给出答案，而是通过提问引导学生思考
2. **循序渐进**：根据学生的掌握程度调整讲解深度
3. **联系实际**：用生活中的例子解释抽象概念
4. **鼓励思考**：当学生回答正确时给予鼓励，错误时引导纠正             

当前学生信息：
{learning_context}

知识库内容：
{knowledge}

请基于以上信息，用引导式的方式帮助学生理解。如果学生是初学者，使用通俗易懂的语言；如果学生已有基础，可以深入讲解。如果知识库中有相关的信息，请额外引用原文。"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{user_input}")
        ])
        
        # 4. 获取对话历史
        memory = memory_manager.get_conversation_memory(user_id, conversation_id)
        chat_history = memory.chat_memory.messages
        
        # 5. 生成回复
        chain = prompt | self.llm
        response = chain.invoke({
            "learning_context": learning_context,
            "knowledge": "\n\n".join(knowledge),
            "chat_history": chat_history,
            "user_input": message
        })
        
        # 6. 保存对话
        memory.chat_memory.add_user_message(message)
        memory.chat_memory.add_ai_message(response.content)
        
        return ChatResponse(
            response=response.content,
            intent="learn",
            sources=[f"知识库: {len(knowledge)} 个相关片段"],
            conversation_id=conversation_id or f"{user_id}_default"
        )
    
    def _handle_review_intent(self, user_id: str, message: str, user_progress, 
                              conversation_id: Optional[str]) -> ChatResponse:
        """处理复习意图"""
        # 获取用户已学知识点
        topics = list(user_progress.mastery_level.keys())
        
        if not topics:
            response_text = "你还没有学习任何知识点。让我们开始学习吧！你想了解哪个金融经济概念？"
        else:
            # 从知识库检索复习内容
            review_query = f"复习 {' '.join(topics[:3])}"
            knowledge = rag_knowledge_base.search(review_query, k=3)
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", """你是一位金融经济导师，正在帮助学生复习。

学生已学知识点：
{topics}

掌握程度：
{mastery_levels}

错题记录：
{weak_points}

请帮助学生复习这些内容，重点关注掌握程度较低的知识点。"""),
                ("human", "{user_input}")
            ])
            
            chain = prompt | self.llm
            response = chain.invoke({
                "topics": ", ".join(topics),
                "mastery_levels": str(user_progress.mastery_level),
                "weak_points": "\n".join(user_progress.weak_points[-5:]) if user_progress.weak_points else "无",
                "user_input": message
            })
            response_text = response.content
        
        memory = memory_manager.get_conversation_memory(user_id, conversation_id)
        memory.chat_memory.add_user_message(message)
        memory.chat_memory.add_ai_message(response_text)
        
        return ChatResponse(
            response=response_text,
            intent="review",
            sources=None,
            conversation_id=conversation_id or f"{user_id}_default"
        )
    
    def _handle_answer_intent(self, user_id: str, message: str, user_progress, 
                              conversation_id: Optional[str]) -> ChatResponse:
        """处理答题意图"""
        # 获取当前主题
        current_topic = user_progress.current_topic or "未知主题"
        
        # 使用 LLM 判卷
        grading_prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一位严格的判卷老师。请评估学生的答案。

当前主题：{topic}

请返回 JSON 格式：
{{
    "score": 0-100,
    "is_correct": true/false,
    "feedback": "评语",
    "correct_answer": "正确答案"
}}"""),
            ("human", "学生答案：{answer}")
        ])
        
        # 获取对话历史以了解问题
        memory = memory_manager.get_conversation_memory(user_id, conversation_id)
        chat_history = memory.chat_memory.messages
        
        # 尝试从历史中提取问题
        question = "未知问题"
        if chat_history:
            for msg in reversed(chat_history):
                if isinstance(msg, AIMessage) and "?" in msg.content:
                    question = msg.content[:200]
                    break
        
        chain = grading_prompt | self.grading_llm
        grading_response = chain.invoke({
            "topic": current_topic,
            "answer": message
        })
        
        # 解析评分结果
        import json
        try:
            content = grading_response.content
            if "{" in content:
                json_start = content.find("{")
                json_end = content.rfind("}") + 1
                json_str = content[json_start:json_end]
                grading_result = json.loads(json_str)
            else:
                grading_result = {"score": 50, "is_correct": False, "feedback": "无法评估", "correct_answer": ""}
        except:
            grading_result = {"score": 50, "is_correct": False, "feedback": "无法评估", "correct_answer": ""}
        
        score = float(grading_result.get("score", 50))
        is_correct = grading_result.get("is_correct", score >= 60)
        feedback = grading_result.get("feedback", "请继续努力")
        correct_answer = grading_result.get("correct_answer", "")
        
        # 更新学习进度
        memory_manager.update_progress(
            user_id=user_id,
            topic=current_topic,
            score=score,
            is_correct=is_correct,
            question=question,
            answer=message
        )
        
        # 生成反馈回复
        if score < 60:
            # 触发补习模式
            knowledge = rag_knowledge_base.search(f"{current_topic} 基础概念", k=2)
            response_text = f"""评分：{score:.1f} 分

{feedback}

正确答案：{correct_answer}

看起来你对这个知识点还需要加强。让我为你补充一些基础知识：

{chr(10).join(knowledge[:2])}

让我们再试一次，或者你想继续学习其他内容？"""
        else:
            response_text = f"""很好！评分：{score:.1f} 分

{feedback}

{"你已经掌握了这个知识点！" if is_correct else "继续加油，你正在进步！"}"""
        
        memory.chat_memory.add_user_message(message)
        memory.chat_memory.add_ai_message(response_text)
        
        return ChatResponse(
            response=response_text,
            intent="answer",
            sources=None,
            conversation_id=conversation_id or f"{user_id}_default"
        )
    
    def _handle_chat_intent(self, user_id: str, message: str, conversation_id: Optional[str]) -> ChatResponse:
        """处理闲聊意图"""
        # 使用工具（如联网搜索）获取最新信息
        tools = get_tools()
        web_search = tools[0]  # web_search 工具
        
        # 判断是否需要搜索
        search_keywords = ["最新", "新闻", "最近", "现在", "当前"]
        need_search = any(keyword in message for keyword in search_keywords)
        
        if need_search:
            search_query = f"金融经济 {message}"
            search_results = web_search.func(search_query)
        else:
            search_results = None
        
        # 构建回复
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一位友好的金融经济教学助手。你可以：
1. 回答金融经济相关问题
2. 进行友好的对话
3. 如果涉及最新信息，可以使用搜索结果

{search_results}"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{user_input}")
        ])
        
        memory = memory_manager.get_conversation_memory(user_id, conversation_id)
        chat_history = memory.chat_memory.messages
        
        chain = prompt | self.llm
        response = chain.invoke({
            "search_results": search_results or "",
            "chat_history": chat_history,
            "user_input": message
        })
        
        memory.chat_memory.add_user_message(message)
        memory.chat_memory.add_ai_message(response.content)
        
        return ChatResponse(
            response=response.content,
            intent="chat",
            sources=["联网搜索"] if need_search else None,
            conversation_id=conversation_id or f"{user_id}_default"
        )


# 全局工作流实例
teaching_workflow = TeachingWorkflow()

