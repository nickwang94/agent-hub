"""
Researcher Agent / Knowledge Base Q&A Agent

Q&A based on knowledge base content
"""
from typing import List, Optional
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from .base import BaseAgent
from core.llm import create_llm
from knowledge.store import KnowledgeStore


class ResearcherAgent(BaseAgent):
    """
    Researcher Agent

    Q&A based on knowledge base content, provides evidence-based answers
    """

    DEFAULT_SYSTEM_PROMPT = """You are a professional research assistant.
Please answer user questions based on the provided knowledge base content.
- If there is relevant information in the knowledge base, please summarize and answer
- If there is no relevant information in the knowledge base, please inform the user
- When citing knowledge base content, please maintain accuracy"""

    def __init__(
        self,
        name: str = "ResearcherAgent",
        description: str = "Knowledge base Q&A assistant",
        system_prompt: Optional[str] = None,
        knowledge_store: Optional[KnowledgeStore] = None,
        top_k: int = 5,
    ):
        """
        Initialize researcher agent

        Args:
            name: Agent name
            description: Agent description
            system_prompt: System prompt
            knowledge_store: Knowledge storage
            top_k: Number of documents to retrieve
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
        Process knowledge base Q&A request

        Args:
            message: User question
            context: Conversation history context

        Returns:
            str: Answer
        """
        if not self.knowledge_store:
            return "Error: Knowledge base not initialized"

        # Retrieve relevant documents
        search_results = self.knowledge_store.search(
            query=message,
            n_results=self.top_k,
        )

        # Check if there are relevant results
        if (
            not search_results["documents"]
            or not search_results["documents"][0]
        ):
            return "Sorry, no information related to your question was found in the knowledge base."

        # Build context
        context_text = self._format_context(search_results)

        # Build prompt
        prompt = f"""{self.system_prompt}

<Knowledge Base Content>
{context_text}
</Knowledge Base Content>

User Question: {message}

Please answer the question based on the knowledge base content above:"""

        # Call LLM
        response = self.llm.invoke([HumanMessage(content=prompt)])

        return response.content

    def _format_context(self, search_results: dict) -> str:
        """
        Format search results as context

        Args:
            search_results: Search results

        Returns:
            str: Formatted context text
        """
        documents = search_results["documents"][0]
        distances = search_results["distances"][0] if search_results.get("distances") else []

        formatted = []
        for i, (doc, dist) in enumerate(zip(documents, distances)):
            similarity = 1 - dist if dist else 0
            formatted.append(
                f"[Document {i+1}] (Similarity: {similarity:.2f})\n{doc}"
            )

        return "\n\n".join(formatted)

    def set_knowledge_store(self, store: KnowledgeStore):
        """Set knowledge base"""
        self.knowledge_store = store
