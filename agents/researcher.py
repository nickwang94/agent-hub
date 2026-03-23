"""
研究 Agent / 知识库问答 Agent

基于知识库内容进行问答
"""
from typing import List, Optional
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from .base import BaseAgent
from core.llm import create_llm
from knowledge.store import KnowledgeStore


class ResearcherAgent(BaseAgent):
    """
    研究 Agent

    基于知识库内容进行问答，提供有依据的回答
    """

    DEFAULT_SYSTEM_PROMPT = """你是一个专业的研究助手。
请基于提供的知识库内容回答用户的问题。
- 如果知识库中有相关信息，请总结并回答
- 如果知识库中没有相关信息，请明确告知用户
- 引用知识库内容时，请保持准确性"""

    def __init__(
        self,
        name: str = "ResearcherAgent",
        description: str = "知识库问答助手",
        system_prompt: Optional[str] = None,
        knowledge_store: Optional[KnowledgeStore] = None,
        top_k: int = 5,
    ):
        """
        初始化研究 Agent

        Args:
            name: Agent 名称
            description: Agent 描述
            system_prompt: 系统提示词
            knowledge_store: 知识库存储
            top_k: 检索的文档数量
        """
        super().__init__(name, description)
        self.system_prompt = system_prompt or self.DEFAULT_SYSTEM_PROMPT
        self.llm = create_llm()
        self.knowledge_store = knowledge_store
        self.top_k = top_k

    def invoke(
        self, message: str, context: Optional[List[BaseMessage]] = None
    ) -> str:
        """
        处理知识库问答请求

        Args:
            message: 用户问题
            context: 对话历史上下文

        Returns:
            str: 回答
        """
        if not self.knowledge_store:
            return "错误：知识库未初始化"

        # 检索相关文档
        search_results = self.knowledge_store.search(
            query=message,
            n_results=self.top_k,
        )

        # 检查是否有相关结果
        if (
            not search_results["documents"]
            or not search_results["documents"][0]
        ):
            return "抱歉，知识库中没有找到与您的问题相关的信息。"

        # 构建上下文
        context_text = self._format_context(search_results)

        # 构建提示词
        prompt = f"""{self.system_prompt}

<知识库内容>
{context_text}
</知识库内容>

用户问题：{message}

请基于上述知识库内容回答问题："""

        # 调用 LLM
        response = self.llm.invoke([HumanMessage(content=prompt)])

        return response.content

    def _format_context(self, search_results: dict) -> str:
        """
        格式化检索结果为上下文

        Args:
            search_results: 搜索结果

        Returns:
            str: 格式化的上下文文本
        """
        documents = search_results["documents"][0]
        distances = search_results["distances"][0] if search_results.get("distances") else []

        formatted = []
        for i, (doc, dist) in enumerate(zip(documents, distances)):
            similarity = 1 - dist if dist else 0
            formatted.append(
                f"[文档 {i+1}] (相似度：{similarity:.2f})\n{doc}"
            )

        return "\n\n".join(formatted)

    def set_knowledge_store(self, store: KnowledgeStore):
        """设置知识库"""
        self.knowledge_store = store
