"""工具模块"""
import httpx
from typing import List, Dict, Optional
from langchain.tools import Tool
from backend.config import settings


class WebSearchTool:
    """联网搜索工具（使用 Tavily）"""
    
    def __init__(self):
        """初始化搜索工具"""
        self.api_key = settings.tavily_api_key
        self.base_url = "https://api.tavily.com/search"
    
    def search(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        执行网络搜索
        
        Args:
            query: 搜索查询
            max_results: 最大结果数
            
        Returns:
            搜索结果列表
        """
        if not self.api_key:
            return [{"error": "Tavily API key 未配置"}]
        
        try:
            response = httpx.post(
                self.base_url,
                json={
                    "api_key": self.api_key,
                    "query": query,
                    "max_results": max_results,
                    "search_depth": "basic"
                },
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            
            results = []
            for result in data.get("results", []):
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content": result.get("content", ""),
                    "score": result.get("score", 0.0)
                })
            
            return results
        except Exception as e:
            print(f"搜索错误: {e}")
            return [{"error": f"搜索失败: {str(e)}"}]
    
    def format_results(self, results: List[Dict]) -> str:
        """格式化搜索结果"""
        if not results or "error" in results[0]:
            return "无法获取搜索结果，请检查网络连接或 API 配置。"
        
        formatted = "搜索结果：\n\n"
        for i, result in enumerate(results, 1):
            formatted += f"{i}. {result.get('title', '无标题')}\n"
            formatted += f"   链接: {result.get('url', '')}\n"
            formatted += f"   摘要: {result.get('content', '')[:200]}...\n\n"
        
        return formatted


class DrawingTool:
    """绘图工具（示例：可以扩展为调用图表生成 API）"""
    
    def generate_chart(self, chart_type: str, data: Dict) -> str:
        """
        生成图表描述（实际实现可以调用图表生成服务）
        
        Args:
            chart_type: 图表类型（line, bar, pie 等）
            data: 图表数据
            
        Returns:
            图表描述或 URL
        """
        # 这里是一个示例实现
        # 实际可以集成 matplotlib、plotly 等库或调用图表生成 API
        return f"已生成 {chart_type} 图表，数据: {data}"


# 创建工具实例
web_search_tool = WebSearchTool()
drawing_tool = DrawingTool()


def get_tools() -> List[Tool]:
    """
    获取所有可用工具
    
    Returns:
        工具列表
    """
    tools = [
        Tool(
            name="web_search",
            func=lambda q: web_search_tool.format_results(web_search_tool.search(q)),
            description="使用此工具搜索最新的金融经济新闻、案例和数据。输入应该是搜索查询。"
        ),
        Tool(
            name="draw_chart",
            func=lambda args: drawing_tool.generate_chart(**eval(args)),
            description="生成图表。输入应该是包含 chart_type 和 data 的字典字符串。"
        )
    ]
    
    return tools

