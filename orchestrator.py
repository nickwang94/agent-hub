"""
多 Agent 编排器

使用 LangGraph 构建状态机，协调多个 Agent 协作
"""
from typing import TypedDict, Literal, Annotated
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import operator

from agents.chat import ChatAgent
from agents.researcher import ResearcherAgent
from session.manager import SessionManager, Session


# ============ 定义状态 ============

class AgentState(TypedDict):
    """
    Agent 状态定义

    LangGraph 使用状态来在节点之间传递信息
    """
    messages: Annotated[list[BaseMessage], operator.add]
    # 当前选中的 agent
    current_agent: str
    # 用户输入
    user_input: str
    # 最终响应
    response: str


# ============ 定义路由逻辑 ============

class AgentOrchestrator:
    """
    Agent 编排器

    使用 LangGraph 管理多 Agent 协作流程
    """

    # Agent 类型
    CHAT_AGENT = "chat"
    RESEARCHER_AGENT = "researcher"

    def __init__(
        self,
        chat_agent: ChatAgent = None,
        researcher_agent: ResearcherAgent = None,
        session_manager: SessionManager = None,
    ):
        """
        初始化编排器

        Args:
            chat_agent: 对话 Agent
            researcher_agent: 研究 Agent
            session_manager: 会话管理器
        """
        self.chat_agent = chat_agent or ChatAgent()
        self.researcher_agent = researcher_agent or ResearcherAgent()
        self.session_manager = session_manager or SessionManager()

        # 构建状态图
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """
        构建状态图

        Returns:
            StateGraph: 编译好的状态图
        """
        # 创建状态图
        workflow = StateGraph(AgentState)

        # 添加节点
        workflow.add_node("router", self._router_node)
        workflow.add_node("chat", self._chat_node)
        workflow.add_node("researcher", self._researcher_node)

        # 设置入口
        workflow.add_edge(START, "router")

        # 添加条件边（路由）
        workflow.add_conditional_edges(
            "router",
            self._route_agent,
            {
                self.CHAT_AGENT: "chat",
                self.RESEARCHER_AGENT: "researcher",
            },
        )

        # 完成处理后结束
        workflow.add_edge("chat", END)
        workflow.add_edge("researcher", END)

        # 编译图
        return workflow.compile()

    def _router_node(self, state: AgentState) -> AgentState:
        """
        路由节点

        分析用户输入，决定使用哪个 Agent
        """
        # 简单的路由逻辑：可以根据关键词判断
        user_input = state["user_input"].lower()

        # 如果问题包含研究/知识/文档相关词汇，使用 Researcher Agent
        research_keywords = [
            "查询", "搜索", "知识库", "文档", "研究",
            "find", "search", "knowledge", "document", "research",
        ]

        if any(keyword in user_input for keyword in research_keywords):
            state["current_agent"] = self.RESEARCHER_AGENT
        else:
            state["current_agent"] = self.CHAT_AGENT

        return state

    def _route_agent(self, state: AgentState) -> Literal["chat", "researcher"]:
        """路由决策"""
        return state["current_agent"]

    def _chat_node(self, state: AgentState) -> AgentState:
        """
        对话节点

        使用 Chat Agent 处理请求
        """
        response = self.chat_agent.invoke(
            message=state["user_input"],
            context=state["messages"],
        )

        state["response"] = response
        state["messages"].append(HumanMessage(content=state["user_input"]))
        state["messages"].append(AIMessage(content=response))

        return state

    def _researcher_node(self, state: AgentState) -> AgentState:
        """
        研究节点

        使用 Researcher Agent 处理请求
        """
        response = self.researcher_agent.invoke(
            message=state["user_input"],
            context=state["messages"],
        )

        state["response"] = response
        state["messages"].append(HumanMessage(content=state["user_input"]))
        state["messages"].append(AIMessage(content=response))

        return state

    def process_message(
        self,
        message: str,
        session_id: Optional[str] = None,
    ) -> tuple[str, str]:
        """
        处理用户消息

        Args:
            message: 用户输入
            session_id: 会话 ID

        Returns:
            tuple[str, str]: (响应内容，使用的 Agent 名称)
        """
        # 获取或创建会话
        session = self.session_manager.get_or_create_session(session_id)

        # 初始状态
        initial_state = AgentState(
            messages=session.get_messages(),
            current_agent="",
            user_input=message,
            response="",
        )

        # 运行状态图
        final_state = self.graph.invoke(initial_state)

        # 更新会话
        session.add_message("user", message)
        session.add_message("assistant", final_state["response"])

        return final_state["response"], final_state["current_agent"]

    def get_agent_info(self) -> dict:
        """获取所有 Agent 信息"""
        return {
            self.CHAT_AGENT: self.chat_agent.get_state(),
            self.RESEARCHER_AGENT: self.researcher_agent.get_state(),
        }
